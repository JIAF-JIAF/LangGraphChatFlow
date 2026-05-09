"""
LangGraph 状态定义
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document


class AgentState(TypedDict):
    """Agent 状态定义"""
    input: str  # 用户输入的查询文本
    chat_history: List[BaseMessage]  # 对话历史消息列表
    output: str  # Agent 输出的响应文本
    intermediate_steps: List[Any]  # 中间步骤记录（如工具调用过程）
    tool_messages: List[Dict[str, Any]]  # 工具调用结果列表


class RAGState(TypedDict):
    """RAG 工作流状态定义"""
    query: str  # 用户查询文本
    session_id: str  # 会话 ID，用于区分不同对话
    need_retrieve: bool  # 是否需要检索知识库
    knowledge_base: str  # 选定的知识库名称
    documents: List[Document]  # 检索到的文档列表
    answer: str  # 生成的最终回答
    router_decision: Optional[Dict[str, Any]]  # 路由器决策详情（可选）
