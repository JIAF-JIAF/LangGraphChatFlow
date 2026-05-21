"""
LangGraph 状态定义

采用 Pydantic 子状态 + TypedDict 顶层模式：
- 子状态使用 Pydantic BaseModel（类型安全、自动校验、默认值）
- 顶层状态使用 TypedDict（支持 state["key"] 访问）
- chat_history 使用带裁剪的 add_messages reducer 实现增量追加
"""

from typing import TypedDict, Optional, List, Dict, Any, Annotated, Callable
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document
from langgraph.graph.message import add_messages


def add_messages_with_truncation(max_messages: int = 20) -> Callable[[List[BaseMessage], List[BaseMessage]], List[BaseMessage]]:
    """
    创建带裁剪功能的消息追加 reducer
    
    Args:
        max_messages: 最大消息数（默认20条，即10轮对话）
    
    Returns:
        带裁剪功能的 reducer 函数
    """
    def reducer(existing: List[BaseMessage], updates: List[BaseMessage]) -> List[BaseMessage]:
        combined = existing + updates
        if len(combined) > max_messages:
            return combined[-max_messages:]
        return combined
    return reducer


class FeelingState(BaseModel):
    feeling: str = "default"
    score: int = 5


class SkillStepState(BaseModel):
    number: int = 0
    name: str = ""
    status: str = ""
    output: str = ""
    duration: Optional[float] = None


class SubTaskState(BaseModel):
    task_id: str = ""
    task_description: str = ""
    dependencies: List[str] = Field(default_factory=list)
    status: str = "pending"
    result: str = ""


class ContextState(TypedDict):
    """上下文相关状态"""
    query: str
    session_id: str
    uid: Optional[str]
    chat_history: Annotated[List[BaseMessage], add_messages_with_truncation(20)]


class RAGState(TypedDict):
    """RAG 检索相关状态"""
    need_retrieve: bool
    documents: List[Document]
    answer: str
    feeling: FeelingState
    rag_success: bool


class TaskState(TypedDict):
    """任务规划相关状态"""
    subtasks: List[SubTaskState]
    current_task_idx: int
    is_task_completed: bool


class ReflectionState(TypedDict):
    """反思校验相关状态"""
    is_reflection_passed: bool
    reflection_feedback: str
    reflection_suggestions: List[str]
    reflection_confidence: float


class RetryState(TypedDict):
    """重试控制相关状态"""
    retry_count: int
    max_retries: int
    retry_task_idx: int


class SkillState(TypedDict):
    """技能匹配相关状态"""
    matched_skill: Optional[dict]
    skill_executed: bool
    skill_name: str
    skill_success: bool
    skill_steps: List[SkillStepState]


class AgentState(ContextState, RAGState, TaskState, ReflectionState, RetryState, SkillState):
    """完整 Agent 状态（多重继承组合所有子状态）"""
    pass


def create_initial_state(
    query: str,
    session_id: str,
    uid: Optional[str] = None,
    max_retries: int = 3
) -> AgentState:
    return {
        "query": query,
        "session_id": session_id,
        "uid": uid,
        "chat_history": [],
        "need_retrieve": False,
        "documents": [],
        "answer": "",
        "feeling": FeelingState(),
        "rag_success": False,
        "subtasks": [],
        "current_task_idx": 0,
        "is_task_completed": False,
        "is_reflection_passed": False,
        "reflection_feedback": "",
        "reflection_suggestions": [],
        "reflection_confidence": 0.0,
        "retry_count": 0,
        "max_retries": max_retries,
        "retry_task_idx": -1,
        "matched_skill": None,
        "skill_executed": False,
        "skill_name": "",
        "skill_success": False,
        "skill_steps": [],
    }
