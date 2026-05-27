"""
Stuff 生成器

采用直接拼接策略：将所有检索到的文档内容直接拼接进提示词，一次性发送给 LLM。

优点：
- 简单直接，实现成本低
- 上下文完整，LLM 可以看到所有相关信息
- 单次调用，响应速度快

缺点：
- 受限于 LLM 的上下文窗口大小
- 文档过多时可能超出 token 限制

适用于检索结果较少、单篇文档较短的场景，是最常用的生成策略。
"""

from typing import List
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from .base import BaseGenerator


class StuffGenerator(BaseGenerator):
    """
    Stuff 生成器
    
    将所有文档内容直接拼接进提示词，一次性生成回答。
    """

    def _build_prompt(self):
        """
        构建 Stuff 提示模板
        
        创建包含系统指令和上下文占位符的提示模板。
        
        Returns:
            ChatPromptTemplate 实例
        """
        system_prompt = """你是一个专业的知识问答助手。
        根据提供的参考文档，回答用户的问题。

        参考文档:
        {context}

        注意事项:
        - 优先使用参考文档中的信息
        - 如果文档中没有相关信息，说明"未找到相关知识"
        - 保持回答简洁准确"""

        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{query}")
        ])

    def generate(self, query: str, documents: List[Document]) -> str:
        """
        使用 Stuff 方式生成回答
        
        将所有文档内容拼接成上下文，构建完整提示词后调用 LLM。
        
        Args:
            query: 用户查询文本
            documents: 检索到的文档列表
            
        Returns:
            生成的回答文本
        """
        if not documents:
            return "未找到相关知识"

        context = "\n\n".join([doc.page_content for doc in documents])

        prompt = self.prompt_template.format(
            context=context,
            query=query
        )

        if self.llm_client and hasattr(self.llm_client, 'chat'):
            response = self.llm_client.chat.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        else:
            return "LLM 客户端未配置"
