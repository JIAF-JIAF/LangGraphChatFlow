"""
Skill 管理器

作为技能模块的统一对外入口，组合 loader、matcher、executor、tools。
核心方法 get_tools() 返回 LangChain Tool 列表，供 LangChain Agent 使用。

架构说明：
- LangGraph（调度层）：不包含技能相关节点
- LangChain Agent（执行层）：通过 tool calling 自主调用技能工具
- Skill 模块（内部）：提供工具定义和底层实现
"""

from typing import Any, Dict, List, Optional

from langchain_core.tools import BaseTool

from .executor import SkillExecutor
from .loader import SkillLoader
from .matcher import SkillMatcher
from .tools import SkillTools
from modules.logger import log


class SkillManager:
    """
    Skill 管理器

    薄层组合 loader、matcher、executor、tools，
    对外提供 get_tools() 方法返回 LangChain Tool 列表。
    """

    def __init__(self, skills_dir: str = "skills", llm_client: Any = None):
        """
        初始化 Skill 管理器

        Args:
            skills_dir: 技能目录路径（默认 "skills"）
            llm_client: LLM 客户端（保留兼容，当前未使用）
        """
        self._loader = SkillLoader(skills_dir=skills_dir)
        self._matcher = SkillMatcher(loader=self._loader)
        self._executor = SkillExecutor(loader=self._loader)
        self._tools = SkillTools(
            loader=self._loader,
            matcher=self._matcher,
            executor=self._executor,
        )
        log("管理器初始化完成", module="Skill.Manager")

    def get_tools(self) -> List[BaseTool]:
        """
        返回 LangChain Tool 列表

        Returns:
            List[BaseTool]: 技能工具列表（skill_list, skill_instructions, skill_reference, skill_run_script）
        """
        return self._tools.get_tools()

    def list_skills(self) -> List[Dict[str, Any]]:
        """
        获取所有技能列表

        Returns:
            List[Dict[str, Any]]: 技能列表
        """
        return self._loader.list_skills()

    def load_skill(self, name: str) -> Optional[Dict[str, Any]]:
        """
        加载指定技能

        Args:
            name: 技能名称

        Returns:
            Optional[Dict[str, Any]]: 技能详情，如果不存在返回 None
        """
        return self._loader.load_skill(name)

    def reload(self) -> None:
        """重新加载技能"""
        self._loader.reload()
        log("管理器已重新加载", module="Skill.Manager")
