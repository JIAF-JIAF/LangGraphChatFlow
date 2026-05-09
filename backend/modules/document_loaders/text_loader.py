"""
TXT 文档加载器
"""

from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader

from .loader_factory import BaseDocumentLoader, DocumentLoaderFactory


class TextDocumentLoader(BaseDocumentLoader):
    """
    TXT 文档加载器
    """

    def load(self) -> List[Document]:
        """
        加载 TXT 文档
        
        Returns:
            Document 对象列表
        """
        try:
            loader = TextLoader(self.file_path, encoding='utf-8')
            return loader.load()
        except Exception as e:
            print(f"加载 TXT 文档失败: {e}")
            return []


DocumentLoaderFactory.register_loader(".txt", TextDocumentLoader)