"""
Chroma 索引器
"""

import os
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_core.tools import StructuredTool

from .base import BaseIndexer


class ChromaIndexer(BaseIndexer):
    """
    Chroma 向量数据库索引器
    
    实现完整的向量存储功能，兼容原有 VectorStore 接口。
    支持多知识库，通过 collection_name 区分不同知识库。

    配置项（环境变量）：
        CHROMA_PERSIST_DIRECTORY: 向量数据库持久化目录（默认db/chroma）
        CHROMA_COLLECTION_NAME: 集合名称（默认knowledge_base）
    """

    def __init__(self, ai_client=None, collection_name: Optional[str] = None):
        super().__init__(ai_client=ai_client)
        
        self.persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "db/chroma")
        self.collection_name = collection_name or os.getenv("CHROMA_COLLECTION_NAME", "knowledge_base")
        self.vector_store = None

    def build_index(self, source_dir: str = "knowledge_base") -> Dict[str, Any]:
        """
        构建 Chroma 索引（兼容原有 init_knowledge_base 接口）
        
        Args:
            source_dir: 源文档目录
            
        Returns:
            包含状态和文档数量的字典
        """
        # 检查源目录，不存在则自动创建
        if not source_dir:
            return {"status": "error", "message": "源目录不能为空"}
        
        if not os.path.exists(source_dir):
            print(f"源目录不存在，自动创建: {source_dir}")
            os.makedirs(source_dir, exist_ok=True)
        
        # 尝试加载已存在的向量存储
        if self.load_index():
            stats = self.get_collection_stats()
            vector_count = stats.get("vector_count", 0)
            
            # 如果已存在向量，直接返回
            if vector_count > 0:
                return {
                    "status": "loaded",
                    "message": f"成功加载已存在的知识库",
                    "count": vector_count
                }
        
        # 从源目录创建新知识库
        if self._load_and_embed_documents(source_dir):
            stats = self.get_collection_stats()
            return {
                "status": "created",
                "message": "成功创建新知识库",
                "count": stats.get("vector_count", 0)
            }
        
        return {
            "status": "error",
            "message": "创建知识库失败"
        }

    def init_knowledge_base(self, source_dir: Optional[str] = "knowledge_base") -> Dict[str, Any]:
        """
        初始化知识库（兼容原有接口）
        
        Args:
            source_dir: 源文档目录路径
            
        Returns:
            包含 status、message、count 等信息的字典
        """
        return self.build_index(source_dir)

    def load_index(self) -> bool:
        """
        加载已存在的 Chroma 索引
        
        Returns:
            加载成功返回 True
        """
        if not os.path.exists(self.persist_directory):
            return False

        if not self.ai_client:
            raise ValueError("需要提供 AI 客户端")

        try:
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.ai_client.embeddings,
                collection_name=self.collection_name
            )
            count = self.vector_store._collection.count()
            print(f"Chroma 索引加载成功，共 {count} 个向量")
            return count > 0
        except Exception as e:
            print(f"加载索引失败: {e}")
            return False

    def load_vector_store(self) -> bool:
        """
        加载已存在的向量存储（兼容原有接口）
        
        Returns:
            加载成功返回 True，失败返回 False
        """
        return self.load_index()

    def _load_and_embed_documents(self, source_dir: str) -> bool:
        """
        从目录加载文档并向量化
        
        Args:
            source_dir: 源文件目录路径
            
        Returns:
            向量化成功返回 True，失败返回 False
        """
        # 使用基类的通用方法加载和分割文档
        split_docs = self._load_and_split_documents(source_dir)
        if split_docs is None:
            return False

        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            self.vector_store = Chroma.from_documents(
                documents=split_docs,
                embedding=self.ai_client.embeddings,
                persist_directory=self.persist_directory,
                collection_name=self.collection_name
            )
            self.persist()
            print(f"向量化完成，共生成 {self.vector_store._collection.count()} 个向量")
            return True
        except Exception as e:
            print(f"向量化失败: {e}")
            return False

    def add_documents(self, documents: List[Document]) -> bool:
        """
        添加文档到索引
        
        Args:
            documents: Document 对象列表
            
        Returns:
            添加成功返回 True
        """
        if not self.vector_store:
            print("索引未初始化")
            return False

        try:
            split_docs = self.text_splitter.split_documents(documents)
            self.vector_store.add_documents(split_docs)
            self.persist()
            return True
        except Exception as e:
            print(f"添加文档失败: {e}")
            return False

    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """
        相似度搜索（兼容原有接口）
        
        Args:
            query: 查询文本
            k: 返回的文档数量，默认 3
            
        Returns:
            匹配的 Document 对象列表
        """
        if not self.vector_store:
            raise ValueError("向量存储未初始化")
        return self.vector_store.similarity_search(query, k=k)

    def as_retriever(self, search_kwargs: Optional[Dict] = None):
        """
        转换为 LangChain 检索器（兼容原有接口）
        
        Args:
            search_kwargs: 检索参数，如 {"k": 3}
            
        Returns:
            LangChain Retriever 实例
        """
        if not self.vector_store:
            raise ValueError("向量存储未初始化")

        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs or {"k": 3}
        )

    def get_retriever(self, **kwargs):
        """
        获取 Chroma 检索器
        
        Returns:
            LangChain Retriever 实例
        """
        search_kwargs = kwargs.get("search_kwargs", {"k": 3})
        return self.as_retriever(search_kwargs)

    def persist(self) -> None:
        """
        持久化向量存储到磁盘（兼容原有接口）
        """
        if self.vector_store:
            self.vector_store.persist()

    def delete_collection(self) -> bool:
        """
        删除集合（兼容原有接口）
        
        Returns:
            删除成功返回 True，失败返回 False
        """
        try:
            if self.vector_store:
                self.vector_store.delete_collection()
                self.vector_store = None
            return True
        except Exception as e:
            print(f"删除集合失败: {e}")
            return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        获取集合统计信息
        
        Returns:
            统计信息字典
        """
        if not self.vector_store:
            return {"vector_count": 0}

        try:
            count = self.vector_store._collection.count()
            return {
                "vector_count": count,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {"vector_count": 0}

    def retrieve_knowledge(self, query: str) -> str:
        """
        从知识库检索相关知识（作为工具供 Agent 调用）
        
        Args:
            query: 查询文本
            
        Returns:
            检索到的知识内容
        """
        try:
            results = self.similarity_search(query, k=3)
            if not results:
                return "未找到相关知识"
            
            knowledge = "\n\n".join([doc.page_content for doc in results])
            return f"检索到的相关知识:\n{knowledge}"
        except Exception as e:
            return f"知识库检索失败: {str(e)}"

    def get_retrieve_knowledge_tool(self):
        """
        获取检索知识的工具（用于 Agent）
        
        Returns:
            LangChain Tool 实例
        """
        return StructuredTool.from_function(
            func=self.retrieve_knowledge,
            name="retrieve_knowledge",
            description="从知识库检索相关知识"
        )
