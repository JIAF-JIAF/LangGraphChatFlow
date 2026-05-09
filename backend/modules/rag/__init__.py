"""
模块化 RAG 框架
提供可插拔的 RAG 组件，支持自由组合
"""

# RAG 链核心
from .rag import RAGWorkflow

__all__ = [
    # RAG 链
    'RAGWorkflow'
]
