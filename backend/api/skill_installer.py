"""
Skill 安装器

使用业界成熟方案：
- pydantic-ai-skills.SkillsToolset: 技能加载和管理
- requests: GitHub API 调用
"""

import os
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
from pydantic_ai_skills import SkillsToolset

from modules.logger import log


@dataclass
class InstallResult:
    """安装结果"""
    success: bool
    message: str
    skill_name: str = ""
    version: str = ""
    installed_path: str = ""


class SkillInstaller:
    """
    Skill 安装器
    
    使用业界成熟方案：
    - pydantic-ai-skills.SkillsToolset: 加载和管理技能
    - GitHub API: 下载技能包
    """

    def __init__(self, skills_dir: str = None, token: str = None):
        if skills_dir is None:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            skills_dir = os.path.join(backend_dir, "skills")
        
        self.skills_dir = Path(skills_dir)
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"token {token}"
        self.session.headers["Accept"] = "application/vnd.github.v3+json"
        self._ensure_skills_dir()
        
        self._toolset = SkillsToolset(directories=[str(self.skills_dir)], validate=False)
        log(f"安装器初始化完成，目录: {self.skills_dir}", module="Skill.Installer")

    def _ensure_skills_dir(self):
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def install_from_url(self, url: str) -> InstallResult:
        """
        从 GitHub URL 安装 Skill

        Args:
            url: GitHub 仓库 URL

        Returns:
            InstallResult: 安装结果
        """
        log(f"从 URL 安装技能: {url}", module="Skill.Installer")
        try:
            location = self._parse_github_url(url)
            if not location:
                return InstallResult(success=False, message=f"无效的 GitHub URL: {url}")
            return self._install(location)
        except Exception as e:
            log(f"安装失败: {e}", module="Skill.Installer")
            return InstallResult(success=False, message=str(e))

    def _parse_github_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        解析 GitHub URL

        支持格式：
        - https://github.com/user/repo
        - https://github.com/user/repo/tree/branch/path
        """
        url = url.strip()
        parsed = urlparse(url)
        
        if parsed.netloc != "github.com":
            return None
        
        parts = parsed.path.strip("/").split("/")
        if len(parts) < 2:
            return None
        
        user = parts[0]
        repo = parts[1].replace(".git", "")
        branch = "main"
        path = ""
        
        if len(parts) >= 4 and parts[2] in ("tree", "blob"):
            branch = parts[3]
            path = "/".join(parts[4:]) if len(parts) > 4 else ""
        
        return {"user": user, "repo": repo, "branch": branch, "path": path}

    def _install(self, location: Dict[str, str]) -> InstallResult:
        """执行安装"""
        user = location["user"]
        repo = location["repo"]
        branch = location["branch"]
        path = location["path"]
        
        skill_name = os.path.basename(path) if path else repo.replace("-skill", "")
        
        target_dir = self.skills_dir / skill_name
        if target_dir.exists():
            return InstallResult(
                success=False,
                message=f"技能 {skill_name} 已存在",
                skill_name=skill_name
            )

        try:
            zip_url = f"https://api.github.com/repos/{user}/{repo}/zipball/{branch}"
            log(f"下载: {zip_url}", module="Skill.Installer")
            
            response = self.session.get(zip_url, timeout=60)
            if response.status_code != 200:
                return InstallResult(
                    success=False,
                    message=f"下载失败: HTTP {response.status_code}"
                )

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name

            with zipfile.ZipFile(tmp_path, 'r') as zf:
                members = zf.namelist()
                if not members:
                    return InstallResult(success=False, message="压缩包为空")
                
                root_dir = members[0].split('/')[0]
                
                if path:
                    prefix = f"{root_dir}/{path}/"
                    relevant_members = [m for m in members if m.startswith(prefix)]
                else:
                    relevant_members = [m for m in members if m.startswith(root_dir + "/")]
                
                target_dir.mkdir(parents=True, exist_ok=True)
                
                for member in relevant_members:
                    if path:
                        relative = member[len(prefix):]
                    else:
                        relative = member[len(root_dir) + 1:]
                    
                    if not relative:
                        continue
                    
                    target_path = target_dir / relative
                    
                    if member.endswith('/'):
                        target_path.mkdir(parents=True, exist_ok=True)
                    else:
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(member) as src, open(target_path, 'wb') as dst:
                            dst.write(src.read())

            os.unlink(tmp_path)
            
            self._toolset.reload()
            
            log(f"技能安装成功: {skill_name}", module="Skill.Installer")
            return InstallResult(
                success=True,
                message=f"技能 {skill_name} 安装成功",
                skill_name=skill_name,
                installed_path=str(target_dir)
            )

        except Exception as e:
            log(f"安装异常: {e}", module="Skill.Installer")
            return InstallResult(
                success=False,
                message=f"安装失败: {str(e)}",
                skill_name=skill_name
            )

    def uninstall(self, skill_name: str) -> InstallResult:
        """
        卸载技能

        Args:
            skill_name: 技能名称

        Returns:
            InstallResult: 卸载结果
        """
        log(f"卸载技能: {skill_name}", module="Skill.Installer")
        target_dir = self.skills_dir / skill_name
        
        if not target_dir.exists():
            return InstallResult(
                success=False,
                message=f"技能 {skill_name} 不存在",
                skill_name=skill_name
            )

        try:
            shutil.rmtree(target_dir)
            self._toolset.reload()
            log(f"技能卸载成功: {skill_name}", module="Skill.Installer")
            return InstallResult(
                success=True,
                message=f"技能 {skill_name} 卸载成功",
                skill_name=skill_name
            )
        except Exception as e:
            log(f"卸载失败: {e}", module="Skill.Installer")
            return InstallResult(
                success=False,
                message=f"卸载失败: {str(e)}",
                skill_name=skill_name
            )

    def list_installed(self) -> List[str]:
        """
        获取已安装的技能列表

        使用 SkillsToolset.skills 属性

        Returns:
            List[str]: 技能名称列表
        """
        skills = list(self._toolset.skills.keys())
        log(f"已安装技能: {len(skills)} 个", module="Skill.Installer")
        return skills

    def get_skill_info(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        获取技能信息

        使用 SkillsToolset.get_skill() 方法

        Args:
            skill_name: 技能名称

        Returns:
            Optional[Dict[str, Any]]: 技能信息
        """
        try:
            skill = self._toolset.get_skill(skill_name)
            
            return {
                "name": skill.name,
                "description": skill.description,
                "version": skill.metadata.get("version", "1.0.0") if skill.metadata else "1.0.0",
                "path": skill.uri or "",
                "content": skill.content[:500] + "..." if len(skill.content) > 500 else skill.content,
                "metadata": skill.metadata or {}
            }
        except KeyError:
            log(f"技能不存在: {skill_name}", module="Skill.Installer")
            return None
        except Exception as e:
            log(f"获取技能信息失败: {e}", module="Skill.Installer")
            return None

    def reload(self) -> None:
        """重新加载技能"""
        self._toolset.reload()
        log("技能已重新加载", module="Skill.Installer")


_installer: Optional[SkillInstaller] = None


def get_installer(skills_dir: str = None, token: str = None) -> SkillInstaller:
    """
    获取 SkillInstaller 单例

    Args:
        skills_dir: 技能目录路径（可选）
        token: GitHub 访问令牌（可选）

    Returns:
        SkillInstaller: SkillInstaller 实例
    """
    global _installer
    if _installer is None:
        _installer = SkillInstaller(skills_dir=skills_dir, token=token)
    return _installer
