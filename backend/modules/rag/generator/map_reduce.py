"""
Map-Reduce 生成器

采用两阶段生成策略：
1. Map 阶段：对每个文档分别生成针对查询的回答
2. Reduce 阶段：将多个回答合并为一个综合回答

适用于文档数量较多或单篇文档过长的场景，可以有效控制单次提示词长度。

当前为预留接口，暂使用 Stuff 方式实现，后续可扩展完整的 Map-Reduce 逻辑。
"""

from typing import List
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from .base import BaseGenerator


class MapReduceGenerator(BaseGenerator):
    """
    Map-Reduce 生成器
    
    实现 Map-Reduce 生成策略，先分治处理每个文档，再合并结果。
    
    属性：
        map_prompt: Map 阶段提示模板，用于处理单个文档
        reduce_prompt: Reduce 阶段提示模板，用于合并多个回答
    """

    def _build_prompt(self):
        """
        构建 Map-Reduce 提示模板
        
        创建两个提示模板：
        - map_prompt：指导 LLM 基于单个文档回答问题
        - reduce_prompt：指导 LLM 合并多个回答
        
        Returns:
            ChatPromptTemplate 实例（map_prompt）
        """
        # Map 阶段提示：处理单个文档
        self.map_prompt = ChatPromptTemplate.from_messages([
            ("system", "根据以下文档，回答用户问题。只使用文档中的信息。\n\n文档: {document}"),
            ("human", "{query}")
        ])

        # Reduce 阶段提示：合并多个回答
        self.reduce_prompt = ChatPromptTemplate.from_messages([
            ("system", "将以下多个回答合并成一个综合回答。\n\n各个回答:\n{summaries}"),
            ("human", "{query}")
        ])

        return self.map_prompt

    def generate(self, query: str, documents: List[Document]) -> str:
        """
        使用 Map-Reduce 方式生成回答
        
        Args:
            query: 用户查询文本
            documents: 检索到的文档列表
            
        Returns:
            生成的回答文本
        """
        if not documents:
            return "未找到相关知识"

        # 暂未实现完整的 Map-Reduce，使用 Stuff 方式作为占位实现
        # 完整实现应包含：
        # 1. 遍历每个文档，调用 LLM 生成独立回答（Map）
        # 2. 收集所有回答，调用 LLM 合并（Reduce）
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
