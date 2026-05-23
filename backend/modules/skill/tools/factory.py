"""
技能工具工厂类

管理所有可用的技能工具实现，支持注册和构建。

核心功能：
- 注册工具构建函数
- 构建所有工具实例
- 获取支持的工具列表
"""

from typing import Dict, List, Callable, Any
from langchain_core.tools import BaseTool


class SkillToolFactory:
    """
    技能工具工厂类
    
    管理所有可用的技能工具实现，新的工具通过 SkillToolFactory.register() 注册。
    """

    _tools: Dict[str, Callable] = {}
    _dependencies: Dict[str, Any] = {}

    @classmethod
    def set_dependencies(cls, loader, matcher, executor):
        """
        设置工具依赖
        
        Args:
            loader: 技能加载器
            matcher: 技能匹配器
            executor: 技能执行器
        """
        cls._dependencies = {
            'loader': loader,
            'matcher': matcher,
            'executor': executor
        }

    @classmethod
    def register(cls, name: str, tool_builder: Callable) -> None:
        """
        注册工具构建函数
        
        Args:
            name: 工具名称，如 "skill_list"
            tool_builder: 工具构建函数，接收依赖参数，返回 BaseTool
        """
        cls._tools[name] = tool_builder

    @classmethod
    def build(cls) -> List[BaseTool]:
        """
        构建所有已注册的工具实例
        
        Returns:
            所有工具实例列表
        """
        return [
            builder(**cls._dependencies)
            for builder in cls._tools.values()
        ]

    @classmethod
    def get_supported_tools(cls) -> List[str]:
        """
        获取支持的工具名称列表
        
        Returns:
            支持的工具名称列表
        """
        return list(cls._tools.keys())


__all__ = ['SkillToolFactory']
