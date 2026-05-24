"""
默认任务生成器（兜底）
"""

from typing import List, Dict, Any, Optional
from ..state import AgentState
from .base import TaskGeneratorHandler
from modules.logger import log


class DefaultTaskGenerator(TaskGeneratorHandler):
    """默认任务生成器（兜底）"""
    
    def _try_handle(self, state: AgentState, planner, query: str) -> Optional[List[Dict[str, Any]]]:
        log("使用默认规划策略", "TaskGenerator")
        
        context_parts = []
        if state.get("answer"):
            context_parts.append(f"初步分析结果：{state['answer']}")
        if state.get("documents"):
            context_parts.append("\n".join([doc.page_content[:500] for doc in state["documents"]]))
        context = "\n\n".join(context_parts)
        
        return planner.plan(query, context)
