"""
技能向量索引器

将技能元数据向量化存储，支持语义检索匹配。
复用 RAG 模块的 ChromaIndexer 基础设施。
"""

import os
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

from modules.rag.indexer import ChromaIndexer
from modules.logger import log, exception


class SkillIndexer:
    """
    技能向量索引器
    
    将技能的 name + description 向量化存储到 Chroma，
    支持基于语义相似度的技能匹配。
    
    使用独立的 collection "skills"，与知识库隔离。
    """

    COLLECTION_NAME = "skills"

    def __init__(self, ai_client=None):
        """
        初始化技能索引器
        
        Args:
            ai_client: AI 客户端（用于 embedding）
        """
        self._indexer = ChromaIndexer(
            ai_client=ai_client,
            collection_name=self.COLLECTION_NAME
        )
        self._indexed = False
        log("技能索引器初始化完成", module="Skill.Indexer")

    def index_skills(self, skills: List[Dict[str, Any]]) -> bool:
        """
        将技能列表向量化索引
        
        Args:
            skills: 技能元数据列表，每项包含 name, description 等
            
        Returns:
            索引成功返回 True
        """
        if not skills:
            log("技能列表为空，跳过索引", module="Skill.Indexer")
            return False

        try:
            ai_client = self._indexer.ai_client
            if not ai_client:
                log("ai_client 为 None，无法创建索引", module="Skill.Indexer")
                return False
            
            embeddings = getattr(ai_client, 'embeddings', None)
            if not embeddings:
                log("ai_client.embeddings 不存在，无法创建索引", module="Skill.Indexer")
                return False

            documents = []
            for skill in skills:
                name = skill.get("name", "")
                description = skill.get("description", "")
                
                content = f"{name}: {description}"
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "skill_name": name,
                        "description": description,
                        "version": skill.get("version", "1.0.0"),
                    }
                )
                documents.append(doc)

            persist_dir = os.getenv("CHROMA_PERSIST_DIRECTORY", "db/chroma")
            os.makedirs(persist_dir, exist_ok=True)

            self._indexer.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                persist_directory=persist_dir,
                collection_name=self.COLLECTION_NAME
            )
            self._indexer.persist()
            
            count = self._indexer.vector_store._collection.count()
            log(f"技能索引完成，共 {count} 个技能", module="Skill.Indexer")
            self._indexed = True
            return True

        except Exception as e:
            exception(f"技能索引失败: {e}", "Skill.Indexer", e)
            return False

    def load_index(self) -> bool:
        """
        加载已存在的技能索引
        
        Returns:
            加载成功返回 True
        """
        success = self._indexer.load_index()
        if success:
            self._indexed = True
            log("技能索引加载成功", module="Skill.Indexer")
        return success

    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        语义检索技能
        
        Args:
            query: 查询文本
            k: 返回数量
            
        Returns:
            匹配的技能列表，每项包含 skill_name, description, score
        """
        if not self._indexed:
            log("索引未初始化，尝试加载", module="Skill.Indexer")
            if not self.load_index():
                return []

        try:
            vector_store = self._indexer.vector_store
            if not vector_store:
                return []

            results = vector_store.similarity_search_with_score(query, k=k)
            skills = []
            for doc, score in results:
                skills.append({
                    "skill_name": doc.metadata.get("skill_name"),
                    "description": doc.metadata.get("description"),
                    "score": score,
                })
            log(f"语义检索返回 {len(skills)} 个技能", module="Skill.Indexer")
            return skills

        except Exception as e:
            exception(f"语义检索失败: {e}", "Skill.Indexer", e)
            return []

    def is_indexed(self) -> bool:
        """检查是否已索引"""
        return self._indexed

    def clear_index(self) -> bool:
        """
        清除技能索引
        
        Returns:
            清除成功返回 True
        """
        try:
            if self._indexer.vector_store:
                self._indexer.vector_store._collection.delete()
                self._indexed = False
                log("技能索引已清除", module="Skill.Indexer")
            return True
        except Exception as e:
            exception(f"清除索引失败: {e}", "Skill.Indexer", e)
            return False
