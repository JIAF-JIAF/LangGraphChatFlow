"""
重排序检索器

使用 Cross-Encoder 模型对检索结果进行重排序，提高检索准确性。

工作原理：
1. 先使用基础检索器获取候选文档（通常会获取更多候选，如 top-10）
2. 使用 Cross-Encoder 模型对每个文档进行评分
3. 根据评分对文档进行排序
4. 返回前 N 个最高分的文档

使用的模型：
- 默认使用 BAAI/bge-reranker-base（中文重排序效果较好）
- 支持自定义模型
"""

from typing import List, Optional, Dict, Tuple
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

from .base import BaseRetriever


class RerankingRetriever(BaseRetriever):
    """
    带重排序的检索器

    使用 Cross-Encoder 模型对检索结果进行重排序。
    """

    def __init__(self, base_retriever: BaseRetriever, config: Optional[Dict] = None):
        super().__init__(indexer=None, config=config)
        self.base_retriever = base_retriever
        
        # 配置参数
        self.rerank_top_k = self.config.get("rerank_top_k", 3)
        self.retrieve_top_k = self.config.get("retrieve_top_k", 10)
        self.model_name = self.config.get("model_name", "BAAI/bge-reranker-base")
        
        # 延迟加载重排序模型
        self._reranker = None

    @property
    def reranker(self):
        """延迟加载重排序模型"""
        if self._reranker is None:
            self._init_reranker()
        return self._reranker

    def _init_reranker(self):
        """初始化 Cross-Encoder 重排序模型"""
        try:
            self._reranker = CrossEncoder(self.model_name)
            print(f"[RERANK] 重排序模型加载成功: {self.model_name}")
        except Exception as e:
            print(f"[ERROR] 加载重排序模型失败: {e}")
            self._reranker = None

    def retrieve(self, query: str) -> List[Document]:
        """
        先检索后重排序

        Args:
            query: 查询文本

        Returns:
            重排序后的文档列表
        """
        # 1. 使用基础检索器获取候选文档
        documents = self.base_retriever.retrieve(query)
        
        if not documents:
            return []
        
        # 如果只有少量文档，直接返回
        if len(documents) <= self.rerank_top_k:
            return documents

        # 2. 如果重排序模型未加载或加载失败，直接返回前 N 个
        if not self.reranker:
            print("[RERANK] 重排序模型未加载，使用基础检索结果")
            return documents[:self.rerank_top_k]

        # 3. 使用 Cross-Encoder 进行重排序
        try:
            # 准备输入对 (query, document)
            pairs = [(query, doc.page_content) for doc in documents]
            
            # 获取评分
            scores = self.reranker.predict(pairs)
            
            # 按评分排序（降序）
            scored_docs = list(zip(documents, scores))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            # 返回前 N 个最高分的文档
            result = [doc for doc, score in scored_docs[:self.rerank_top_k]]
            
            print(f"[RERANK] 重排序完成，原始 {len(documents)} 篇，返回前 {self.rerank_top_k} 篇")
            return result
            
        except Exception as e:
            print(f"[ERROR] 重排序失败: {e}")
            # 如果重排序失败，返回基础检索结果
            return documents[:self.rerank_top_k]

    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        获取相关文档（兼容 LangChain 接口）

        Args:
            query: 查询文本

        Returns:
            相关文档列表
        """
        return self.retrieve(query)
