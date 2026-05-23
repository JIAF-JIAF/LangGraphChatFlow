"""
技能工具包

自动导入所有工具模块，触发注册机制
"""

from typing import List

from langchain_core.tools import BaseTool

from ..executor import SkillExecutor
from ..loader import SkillLoader
from ..matcher import SkillMatcher
from .factory import SkillToolFactory
from modules.logger import log

from .skill_list import build_skill_list_tool
from .skill_instructions import build_skill_instructions_tool
from .skill_reference import build_skill_reference_tool
from .skill_save_file import build_skill_save_file_tool
from .skill_run_script import build_skill_run_script_tool


class SkillTools:
    """
    技能工具集

    将技能操作封装为 LangChain Tool 实例，
    供 LangChain Agent 通过 tool calling 自主调用。

    遵循 Agent Skills 开放标准的渐进式披露模式：
    1. skill_list — 发现技能（元数据层）
    2. skill_instructions — 加载指令（指令层）
    3. skill_reference — 读取参考文档（资源层）
    4. skill_save_file — 保存生成内容（输出层）
    5. skill_run_script — 执行脚本（执行层）
    """

    def __init__(self, loader: SkillLoader, matcher: SkillMatcher, executor: SkillExecutor):
        SkillToolFactory.set_dependencies(loader, matcher, executor)
        log("工具集初始化完成", module="Skill.Tools")

    def build(self) -> List[BaseTool]:
        """
        构建所有已注册的工具实例

        Returns:
            List[BaseTool]: 技能工具列表
        """
        return SkillToolFactory.build()

    get_tools = build


__all__ = [
    'SkillTools',
    'SkillToolFactory',
    'build_skill_list_tool',
    'build_skill_instructions_tool',
    'build_skill_reference_tool',
    'build_skill_save_file_tool',
    'build_skill_run_script_tool',
]
