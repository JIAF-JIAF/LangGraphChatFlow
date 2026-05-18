"""
基于RAG结果润色的任务生成器
"""

from typing import List, Dict, Any, Optional
from ..state import AgentState
from .base import TaskGeneratorHandler


class RagRefineTaskGenerator(TaskGeneratorHandler):
    """基于RAG结果润色的任务生成器"""
    
    def _try_handle(self, state: AgentState, planner, query: str) -> Optional[List[Dict[str, Any]]]:
        rag_success = state.get("rag_success", False)
        rag_answer = state.get("answer", "")
        
        if not rag_success or not rag_answer:
            return None
        
        print(f"[任务生成] 使用RAG润色策略")
        
        return [{
            "task_id": "task_1",
            "task_description": f"请对以下内容进行润色和优化，使其更自然流畅：\n\n{rag_answer}",
            "dependencies": [],
            "status": "pending",
            "result": ""
        }]
