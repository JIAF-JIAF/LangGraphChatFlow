"""
技能模块

提供技能的加载、匹配、执行和工具注册能力。

架构：
- loader: 使用 pydantic_ai_skills.SkillsToolset 加载 SKILL.md
- matcher: 关键词 + 语义匹配
- executor: 脚本安全执行（subprocess + 超时控制）
- tools: LangChain Tool 定义（skill_list, skill_instructions, skill_reference, skill_run_script）
- manager: 统一对外入口，组合以上组件

注意：技能安装功能已移至 api/skill_installer.py
"""

from .manager import SkillManager
from .loader import SkillLoader
from .matcher import SkillMatcher
from .executor import SkillExecutor
from .tools import SkillTools
from .models import SkillInfo

__all__ = [
    "SkillManager",
    "SkillLoader",
    "SkillMatcher",
    "SkillExecutor",
    "SkillTools",
    "SkillInfo",
]
