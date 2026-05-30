"""
多 Agent 状态定义

扩展现有 AgentState，保留全部字段，新增多 Agent 协作所需字段。

设计原则：
- 完全兼容现有 AgentState（所有字段原样保留，类型一致）
- chat_history 保留 add_messages_with_truncation reducer（裁剪逻辑不丢失）
- agent_results 使用 operator.add reducer（支持 Send API 并行写入安全聚合）
- current_agent 为普通字段（同一时刻只有一个活跃 Agent）

类型对照（与 states/base.py 严格一致）：
- feeling: FeelingState（Pydantic BaseModel），不是 Dict
- subtasks: List[SubTaskState]（Pydantic BaseModel），不是 List[Dict]
"""

from typing import TypedDict, Annotated, Optional, List, Dict, Any
from operator import add
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document

from modules.langgraph.states.base import add_messages_with_truncation, FeelingState, SubTaskState


class MultiAgentState(TypedDict):
    """
    多 Agent 状态（扩展 AgentState，保留全部现有字段）

    现有字段与 AgentState 完全一致，新增：
    - current_agent: 当前活跃 Agent 名称
    - agent_results: 各 Agent 结果（支持并行追加）
    """
    # === ContextState：对话上下文 ===
    query: str                                              # 用户原始输入
    session_id: str                                         # 会话唯一标识，用于 Checkpoint 持久化
    uid: Optional[str]                                      # 用户标识，用于权限控制和个性化
    chat_history: Annotated[List[BaseMessage], add_messages_with_truncation(20)]  # 对话历史，超过 20 条自动裁剪

    # === RAGState：知识检索 ===
    need_retrieve: bool                                     # 是否需要触发知识库检索
    documents: List[Document]                               # RAG 检索到的文档片段列表
    answer: str                                             # 最终生成的回答文本
    feeling: FeelingState                                   # 情绪检测结果 Pydantic Model {"feeling": str, "score": int}
    rag_success: bool                                       # RAG 检索是否成功返回有效结果

    # === TaskState：任务规划 ===
    subtasks: List[SubTaskState]                            # TaskPlanner 分解的子任务列表（Pydantic Model）
    current_task_idx: int                                   # 当前正在执行的子任务索引
    is_task_completed: bool                                 # 所有子任务是否已执行完毕

    # === IntentState：意图识别 ===
    intents: List[Dict[str, Any]]                           # 识别出的意图列表（支持多意图）
    is_multi_intent: bool                                   # 是否为多意图（用户一句话包含多个需求）
    current_intent_idx: int                                 # 当前正在处理的意图索引
    current_intent: Optional[Dict[str, Any]]                # 当前正在处理的意图对象
    execution_mode: str                                     # 执行模式："plan" / "direct" / "system"
    intent_results: List[Dict[str, Any]]                    # 各意图的执行结果列表

    # === 多 Agent 协作字段 ===
    current_agent: str                                      # 当前活跃的 Agent 名称（如 "rag_expert"），同一时刻仅一个
    agent_results: Annotated[List[Dict[str, Any]], add]     # 各 Agent 返回结果，operator.add reducer 支持 Send 并行安全追加


def create_multi_agent_initial_state(
    query: str,
    session_id: str,
    uid: Optional[str] = None,
) -> Dict[str, Any]:
    """创建多 Agent 初始状态（与 create_initial_state 默认值一致）"""
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
        "intents": [],
        "is_multi_intent": False,
        "current_intent_idx": 0,
        "current_intent": None,
        "execution_mode": "plan",
        "intent_results": [],
        "current_agent": "",
        "agent_results": [],
    }
