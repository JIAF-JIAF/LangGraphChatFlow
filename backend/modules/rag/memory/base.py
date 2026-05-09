"""
记忆模块基类

定义记忆模块的通用接口，提供空方法实现作为默认行为。
子类可覆盖这些方法实现具体的存储方案。

记忆模块负责管理对话历史和长期知识，支持多会话管理。

核心职责：
1. 获取历史（get_history）：获取指定会话的历史记录
2. 添加消息（add_message）：向历史中添加消息
3. 清除历史（clear_history）：清除指定会话的历史

支持的记忆类型：
- 对话记忆（ConversationMemory）：存储短期对话历史
- 知识记忆（KnowledgeMemory）：存储长期知识（预留接口）
"""

from typing import Optional, Dict, List


class BaseMemory:
    """
    记忆模块基类
    
    定义记忆模块的通用接口，提供空方法实现作为默认行为。
    子类可覆盖这些方法实现具体的存储方案。
    
    属性：
        config: 配置字典
        max_history_length: 最大历史记录长度
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化记忆模块
        
        Args:
            config: 配置参数（可选）
        """
        self.config = config or {}
        self.max_history_length = self.config.get("max_history_length", 10)

    def get_history(self, session_id: str) -> List:
        """
        获取会话历史
        
        默认返回空列表，子类需覆盖此方法实现具体逻辑。
        
        Args:
            session_id: 会话 ID
            
        Returns:
            会话历史对象或列表，默认返回空列表
        """
        print("[WARN] BaseMemory.get_history: 使用基类默认实现（未实现具体逻辑）")
        return []

    def add_message(self, session_id: str, role: str, content: str):
        """
        添加消息到历史
        
        默认不执行任何操作，子类需覆盖此方法实现具体逻辑。
        
        Args:
            session_id: 会话 ID
            role: 角色（human/assistant/system）
            content: 消息内容
        """
        print("[WARN] BaseMemory.add_message: 使用基类默认实现（未实现具体逻辑）")
        pass

    def clear_history(self, session_id: str):
        """
        清除会话历史
        
        默认不执行任何操作，子类需覆盖此方法实现具体逻辑。
        
        Args:
            session_id: 会话 ID
        """
        print("[WARN] BaseMemory.clear_history: 使用基类默认实现（未实现具体逻辑）")
        pass
