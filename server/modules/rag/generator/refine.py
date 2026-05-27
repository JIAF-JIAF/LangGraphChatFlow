"""
Refine 生成器

采用迭代式生成策略：
1. 基于第一个文档生成初始回答
2. 依次用后续文档逐步完善和修正回答
3. 最终得到综合所有文档信息的回答

适用于需要深度分析和逐步完善的场景，能够处理复杂的多文档推理任务。

当前为预留接口，暂使用 Stuff 方式实现，后续可扩展完整的 Refine 逻辑。
"""

from typing import List
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from .base import BaseGenerator


class RefineGenerator(BaseGenerator):
    """
    Refine 生成器
    
    实现迭代式生成策略，逐步完善回答。
    
    属性：
        refine_prompt: Refine 阶段提示模板，用于基于新文档完善现有回答
    """

    def _build_prompt(self):
        """
        构建 Refine 提示模板
        
        创建用于迭代完善回答的提示模板，指导 LLM 基于新文档更新现有回答。
        
        Returns:
            ChatPromptTemplate 实例
        """
        self.refine_prompt = ChatPromptTemplate.from_messages([
            ("system", "根据新文档完善现有回答。\n\n现有回答: {current_answer}\n\n新文档: {document}"),
            ("human", "{query}")
        ])
        return self.refine_prompt

    def generate(self, query: str, documents: List[Document]) -> str:
        """
        使用 Refine 方式生成回答
        
        Args:
            query: 用户查询文本
            documents: 检索到的文档列表
            
        Returns:
            生成的回答文本
        """
        if not documents:
            return "未找到相关知识"

        # 暂未实现完整的 Refine，使用 Stuff 方式作为占位实现
        # 完整实现应包含：
        # 1. 基于第一个文档生成初始回答
        # 2. 依次用后续文档调用 LLM 完善回答
        context = "\n\n".join([doc.page_content for doc in documents])
        prompt = f"""根据提供的参考文档回答问题。

        参考文档:
        {context}

        问题: {query}

        请基于以上文档内容回答。"""

        if self.llm_client and hasattr(self.llm_client, 'chat'):
            response = self.llm_client.chat.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        else:
            return "LLM 客户端未配置"
