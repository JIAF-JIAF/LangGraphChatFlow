"""
技能管理层（匹配器）
负责技能的匹配和查询

提供基于关键词和语义的技能匹配能力
"""

from typing import Any, Dict, List, Optional

from .loader import SkillLoader
from modules.logger import log


class SkillMatcher:
    """
    技能匹配器
    负责根据用户查询匹配最合适的技能
    
    匹配策略：
    1. 精确匹配：技能名称或描述中包含查询关键词
    2. 模糊匹配：查询关键词与技能信息的相似度匹配
    """

    def __init__(self, loader: SkillLoader):
        """
        初始化技能匹配器

        Args:
            loader: 技能加载器实例
        """
        self._loader = loader
        log("匹配器初始化完成", module="Skill.Matcher")

    def match_by_keywords(self, query: str) -> Optional[Dict[str, Any]]:
        """
        基于关键词匹配技能

        Args:
            query: 用户查询文本

        Returns:
            Optional[Dict[str, Any]]: 匹配的技能，如果没有匹配返回 None
        """
        log(f"关键词匹配: {query[:50]}...", module="Skill.Matcher")
        query_lower = query.lower()
        skills = self._loader.list_skills()
        
        important_tokens = self._extract_important_tokens(query_lower)
        
        for skill in skills:
            name = skill.get("name", "").lower()
            desc = skill.get("description", "").lower()
            
            if name in query_lower or any(token in desc for token in important_tokens):
                log(f"精确匹配成功: {skill['name']}", module="Skill.Matcher")
                return self._loader.load_skill(skill["name"])
        
        for skill in skills:
            name = skill.get("name", "").lower()
            desc = skill.get("description", "").lower()
            combined = f"{name} {desc}"
            
            for token in important_tokens:
                if len(token) >= 3 and token in combined:
                    log(f"模糊匹配成功: {skill['name']}", module="Skill.Matcher")
                    return self._loader.load_skill(skill["name"])
        
        log("未找到匹配技能", module="Skill.Matcher")
        return None

    def match_skill(self, query: str) -> Optional[Dict[str, Any]]:
        """
        根据查询匹配技能（主入口）

        Args:
            query: 用户查询文本

        Returns:
            Optional[Dict[str, Any]]: 匹配的技能，如果没有匹配返回 None
        """
        matched = self.match_by_keywords(query)
        if matched:
            return matched
        
        return None

    def _extract_important_tokens(self, query: str) -> List[str]:
        """
        从查询中提取重要词汇

        Args:
            query: 用户查询文本（已转为小写）

        Returns:
            List[str]: 重要词汇列表
        """
        tokens = query.split()
        
        stop_words = {"the", "a", "an", "is", "are", "be", "to", "of", "and", "for", "in", "on", "at", "with", "by", "from"}
        important_tokens = [
            token for token in tokens 
            if token not in stop_words and len(token) >= 2
        ]
        
        return important_tokens

    def reload(self) -> None:
        """重新加载技能数据"""
        self._loader.reload()
        log("匹配器已重新加载", module="Skill.Matcher")
