"""
简单向量检索器

基于向量相似度进行检索，是最基础的检索策略。

工作原理：
1. 将用户查询转换为向量
2. 在向量数据库中查找与查询向量最相似的文档向量
3. 返回相似度最高的前 k 个文档

适用于大多数常见场景，是默认的检索策略。
"""

from typing import List, Optional, Dict
from langchain_core.documents import Document

from .base import BaseRetriever


class SimpleVectorRetriever(BaseRetriever):
    """
    简单向量检索器
    
    基于向量相似度进行检索。
    """

    def __init__(self, indexer=None):
        """
        初始化检索器
        
        Args:
            indexer: 索引器实例，用于获取底层检索器
        """
        super().__init__(indexer=indexer)
        self._retriever = None
        self._init_retriever()

    def _init_retriever(self):
        """初始化底层检索器"""
        if self.indexer:
            self._retriever = self.indexer.get_retriever(
                search_kwargs=self.retrieval_kwargs
            )

    def retrieve(self, query: str) -> List[Document]:
        """
        执行向量检索
        
        Args:
            query: 查询文本
            
        Returns:
            相关文档列表
        """
        if not self._retriever:
            return []
        return self._retriever.invoke(query)

    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        获取相关文档（兼容 LangChain 接口）
        
        Args:
            query: 查询文本
            
        Returns:
            相关文档列表
        """
        return self.retrieve(query)
