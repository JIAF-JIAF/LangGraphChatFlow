"""
Skill 工具动态适配器

Skill 工具列表是动态的（可安装/删除），不能硬编码枚举。

封装策略：
  1. get_skill_tools(skill_manager) — 直接透传 SkillManager.get_tools() 返回的 List[BaseTool]
  2. reload_skill_tools(skill_manager) — 刷新技能工具列表（安装/删除技能后调用）
  3. skill_execute(skill_name, content) — 兜底工具，委托 ExecutorRegistry.build("skill") 执行

现有 API 对照：
  SkillManager.get_tools() -> List[BaseTool]（skill_list, skill_instructions, skill_run_script 等）
  SkillManager.reload() -> None
  ExecutorRegistry.build("skill", agent=...) -> SkillExecutor
  SkillExecutor.execute(intent, context) -> ExecutionResult
"""

from typing import List
from langchain_core.tools import BaseTool, tool
from modules.langgraph.executors.registry import ExecutorRegistry
from modules.logger import log


def get_skill_tools(skill_manager) -> List[BaseTool]:
    """从 SkillManager 动态获取技能工具列表

    Args:
        skill_manager: SkillManager 实例

    Returns:
        LangChain BaseTool 列表，包含当前所有可用技能工具
    """
    try:
        tools = skill_manager.get_tools()
        tool_names = [t.name for t in tools]
        log(f"[SkillAdapter] 获取到 {len(tools)} 个技能工具: {tool_names}", "MultiAgent")
        return tools
    except Exception as e:
        log(f"[SkillAdapter] 获取技能工具失败: {e}", "MultiAgent")
        return []


def reload_skill_tools(skill_manager) -> List[BaseTool]:
    """刷新技能工具列表（安装/删除技能后调用）

    Args:
        skill_manager: SkillManager 实例

    Returns:
        刷新后的 LangChain BaseTool 列表
    """
    try:
        skill_manager.reload()
        return get_skill_tools(skill_manager)
    except Exception as e:
        log(f"[SkillAdapter] 刷新技能工具失败: {e}", "MultiAgent")
        return []


@tool
def skill_execute(skill_name: str, content: str) -> str:
    """执行指定技能。当其他技能工具无法满足需求时使用此通用入口，委托 SkillExecutor 执行。

    Args:
        skill_name: 技能名称（如 drawio-skill, tldraw-skill, data-analysis）
        content: 技能执行的内容描述
    """
    executor = ExecutorRegistry.build("skill")
    intent = {
        "type": f"skill_{skill_name}",
        "category": "skill",
        "target": f"skill:{skill_name}",
        "content": content,
    }
    result = executor.execute(intent, context={"chat_history": [], "feeling": {}})
    log(f"[SkillAdapter] 兜底执行技能: {skill_name}", "MultiAgent")
    return result.content if result.success else f"执行失败: {result.error}"
