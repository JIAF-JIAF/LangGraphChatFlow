"""
技能脚本执行层

负责技能脚本的执行，提供安全的脚本运行能力：
- 工作目录隔离：每个技能在独立目录中执行
- 超时控制：防止脚本无限运行
- 安全限制：仅允许 .py 和 .sh 脚本执行
- 结果标准化：统一返回格式

注意：LLM 驱动的技能执行已移除，由 LangChain Agent 通过
skill_instructions 工具获取指令后自主执行，避免污染主流程。
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from .loader import SkillLoader
from modules.logger import log


_ALLOWED_EXTENSIONS = {".py", ".sh"}


class SkillExecutor:
    """
    技能脚本执行器

    专注于脚本的安全执行，提供工作目录隔离和超时控制。
    LLM 驱动的技能执行由 LangChain Agent 通过 tool calling 自主完成，
    不再经过此执行器。
    """

    def __init__(self, loader: SkillLoader):
        """
        初始化技能脚本执行器

        Args:
            loader: 技能加载器实例
        """
        self._loader = loader
        self._default_timeout = 30
        log("执行器初始化完成", module="Skill.Executor")

    def run_script(
        self,
        skill_name: str,
        script_path: str,
        args: Optional[List[str]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """
        执行技能脚本

        Args:
            skill_name: 技能名称
            script_path: 脚本路径（相对于技能目录，如 scripts/process.py）
            args: 脚本参数
            timeout: 超时时间（秒）

        Returns:
            Dict[str, Any]: 执行结果，包含 success, output, error 等字段
        """
        log(f"执行脚本: {skill_name}/{script_path}", module="Skill.Executor")
        skill_dir = self._loader.get_skill_path(skill_name)
        if not skill_dir:
            log(f"技能不存在: {skill_name}", module="Skill.Executor")
            return {
                "success": False,
                "error": f"技能不存在: {skill_name}",
                "output": "",
            }

        full_path = skill_dir / script_path
        if not full_path.exists():
            log(f"脚本文件不存在: {script_path}", module="Skill.Executor")
            return {
                "success": False,
                "error": f"脚本文件不存在: {script_path}",
                "output": "",
            }

        ext = full_path.suffix.lower()
        if ext not in _ALLOWED_EXTENSIONS:
            log(f"不支持的脚本类型: {ext}", module="Skill.Executor")
            return {
                "success": False,
                "error": f"不支持的脚本类型: {ext}，仅支持 {', '.join(_ALLOWED_EXTENSIONS)}",
                "output": "",
            }

        try:
            cmd = self._build_command(full_path, ext, args or [])
            log(f"执行命令: {' '.join(cmd)}", module="Skill.Executor")
            result = subprocess.run(
                cmd,
                cwd=str(skill_dir),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout,
            )

            if result.returncode == 0:
                log(f"脚本执行成功", module="Skill.Executor")
            else:
                log(f"脚本执行失败，退出码: {result.returncode}", module="Skill.Executor")

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error": result.stderr if result.returncode != 0 else "",
                "exit_code": result.returncode,
            }

        except subprocess.TimeoutExpired:
            log(f"脚本执行超时（{timeout}秒）", module="Skill.Executor")
            return {
                "success": False,
                "error": f"脚本执行超时（{timeout}秒）",
                "output": "",
            }
        except Exception as e:
            log(f"脚本执行异常: {str(e)}", module="Skill.Executor")
            return {
                "success": False,
                "error": str(e),
                "output": "",
            }

    def _build_command(self, script_path: Path, ext: str, args: List[str]) -> List[str]:
        """
        构建执行命令

        Args:
            script_path: 脚本完整路径
            ext: 脚本扩展名
            args: 脚本参数

        Returns:
            List[str]: 执行命令
        """
        if ext == ".py":
            return ["python", str(script_path)] + args
        elif ext == ".sh":
            return ["bash", str(script_path)] + args
        return [str(script_path)] + args
