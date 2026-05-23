"""
基于RAG结果的任务生成器
"""

from typing import List, Dict, Any, Optional
from ..state import AgentState
from .base import TaskGeneratorHandler


class RagRefineTaskGenerator(TaskGeneratorHandler):
    """基于RAG结果的任务生成器"""
    
    def _try_handle(self, state: AgentState, planner, query: str) -> Optional[List[Dict[str, Any]]]:
        """
        当 RAG 检索成功时，生成基于文档的任务
        
        Args:
            state: 当前状态，包含 documents 和 rag_success
            planner: 任务规划器
            query: 用户查询
            
        Returns:
            子任务列表，或 None（交给下一个处理器）
        """
        rag_success = state.get("rag_success", False)
        documents = state.get("documents", [])
        
        # 如果 RAG 没有检索到文档，交给下一个处理器
        if not rag_success or not documents:
            return None
        
        print(f"[任务生成] 使用RAG文档策略，文档数: {len(documents)}")
        
        return [{
            "task_id": "task_1",
            "task_description": f"请基于提供的参考文档回答用户问题：{query}\n\n注意：参考文档已经在上下文中提供，请直接基于文档内容回答，不要使用任何工具。",
            "dependencies": [],
            "status": "pending",
            "result": ""
        }]
