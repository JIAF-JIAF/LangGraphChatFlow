"""
任务生成处理器基类
"""

from typing import List, Dict, Any, Optional
from ..state import AgentState


class TaskGeneratorHandler:
    """任务生成处理器基类"""
    
    def __init__(self, next_handler=None):
        """
        初始化处理器
        
        Args:
            next_handler: 下一个处理器（责任链中的下一环）
        """
        self._next_handler = next_handler
    
    def handle(self, state: AgentState, planner, query: str) -> List[Dict[str, Any]]:
        """
        处理请求，返回子任务列表
        
        Args:
            state: 当前 Agent 状态
            planner: 任务规划器实例
            query: 用户查询
            
        Returns:
            子任务列表
        """
        result = self._try_handle(state, planner, query)
        if result is not None:
            return result
        if self._next_handler:
            return self._next_handler.handle(state, planner, query)
        return []
    
    def _try_handle(self, state: AgentState, planner, query: str) -> Optional[List[Dict[str, Any]]]:
        """
        尝试处理请求（子类必须实现）
        
        Returns:
            - List[Dict]: 生成的子任务列表（成功）
            - None: 无法处理，交给下一个处理器
        """
        raise NotImplementedError("子类必须实现 _try_handle 方法")
