"""
技能管理层（匹配器）：负责技能的匹配和查询
提供基于语义的技能匹配能力"""

from typing import Any, Dict, List, Optional

from .loader import SkillLoader
from .indexer import SkillIndexer
from modules.logger import log


class SkillMatcher:
    """
    技能匹配器
    负责根据用户查询匹配最合适的技能
    
    匹配策略：
    1. 语义检索：使用向量相似度匹配技能描述
    2. 关键词兜底：当语义检索无结果时，使用关键词匹配
    """

    def __init__(self, loader: SkillLoader, indexer: Optional[SkillIndexer] = None):
        """
        初始化技能匹配器

        Args:
            loader: 技能加载器实例
            indexer: 技能索引器实例（用于语义检索）
        """
        self._loader = loader
        self._indexer = indexer
        log("匹配器初始化完成", module="Skill.Matcher")

    def match_by_semantic(self, query: str, threshold: float = 1.5) -> Optional[Dict[str, Any]]:
        """
        基于语义相似度匹配技能

        Args:
            query: 用户查询文本
            threshold: 相似度阈值（距离越小越相似）

        Returns:
            Optional[Dict[str, Any]]: 匹配的技能，如果没有匹配返回 None
        """
        if not self._indexer or not self._indexer.is_indexed():
            log("语义索引不可用，跳过语义匹配", module="Skill.Matcher")
            return None

        log(f"语义匹配: {query[:50]}...", module="Skill.Matcher")
        
        results = self._indexer.search(query, k=3)
        
        if not results:
            log("语义检索无结果", module="Skill.Matcher")
            return None

        best_match = results[0]
        score = best_match.get("score", float("inf"))
        
        if score > threshold:
            log(f"最佳匹配分数 {score:.3f} 超过阈值 {threshold}，忽略", module="Skill.Matcher")
            return None

        skill_name = best_match.get("skill_name")
        log(f"语义匹配成功: {skill_name} (score={score:.3f})", module="Skill.Matcher")
        return self._loader.load_skill(skill_name)

    def match_by_keywords(self, query: str) -> Optional[Dict[str, Any]]:
        """
        基于关键词匹配技能（兜底策略）

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

        优先使用语义检索，失败则使用关键词匹配兜底。

        Args:
            query: 用户查询文本

        Returns:
            Optional[Dict[str, Any]]: 匹配的技能，如果没有匹配返回 None
        """
        matched = self.match_by_semantic(query)
        if matched:
            return matched

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
        
        stop_words = {"the", "a", "an", "is", "are", "be", "to", "of", "and", "for", "in", "on", "at", "with", "by", "from", "的", "了", "是", "在", "我", "你", "他", "她", "它"}
        important_tokens = [
            token for token in tokens 
            if token not in stop_words and len(token) >= 2
        ]
        
        return important_tokens

    def reload(self) -> None:
        """重新加载技能数据"""
        self._loader.reload()
        log("匹配器已重新加载", module="Skill.Matcher")
