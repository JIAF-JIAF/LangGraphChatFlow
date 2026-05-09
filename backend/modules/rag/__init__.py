"""
模块化 RAG 框架
提供可插拔的 RAG 组件，支持自由组合

模块结构：
- indexer: 索引模块（文档加载、切分、向量化）
- retriever: 检索模块（向量检索、过滤、重排序）
- generator: 生成模块（Stuff/Map-Reduce/Refine）
- memory: 记忆模块（对话历史管理）
- router: 路由模块（检索决策、策略选择）
- rag_chain: RAG 链核心（组合所有模块）
"""

# 索引模块
from .indexer import BaseIndexer, ChromaIndexer, MilvusIndexer

# 检索模块
from .retriever import BaseRetriever, SimpleVectorRetriever

# 生成模块
from .generator import BaseGenerator, StuffGenerator, MapReduceGenerator, RefineGenerator

# 记忆模块
from .memory import BaseMemory, ConversationMemory, KnowledgeMemory

# 路由模块
from .router import BaseRouter, SimpleRouter

# RAG 链核心
from .rag_chain import RAGChain

__all__ = [
    # 索引模块
    'BaseIndexer',
    'ChromaIndexer',
    'MilvusIndexer',

    # 检索模块
    'BaseRetriever',
    'SimpleVectorRetriever',

    # 生成模块
    'BaseGenerator',
    'StuffGenerator',
    'MapReduceGenerator',
    'RefineGenerator',

    # 记忆模块
    'BaseMemory',
    'ConversationMemory',
    'KnowledgeMemory',

    # 路由模块
    'BaseRouter',
    'SimpleRouter',

    # RAG 链
    'RAGChain'
]
