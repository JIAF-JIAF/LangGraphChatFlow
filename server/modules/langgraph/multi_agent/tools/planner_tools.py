"""
Planner 工具封装

将 TaskPlanner 封装为 LangChain @tool，供 Planner Subgraph 内部使用。

对照现有 TaskPlanner：
  TaskPlanner.plan(query, context="") -> List[Dict[str, Any]]
  TaskPlanner.get_summary(subtasks) -> str

封装后：
  decompose_task(query, context) — 分解复杂任务为子任务列表
  summarize_results(query, results) — 汇总子任务结果为最终回答
"""

import json
from typing import List
from langchain_core.tools import tool
from modules.langgraph.planner.task_planner import TaskPlanner
from modules.logger import log


def create_planner_tools(task_planner: TaskPlanner) -> List:
    """将 TaskPlanner 封装为 LangChain @tool

    Args:
        task_planner: TaskPlanner 实例

    Returns:
        [decompose_task, summarize_results] 工具列表
    """

    @tool
    def decompose_task(query: str, context: str = "") -> str:
        """将复杂任务分解为子任务列表。当用户的问题需要多步骤处理时使用。

        Args:
            query: 用户的问题或任务描述
            context: 额外上下文信息（可选）
        """
        log(f"[PlannerTool] 分解任务: {query[:30]}...", "MultiAgent")
        subtasks = task_planner.plan(query, context)
        return json.dumps(subtasks, ensure_ascii=False, indent=2)

    @tool
    def summarize_results(query: str, results: str) -> str:
        """将多个子任务的结果汇总为最终回答。当所有子任务完成后使用。

        Args:
            query: 原始用户问题
            results: 各子任务的执行结果（JSON 格式）
        """
        log("[PlannerTool] 汇总结果", "MultiAgent")
        try:
            subtasks = json.loads(results) if isinstance(results, str) else results
        except json.JSONDecodeError:
            subtasks = [{"task_description": query, "result": results, "status": "completed"}]

        summary = task_planner.get_summary(subtasks)
        return summary if summary else str(results)

    return [decompose_task, summarize_results]
