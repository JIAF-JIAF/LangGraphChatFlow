"""
RAG检索相关节点

负责：
1. 检索路由：判断是否需要检索
2. 文档检索：从知识库检索相关文档
"""

from typing import Dict, Any
from langgraph.config import get_stream_writer
from modules.logger import log
from .steps import Step


class RouterNode:
    """检索路由节点 - 判断是否需要检索"""

    def __init__(self, rag_workflow: Any):
        """
        初始化检索路由节点

        Args:
            rag_workflow: RAG工作流实例
        """
        self._rag_workflow = rag_workflow

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        判断是否需要检索

        Args:
            state: 当前状态（包含 query, session_id, chat_history, feeling）

        Returns:
            更新后的状态（包含 need_retrieve）
        """
        writer = get_stream_writer()
        query = state["query"]

        writer(Step.RAG_ROUTER.started_event())
        log(f"[节点: {Step.RAG_ROUTER.step}] 开始执行查询: {query[:30]}...", "LangGraph")

        need_retrieve = self._rag_workflow.should_retrieve(query)
        detail = "需要检索" if need_retrieve else "无需检索"
        writer(Step.RAG_ROUTER.completed_event(detail=detail))
        log(f"[节点: {Step.RAG_ROUTER.step}] 决策: {detail}", "LangGraph")

        return {"need_retrieve": need_retrieve}


class RetrieveNode:
    """检索节点 - 执行文档检索"""

    def __init__(self, rag_workflow: Any):
        """
        初始化检索节点

        Args:
            rag_workflow: RAG工作流实例
        """
        self._rag_workflow = rag_workflow

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行文档检索

        Args:
            state: 当前状态

        Returns:
            更新后的状态（documents 使用 list_append，返回增量）
        """
        writer = get_stream_writer()
        query = state["query"]

        writer(Step.RETRIEVE.started_event())
        log(f"[节点: {Step.RETRIEVE.step}] 开始执行", "LangGraph")

        kb = self._rag_workflow.select_knowledge_base(query)
        self._rag_workflow.switch_knowledge_base(kb)

        documents = self._rag_workflow.retrieve(query)
        log(f"[节点: {Step.RETRIEVE.step}] 检索到 {len(documents)} 个文档", "LangGraph")

        rag_success = len(documents) > 0
        detail = f"检索到 {len(documents)} 条结果"
        writer(Step.RETRIEVE.completed_event(detail=detail))
        log(f"[节点: {Step.RETRIEVE.step}] RAG 成功: {rag_success}", "LangGraph")

        return {
            "documents": documents,
            "rag_success": rag_success,
        }
