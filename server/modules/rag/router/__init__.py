"""
路由模块
负责决定是否需要检索、使用哪个知识库、使用哪种检索策略

支持的路由器类型：
- BaseRouter: 路由器基类
- SimpleRouter: 简单路由器（始终返回True）
- LLMRouter: 基于LLM的智能路由器（根据问题类型智能判断）
"""

from .base import BaseRouter
from .simple import SimpleRouter
from .llm_router import LLMRouter

__all__ = [
    'BaseRouter',
    'SimpleRouter',
    'LLMRouter'
]
