"""
任务生成责任链模块

使用责任链模式处理任务生成逻辑，支持：
- 基于RAG结果润色的任务生成
- 默认规划策略（兜底）

新增任务生成策略只需：
1. 在本文件夹创建新的处理器类
2. 在 TaskGeneratorChain.build() 中注册
"""

from .base import TaskGeneratorHandler
from .rag_refine_handler import RagRefineTaskGenerator
from .default_handler import DefaultTaskGenerator
from .chain import TaskGeneratorChain

__all__ = [
    "TaskGeneratorHandler",
    "RagRefineTaskGenerator",
    "DefaultTaskGenerator",
    "TaskGeneratorChain"
]
