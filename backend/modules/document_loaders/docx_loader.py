"""
DOCX 文档加载器
"""

from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import UnstructuredWordDocumentLoader

from .loader_factory import BaseDocumentLoader, DocumentLoaderFactory


class DOCXDocumentLoader(BaseDocumentLoader):
    """
    DOCX 文档加载器
    """

    def load(self) -> List[Document]:
        """
        加载 DOCX 文档
        
        Returns:
            Document 对象列表
        """
        try:
            loader = UnstructuredWordDocumentLoader(self.file_path)
            return loader.load()
        except Exception as e:
            print(f"加载 DOCX 文档失败: {e}")
            return []


DocumentLoaderFactory.register_loader(".docx", DOCXDocumentLoader)