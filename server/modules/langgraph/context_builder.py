"""
上下文构建器

负责将各种上下文信息（RAG 文档、对话历史等）格式化为 Agent 可用的 prompt 内容。
LangGraph 调度层只负责流程编排，具体的上下文构建逻辑由本模块提供。
"""

from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage


class ContextBuilder:
    """
    上下文构建器
    
    提供模块化的上下文构建能力，将 RAG 文档、对话历史等格式化为 prompt 内容。
    """
    
    TASK_CONSTRAINT = "\n\n【重要约束】这是计划执行模式，你必须独立完成此任务，不得向用户追问信息，不得调用任何工具。如果任务需要用户提供额外信息才能完成，请基于已有信息自行推断并完成。当上下文中已经提供了参考文档时，请直接基于文档内容回答，不要尝试查找或调用其他工具。"
    
    @staticmethod
    def build_rag_context(
        documents: List[Document],
        max_docs: int = 3,
        max_content_length: int = 1000,
        include_instruction: bool = True
    ) -> str:
        """
        构建 RAG 文档上下文
        
        Args:
            documents: RAG 检索到的文档列表
            max_docs: 最大文档数量
            max_content_length: 每个文档的最大内容长度
            include_instruction: 是否包含使用指令
            
        Returns:
            格式化后的上下文字符串，如果无文档则返回空字符串
        """
        if not documents:
            return ""
        
        selected_docs = documents[:max_docs]
        
        doc_parts = []
        for i, doc in enumerate(selected_docs):
            content = doc.page_content[:max_content_length] if doc.page_content else ""
            source = doc.metadata.get("source", "未知来源")
            doc_parts.append(f"【参考文档{i+1}】(来源: {source})\n{content}")
        
        doc_contents = "\n\n".join(doc_parts)
        
        if include_instruction:
            return f"\n\n【RAG检索到的参考文档】\n{doc_contents}\n\n请参考以上文档内容完成任务。"
        else:
            return f"\n\n【RAG检索到的参考文档】\n{doc_contents}"
    
    @staticmethod
    def build_task_prompt(task_description: str, include_constraint: bool = True) -> str:
        """
        构建任务 prompt
        
        Args:
            task_description: 任务描述
            include_constraint: 是否包含执行约束
            
        Returns:
            格式化后的任务 prompt
        """
        if include_constraint:
            return f"请完成以下任务：\n{task_description}{ContextBuilder.TASK_CONSTRAINT}"
        return f"请完成以下任务：\n{task_description}"
    
    @staticmethod
    def build_task_with_context(
        task_description: str,
        documents: Optional[List[Document]] = None,
        include_constraint: bool = True,
        include_rag_instruction: bool = True
    ) -> str:
        """
        构建带上下文的任务描述
        
        Args:
            task_description: 原始任务描述
            documents: RAG 文档列表（可选）
            include_constraint: 是否包含执行约束
            include_rag_instruction: 是否包含 RAG 使用指令
            
        Returns:
            增强后的任务描述
        """
        enhanced_task = ContextBuilder.build_task_prompt(task_description, include_constraint)
        
        if documents:
            rag_context = ContextBuilder.build_rag_context(
                documents,
                include_instruction=include_rag_instruction
            )
            enhanced_task = enhanced_task + rag_context
        
        return enhanced_task
    
    @staticmethod
    def build_chat_history(query: str, answer: str) -> List:
        """
        构建对话历史增量
        
        Args:
            query: 用户查询
            answer: AI 回答
            
        Returns:
            包含 HumanMessage 和 AIMessage 的列表
        """
        return [
            HumanMessage(content=query),
            AIMessage(content=answer)
        ]


__all__ = ["ContextBuilder"]
