"""
文档加载器工厂类
管理所有可用的文档加载器，支持注册和获取
"""

import os
from typing import Dict, List, Optional
from langchain_core.documents import Document


class DocumentLoaderFactory:
    """
    文档加载器工厂类
    
    管理所有可用的文档加载器，新的加载器通过 DocumentLoaderFactory.register_loader() 注册。
    """

    _loaders: Dict[str, type] = {}

    @classmethod
    def register_loader(cls, extension: str, loader_class: type) -> None:
        """
        注册文档加载器
        
        Args:
            extension: 文件扩展名，如 ".txt"、"pdf"
            loader_class: 继承自 BaseDocumentLoader 的加载器类
        """
        cls._loaders[extension.lower()] = loader_class

    @classmethod
    def get_loader(cls, file_path: str):
        """
        获取文件对应的加载器实例
        
        Args:
            file_path: 文件路径
            
        Returns:
            对应的加载器实例，不支持则返回 None
        """
        ext = os.path.splitext(file_path)[1].lower()
        loader_class = cls._loaders.get(ext)
        if loader_class:
            return loader_class(file_path)
        return None

    @classmethod
    def load(cls, file_path: str) -> List[Document]:
        """
        加载文档
        
        Args:
            file_path: 文件路径
            
        Returns:
            Document 对象列表，加载失败返回空列表
        """
        loader = cls.get_loader(file_path)
        if loader:
            return loader.load()
        return []

    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """
        获取支持的文档扩展名列表
        
        Returns:
            支持的扩展名列表
        """
        return list(cls._loaders.keys())


class BaseDocumentLoader:
    """
    文档加载器基类
    """

    def __init__(self, file_path: str):
        """
        初始化加载器
        
        Args:
            file_path: 文件路径
        """
        self.file_path = file_path

    def load(self) -> List[Document]:
        """
        加载文档
        
        Returns:
            Document 对象列表
        """
        raise NotImplementedError


__all__ = ['DocumentLoaderFactory', 'BaseDocumentLoader']