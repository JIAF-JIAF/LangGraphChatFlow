"""
路由模块基类

定义路由器的通用接口，提供空方法实现作为默认行为。
子类可覆盖这些方法实现具体的路由策略。

路由器负责决定是否需要检索、使用哪个知识库、采用哪种检索策略。

核心职责：
1. 判断是否需要检索（should_retrieve）
2. 选择知识库（select_knowledge_base）
3. 选择检索策略（select_retrieval_strategy）

支持的路由策略：
- 简单路由（SimpleRouter）：基于规则的路由决策
"""

from typing import Optional, Dict, Any


class BaseRouter:
    """
    路由器基类
    
    定义路由器的通用接口，提供空方法实现作为默认行为。
    子类可覆盖这些方法实现具体的路由策略。
    
    属性：
        config: 配置字典
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化路由器
        
        Args:
            config: 配置参数（可选）
        """
        self.config = config or {}

    def should_retrieve(self, query: str) -> bool:
        """
        判断是否需要检索
        
        默认返回 True，子类需覆盖此方法实现具体的路由逻辑。
        
        Args:
            query: 用户查询文本
            
        Returns:
            需要检索返回 True，否则返回 False，默认返回 True
        """
        print("[WARN] BaseRouter.should_retrieve: 使用基类默认实现（未实现具体逻辑）")
        return True

    def select_knowledge_base(self, query: str) -> Optional[str]:
        """
        选择知识库
        
        默认返回 None（使用默认知识库），子类需覆盖此方法实现具体逻辑。
        
        Args:
            query: 用户查询文本
            
        Returns:
            知识库名称，None 表示使用默认知识库
        """
        print("[WARN] BaseRouter.select_knowledge_base: 使用基类默认实现（未实现具体逻辑）")
        return None

    def select_retrieval_strategy(self, query: str) -> Dict[str, Any]:
        """
        选择检索策略
        
        默认返回空字典，子类需覆盖此方法实现具体逻辑。
        
        Args:
            query: 用户查询文本
            
        Returns:
            检索策略配置字典，默认返回空字典
        """
        print("[WARN] BaseRouter.select_retrieval_strategy: 使用基类默认实现（未实现具体逻辑）")
        return {}
