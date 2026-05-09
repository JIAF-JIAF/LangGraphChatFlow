"""
生成模块
负责基于检索到的文档生成最终回答
"""

from .base import BaseGenerator
from .stuff import StuffGenerator
from .map_reduce import MapReduceGenerator
from .refine import RefineGenerator

__all__ = [
    'BaseGenerator',
    'StuffGenerator',
    'MapReduceGenerator',
    'RefineGenerator'
]
