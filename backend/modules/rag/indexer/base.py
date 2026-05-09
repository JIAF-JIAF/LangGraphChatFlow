"""
索引模块基类

定义索引器的通用接口，提供空方法实现作为默认行为。
子类可覆盖这些方法实现具体的向量存储方案。

索引器负责文档的加载、切分、向量化和存储，是 RAG 系统的基础组件。

核心职责：
1. 构建索引（build_index）：从源目录加载文档并创建向量索引
2. 加载索引（load_index）：加载已存在的索引
3. 添加文档（add_documents）：向已有索引中添加新文档
4. 获取检索器（get_retriever）：获取对应的检索器实例

支持的向量数据库：
- Chroma（本地轻量级）
- Milvus（企业级向量数据库）
"""

import os
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from modules.document_loaders import DocumentLoaderFactory


class BaseIndexer:
    """
    索引器基类
    
    定义索引器的通用接口，提供空方法实现作为默认行为。
    子类可覆盖这些方法实现具体的向量存储方案。
    
    属性：
        ai_client: AI 客户端实例，用于调用嵌入模型
        config: 配置字典
        text_splitter: 文本分割器，用于将长文档切分为片段
    """

    def __init__(self, ai_client=None, config: Optional[Dict] = None):
        """
        初始化索引器
        
        Args:
            ai_client: AI 客户端实例（用于嵌入）
            config: 配置参数（可选）
        """
        self.ai_client = ai_client
        self.config = config or {}
        
        # 默认文本分割器配置
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.get("chunk_size", 500),
            chunk_overlap=self.config.get("chunk_overlap", 50),
            length_function=len,
            add_start_index=True
        )

    def build_index(self, source_dir: str = "knowledge_base") -> Dict[str, Any]:
        """
        构建索引
        
        默认返回错误状态，子类需覆盖此方法实现具体的索引构建逻辑。
        
        Args:
            source_dir: 源文档目录路径
            
        Returns:
            索引构建结果字典，包含 status、message、count 等信息
        """
        print("[WARN] BaseIndexer.build_index: 使用基类默认实现（未实现具体逻辑）")
        return {"status": "error", "message": "索引器未实现"}

    def load_index(self) -> bool:
        """
        加载已存在的索引
        
        默认返回 False，子类需覆盖此方法实现具体的索引加载逻辑。
        
        Returns:
            加载成功返回 True，失败返回 False，默认返回 False
        """
        print("[WARN] BaseIndexer.load_index: 使用基类默认实现（未实现具体逻辑）")
        return False

    def add_documents(self, documents: List[Document]) -> bool:
        """
        添加文档到索引
        
        默认返回 False，子类需覆盖此方法实现具体的文档添加逻辑。
        
        Args:
            documents: Document 对象列表
            
        Returns:
            添加成功返回 True，失败返回 False，默认返回 False
        """
        print("[WARN] BaseIndexer.add_documents: 使用基类默认实现（未实现具体逻辑）")
        return False

    def get_retriever(self, **kwargs):
        """
        获取检索器
        
        默认返回 None，子类需覆盖此方法返回对应的检索器实例。
        
        Args:
            kwargs: 检索参数
            
        Returns:
            检索器实例，默认返回 None
        """
        print("[WARN] BaseIndexer.get_retriever: 使用基类默认实现（未实现具体逻辑）")
        return None

    def _load_and_split_documents(self, source_dir: str) -> Optional[List[Document]]:
        """
        从目录加载文档并分割（通用方法）
        
        Args:
            source_dir: 源文件目录路径
            
        Returns:
            分割后的 Document 列表，失败返回 None
        """
        if not os.path.exists(source_dir):
            print(f"源目录不存在: {source_dir}")
            return None

        documents = []
        for filename in os.listdir(source_dir):
            file_path = os.path.join(source_dir, filename)
            if os.path.isfile(file_path):
                docs = DocumentLoaderFactory.load(file_path)
                if docs:
                    documents.extend(docs)
                    print(f"加载文档: {filename}")

        if not documents:
            print("未找到可加载的文档")
            return None

        split_docs = self.text_splitter.split_documents(documents)
        print(f"文档分割完成，共 {len(split_docs)} 个片段")
        
        return split_docs
