"""
skill_list 工具

列出/搜索可用技能

【功能说明】
列出系统中所有可用的技能，或根据关键词搜索相关技能。
这是技能发现的第一步，遵循 Skills as Tools 标准的"发现"阶段。

【调用者】
- LangChain Agent：在 execute_task 节点中，当 Agent 需要判断是否有技能能处理用户请求时调用
- 用户请求示例："帮我画一个流程图"、"生成一个报告"

【消费者】
- LangChain Agent：获取技能列表后，Agent 根据描述判断哪个技能适合处理当前请求
- 返回格式：技能名称 + 描述的列表字符串

【工作流程】
1. Agent 收到用户请求（如"画流程图"）
2. Agent 调用 skill_list(query="流程图") 搜索相关技能
3. 返回匹配的技能信息："找到相关技能：\n- drawio-skill: 用于生成流程图..."
4. Agent 根据返回结果决定下一步调用 skill_instructions 获取详细指令

【参数说明】
- query: 搜索关键词（可选）
  - 为空：列出所有技能
  - 不为空：先精确匹配，匹配失败则返回所有技能

【返回值】
- 成功：技能列表字符串，格式为 "技能名称: 技能描述"
- 失败："当前没有可用技能" 或 "没有找到相关技能"
"""

from typing import Any
from pydantic import BaseModel, Field, PrivateAttr
from langchain_core.tools import BaseTool
from modules.logger import log
from .factory import SkillToolFactory


class SkillListInput(BaseModel):
    query: str = Field(default="", description="搜索关键词，为空则列出所有技能")


class SkillListTool(BaseTool):
    name: str = "skill_list"
    description: str = "列出可用技能。提供关键词可筛选相关技能，不提供则列出所有技能。当你需要判断是否有技能能处理用户请求时，先调用此工具。"
    args_schema: type[BaseModel] = SkillListInput
    
    _loader: Any = PrivateAttr()
    _matcher: Any = PrivateAttr()
    
    def __init__(self, loader: Any, matcher: Any, **data):
        super().__init__(**data)
        self._loader = loader
        self._matcher = matcher
    
    def _run(self, query: str = "") -> str:
        log(f"skill_list 被调用，query={query}", module="Skill.Tools")
        skills = self._loader.list_skills()
        
        if query:
            matched = self._matcher.match_skill(query)
            if matched:
                return f"找到相关技能：\n- {matched['name']}: {matched['description']}"
            
            if not skills:
                return "没有找到相关技能"
            
            return "未精确匹配，所有可用技能：\n" + "\n".join(
                f"- {s['name']}: {s['description']}" for s in skills
            )
        
        if not skills:
            return "当前没有可用技能"
        
        return "可用技能：\n" + "\n".join(
            f"- {s['name']}: {s['description']}" for s in skills
        )


def build_skill_list_tool(loader, matcher, executor):
    """
    构建 skill_list 工具
    
    Args:
        loader: 技能加载器
        matcher: 技能匹配器
        executor: 技能执行器
        
    Returns:
        skill_list 工具实例
    """
    return SkillListTool(loader=loader, matcher=matcher)


SkillToolFactory.register("skill_list", build_skill_list_tool)
