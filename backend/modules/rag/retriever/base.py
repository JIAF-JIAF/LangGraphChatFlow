"""
检索模块基类

定义检索器的通用接口，提供空方法实现作为默认行为。
子类可覆盖这些方法实现具体的检索策略。

检索器负责从索引中查询与用户问题相关的文档。

核心职责：
1. 执行检索（retrieve）：根据查询文本返回相关文档
2. 获取相关文档（get_relevant_documents）：兼容 LangChain 接口

支持的检索策略：
- 简单向量检索（SimpleVectorRetriever）
- 重排序检索（RerankingRetriever）：先检索再重排序
- 过滤检索（FilteredRetriever）：支持元数据过滤
"""

import os
from typing import List, Optional, Dict
from langchain_core.documents import Document

from modules.logger import log


class BaseRetriever:
    """
    检索器基类
    
    定义检索器的通用接口，提供空方法实现作为默认行为。
    子类可覆盖这些方法实现具体的检索策略。
    
    属性：
        indexer: 索引器实例，用于访问向量数据库
        retrieval_kwargs: 检索参数（如 k：返回文档数量）

    配置项（环境变量）：
        RETRIEVER_K: 返回文档数量（默认3）
    """

    def __init__(self, indexer=None):
        """
        初始化检索器
        
        Args:
            indexer: 索引器实例
        """
        self.indexer = indexer
        k = int(os.getenv("RETRIEVER_K", 3))
        self.retrieval_kwargs = {"k": k}

    def retrieve(self, query: str) -> List[Document]:
        """
        执行检索
        
        默认返回空列表，子类需覆盖此方法实现具体的检索逻辑。
        
        Args:
            query: 查询文本
            
        Returns:
            相关文档列表，默认返回空列表
        """
        log("[WARN] BaseRetriever.retrieve: 使用基类默认实现（未实现具体逻辑）", "Retriever")
        return []

    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        获取相关文档（兼容 LangChain 接口）
        
        Args:
            query: 查询文本
            
        Returns:
            相关文档列表
        """
        return self.retrieve(query)
