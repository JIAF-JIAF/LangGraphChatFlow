"""
RAG 工具封装

将 RAGWorkflow 封装为 LangChain @tool，供 RAG Subgraph 内部使用。

对照现有 RAGExecutor.execute()：
  1. switch_knowledge_base(kb_name)
  2. retrieve(query) -> List[Document]
  3. generate(query, documents) -> Dict[str, Any]  (含 success, answer, error)

封装后：
  knowledge_search(query, kb_name)  — 步骤 1+2：切换知识库 + 检索
  knowledge_generate(query, context) — 步骤 3：基于检索结果生成回答
"""

from typing import List
from langchain_core.tools import tool
from langchain_core.documents import Document
from modules.rag import RAGWorkflow
from modules.logger import log


def create_rag_tools(rag_workflow: RAGWorkflow) -> List:
    """将 RAGWorkflow 封装为 LangChain @tool

    Args:
        rag_workflow: RAGWorkflow 实例

    Returns:
        [knowledge_search, knowledge_generate] 工具列表
    """

    @tool
    def knowledge_search(query: str, kb_name: str = "") -> str:
        """从知识库中检索相关文档。当用户的问题需要查找知识库中的信息时使用。

        Args:
            query: 搜索查询
            kb_name: 知识库名称（可选，默认使用当前知识库）
        """
        if kb_name:
            rag_workflow.switch_knowledge_base(kb_name)

        documents: List[Document] = rag_workflow.retrieve(query)
        if not documents:
            return "未在知识库中找到相关信息。"

        log(f"[RAGTool] 检索到 {len(documents)} 个文档", "MultiAgent")
        return "\n\n".join(
            f"[文档{i+1}] {doc.page_content[:500]}"
            for i, doc in enumerate(documents)
        )

    @tool
    def knowledge_generate(query: str, context: str) -> str:
        """基于检索到的知识库内容生成回答。需要先使用 knowledge_search 获取上下文。

        Args:
            query: 用户问题
            context: 从 knowledge_search 获得的检索结果
        """
        log("[RAGTool] 基于检索结果生成回答", "MultiAgent")
        result = rag_workflow.generate(query, [Document(page_content=context)])
        if result.get("success"):
            return result.get("answer", "生成失败")
        return result.get("error", "生成失败")

    return [knowledge_search, knowledge_generate]
