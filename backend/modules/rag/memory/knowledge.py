"""
知识记忆（预留接口）

用于存储长期知识和检索历史，与短期对话记忆形成互补。

预留功能：
1. 存储从知识库中检索到的知识片段
2. 支持知识的长期存储和复用
3. 可用于增强模型的长期记忆能力

当前为预留接口，暂未实现完整功能。
"""

from typing import Dict, List, Optional

from .base import BaseMemory


class KnowledgeMemory(BaseMemory):
    """
    知识记忆（预留接口）
    
    用于存储长期知识和检索历史。
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化知识记忆
        
        Args:
            config: 配置参数（可选）
        """
        super().__init__(config=config)
        self._knowledge_store: Dict[str, List[Dict]] = {}

    def get_history(self, session_id: str):
        """
        获取知识历史
        
        Args:
            session_id: 会话 ID
            
        Returns:
            知识历史列表
        """
        return self._knowledge_store.get(session_id, [])

    def add_message(self, session_id: str, role: str, content: str):
        """
        添加知识记录（预留实现）
        
        Args:
            session_id: 会话 ID
            role: 角色
            content: 内容
        """
        if session_id not in self._knowledge_store:
            self._knowledge_store[session_id] = []
        self._knowledge_store[session_id].append({
            "role": role,
            "content": content,
            "timestamp": None  # 预留时间戳字段
        })

    def clear_history(self, session_id: str):
        """
        清除知识历史
        
        Args:
            session_id: 会话 ID
        """
        if session_id in self._knowledge_store:
            self._knowledge_store[session_id] = []
