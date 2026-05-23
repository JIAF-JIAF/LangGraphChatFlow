"""
技能模块数据模型

定义技能相关的数据结构，供 loader、matcher、executor、tools 使用。
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class SkillInfo:
    """
    技能元数据

    表示技能的基本信息，用于列表展示和匹配
    """
    name: str
    description: str = ""
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
