"""
LangGraph 状态模块

采用 Pydantic 子状态 + TypedDict 顶层 + Annotated Reducer 模式：
- 子状态使用 Pydantic BaseModel（类型安全、自动校验、默认值）
- 顶层状态使用 TypedDict（支持 state["key"] 访问）
- List 字段使用 Annotated + Reducer 实现自动追加

模块划分：
- ContextState: 上下文（query, session_id, uid, chat_history）
- RAGState: RAG 检索（documents, answer, feeling, need_retrieve）
- TaskState: 任务规划（subtasks, current_task_idx, is_task_completed）
- ReflectionState: 反思校验（is_reflection_passed, reflection_feedback）
- RetryState: 重试控制（retry_count, max_retries, retry_task_idx）
- SkillState: 技能匹配（matched_skill, skill_name, skill_steps）
"""

from .base import (
    AgentState,
    ContextState,
    RAGState,
    TaskState,
    ReflectionState,
    RetryState,
    SkillState,
    FeelingState,
    SubTaskState,
    SkillStepState,
    create_initial_state,
)

__all__ = [
    "AgentState",
    "ContextState",
    "RAGState",
    "TaskState",
    "ReflectionState",
    "RetryState",
    "SkillState",
    "FeelingState",
    "SubTaskState",
    "SkillStepState",
    "create_initial_state",
]
