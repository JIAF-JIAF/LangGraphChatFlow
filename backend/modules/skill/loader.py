"""
技能加载层
负责技能文件的加载和解析

使用 pydantic_ai_skills.SkillsToolset 实现标准化的技能加载
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic_ai_skills import SkillsToolset
from modules.logger import log


class SkillLoader:
    """
    技能加载器
    负责从技能目录加载和解析 SKILL.md 文件

    使用延迟加载策略：
    - 启动时只加载元数据
    - 需要时才加载完整技能内容
    """

    def __init__(self, skills_dir: str | Path = "skills"):
        """
        初始化技能加载器

        Args:
            skills_dir: 技能目录路径
        """
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        skills_path = Path(skills_dir)
        if not skills_path.is_absolute():
            skills_path = Path(os.path.join(backend_dir, str(skills_dir)))

        self.skills_dir = skills_path
        self._toolset = SkillsToolset(directories=[str(self.skills_dir)])
        self._skills_cache: Dict[str, Dict[str, Any]] = {}

        self.skills_dir.mkdir(parents=True, exist_ok=True)
        log(f"加载器初始化完成，目录: {self.skills_dir}", module="Skill.Loader")

    def list_skills(self) -> List[Dict[str, Any]]:
        """
        获取所有技能元数据列表

        Returns:
            List[Dict[str, Any]]: 技能元数据列表
        """
        log("开始加载技能列表", module="Skill.Loader")
        skills = self._toolset.skills.values()
        result = [
            {
                "name": s.name,
                "description": s.description,
                "version": getattr(s, 'version', '1.0.0'),
                "metadata": getattr(s, 'metadata', {})
            }
            for s in skills
        ]
        log(f"加载完成，共 {len(result)} 个技能", module="Skill.Loader")
        return result

    def load_skill(self, name: str) -> Optional[Dict[str, Any]]:
        """
        加载完整技能内容（按需加载）

        Args:
            name: 技能名称

        Returns:
            Optional[Dict[str, Any]]: 技能完整信息，如果不存在返回 None
        """
        if name in self._skills_cache:
            log(f"从缓存加载技能: {name}", module="Skill.Loader")
            return self._skills_cache[name]

        log(f"加载技能: {name}", module="Skill.Loader")
        skill = self._toolset.get_skill(name)

        if skill:
            instructions = getattr(skill, 'instructions', None) or getattr(skill, 'content', '')

            skill_data = {
                "name": skill.name,
                "description": skill.description,
                "version": getattr(skill, 'version', '1.0.0'),
                "instructions": instructions,
                "content": getattr(skill, 'content', ''),
                "metadata": getattr(skill, 'metadata', {}),
                "resources": getattr(skill, 'resources', []),
                "scripts": getattr(skill, 'scripts', []),
                "uri": getattr(skill, 'uri', None)
            }
            self._skills_cache[name] = skill_data
            log(f"技能加载成功: {name}", module="Skill.Loader")
            return skill_data

        log(f"技能不存在: {name}", module="Skill.Loader")
        return None

    def get_skill_path(self, name: str) -> Optional[Path]:
        """
        获取技能目录路径

        Args:
            name: 技能名称

        Returns:
            Optional[Path]: 技能目录路径，如果不存在返回 None
        """
        skill_path = self.skills_dir / name
        return skill_path if skill_path.exists() else None

    def get_reference(self, skill_name: str, ref_path: str) -> Optional[str]:
        """
        获取技能引用文件内容

        Args:
            skill_name: 技能名称
            ref_path: 引用文件路径

        Returns:
            Optional[str]: 文件内容，如果不存在返回 None
        """
        log(f"读取参考文档: {skill_name}/{ref_path}", module="Skill.Loader")
        skill_dir = self.skills_dir / skill_name
        ref_file = skill_dir / ref_path
        if not ref_file.exists():
            ref_file = skill_dir / "references" / os.path.basename(ref_path)
        if ref_file.exists():
            return ref_file.read_text(encoding="utf-8")
        log(f"参考文档不存在: {ref_path}", module="Skill.Loader")
        return None

    def clear_cache(self) -> None:
        """清除技能缓存"""
        self._skills_cache.clear()
        log("缓存已清除", module="Skill.Loader")

    def reload(self) -> None:
        """重新初始化加载器"""
        self._toolset = SkillsToolset(directories=[str(self.skills_dir)])
        self._skills_cache.clear()
        log("加载器已重新初始化", module="Skill.Loader")
