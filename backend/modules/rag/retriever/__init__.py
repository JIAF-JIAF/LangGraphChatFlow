"""
检索模块
负责从索引中检索相关文档，支持多种检索策略

已实现：
- SimpleVectorRetriever：基于向量相似度的简单检索
- RerankingRetriever：重排序检索（使用 Cross-Encoder 模型）

预留接口：
- FilteredRetriever：过滤检索
"""

from .base import BaseRetriever
from .simple import SimpleVectorRetriever
from .reranking import RerankingRetriever

__all__ = [
    'BaseRetriever',
    'SimpleVectorRetriever',
    'RerankingRetriever'
]
