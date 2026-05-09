"""
简单路由器

基于规则的路由决策实现。

提供默认的路由逻辑，所有方法返回默认值，不包含实际规则判断。
可作为基础实现，后续可根据业务需求扩展具体的路由规则。

当前实现：
- should_retrieve：始终返回 True（默认需要检索）
- select_knowledge_base：始终返回 None（使用默认知识库）
- select_retrieval_strategy：始终返回空字典（使用默认策略）
"""

from typing import Optional, Dict, Any

from .base import BaseRouter


class SimpleRouter(BaseRouter):
    """
    简单路由器
    
    提供基础的路由决策接口，所有方法返回默认值。
    """

    def should_retrieve(self, query: str) -> bool:
        """
        判断是否需要检索
        
        默认返回 True，即始终进行检索。
        
        Args:
            query: 用户查询文本
            
        Returns:
            True（始终需要检索）
        """
        return True

    def select_knowledge_base(self, query: str) -> Optional[str]:
        """
        选择知识库
        
        默认返回 None，即使用默认知识库。
        
        Args:
            query: 用户查询文本
            
        Returns:
            None（使用默认知识库）
        """
        return None

    def select_retrieval_strategy(self, query: str) -> Dict[str, Any]:
        """
        选择检索策略
        
        默认返回空字典，即使用默认检索参数。
        
        Args:
            query: 用户查询文本
            
        Returns:
            空字典（使用默认策略）
        """
        return {}
