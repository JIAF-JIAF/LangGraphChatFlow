"""
对话记忆实现

使用 LangChain 的 InMemoryChatMessageHistory 存储对话历史，支持多会话管理。

核心功能：
1. 存储用户和助手的对话消息
2. 支持多会话隔离（通过 session_id）
3. 自动修剪过长的历史记录

适用于需要保持对话上下文的场景。
"""

from typing import Dict, Optional
from langchain_core.chat_history import InMemoryChatMessageHistory

from .base import BaseMemory


class ConversationMemory(BaseMemory):
    """
    对话记忆实现
    
    使用 InMemoryChatMessageHistory 存储对话历史，支持多会话管理。
    """

    def __init__(self):
        """
        初始化对话记忆
        """
        super().__init__()
        self._history_store: Dict[str, InMemoryChatMessageHistory] = {}

    def get_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """
        获取或创建会话历史
        
        Args:
            session_id: 会话 ID
            
        Returns:
            InMemoryChatMessageHistory 实例
        """
        if session_id not in self._history_store:
            self._history_store[session_id] = InMemoryChatMessageHistory()
        return self._history_store[session_id]

    def add_message(self, session_id: str, role: str, content: str):
        """
        添加消息到历史
        
        Args:
            session_id: 会话 ID
            role: 角色（human/assistant）
            content: 消息内容
        """
        history = self.get_history(session_id)
        
        if role == "human":
            history.add_user_message(content)
        elif role == "assistant":
            history.add_ai_message(content)
        else:
            history.add_message({"role": role, "content": content})

        # 限制历史长度
        self._trim_history(session_id)

    def _trim_history(self, session_id: str):
        """
        修剪历史记录到最大长度
        
        Args:
            session_id: 会话 ID
        """
        history = self._history_store.get(session_id)
        if history:
            messages = history.messages
            if len(messages) > self.max_history_length * 2:  # 每条对话包含 human + assistant
                history.clear()
                for msg in messages[-self.max_history_length * 2:]:
                    history.add_message(msg)

    def clear_history(self, session_id: str):
        """
        清除会话历史
        
        Args:
            session_id: 会话 ID
        """
        if session_id in self._history_store:
            self._history_store[session_id].clear()

    def get_runnable_history(self):
        """
        获取 RunnableWithMessageHistory 兼容的历史获取函数
        
        Returns:
            历史获取函数
        """
        return lambda session_id: self.get_history(session_id)

    def get_history_str(self, session_id: str) -> str:
        """
        获取历史记录字符串
        
        Args:
            session_id: 会话 ID
            
        Returns:
            格式化的历史记录字符串
        """
        history = self.get_history(session_id)
        messages = []
        for msg in history.messages:
            if hasattr(msg, 'role'):
                role = msg.role
                content = msg.content if hasattr(msg, 'content') else str(msg)
                messages.append(f"{role}: {content}")
        return "\n".join(messages)
