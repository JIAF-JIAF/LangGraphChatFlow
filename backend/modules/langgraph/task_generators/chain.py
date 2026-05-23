"""
任务生成责任链工厂
"""

from .base import TaskGeneratorHandler
from .rag_refine_handler import RagRefineTaskGenerator
from .default_handler import DefaultTaskGenerator


class TaskGeneratorChain:
    """任务生成责任链工厂"""

    @staticmethod
    def build() -> TaskGeneratorHandler:
        """
        构建责任链

        新增处理器时，只需在此处插入新的处理器类

        Returns:
            责任链的第一个处理器
        """
        return RagRefineTaskGenerator(
            DefaultTaskGenerator()
        )
