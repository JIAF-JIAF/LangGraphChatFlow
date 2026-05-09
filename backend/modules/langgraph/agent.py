"""
LangGraph Agent 实现

标准 LangGraph RAG 流程：
START → router → ┌── 需要检索 ──→ retrieve → generate → END
                  │
                  └── 不需要检索 ──→ call_model → END
"""

import time
from typing import Optional, Dict, Any, List, Literal
from langgraph.graph import StateGraph, END, START
from langchain_core.documents import Document

from .state import AgentState


class LangGraphAgent:
    """
    LangGraph Agent

    纯调度层：
    - 调用 RAGWorkflow 处理检索逻辑
    - 调用 LangChainAgent 处理对话逻辑
    """

    def __init__(
        self,
        llm_client: Any = None,
        tools: Optional[List[Any]] = None,
        prompt: Optional[Any] = None,
        langchain_agent: Optional[Any] = None,
        rag_workflow: Optional[Any] = None,
        checkpointer: Optional[Any] = None,
        verbose: bool = True
    ):
        """
        初始化 LangGraph Agent

        Args:
            llm_client: LLM 客户端实例
            tools: 可用工具列表（可选）
            prompt: 提示模板（可选）
            langchain_agent: LangChain Agent 实例，用于处理不需要检索的对话
            rag_workflow: RAGWorkflow 实例，用于处理检索逻辑
            checkpointer: 检查点实例，用于状态持久化（可选）
            verbose: 是否输出详细日志
        """
        self.llm_client = llm_client
        self._tools = tools or []
        self.prompt = prompt
        self._langchain_agent = langchain_agent  # 核心对话 Agent
        self._rag_workflow = rag_workflow        # RAG 业务模块
        self._checkpointer = checkpointer
        self._verbose = verbose
        self._graph = None
        self._build_graph()

    def _log(self, message: str, level: str = "INFO"):
        """
        输出日志

        Args:
            message: 日志消息
            level: 日志级别
        """
        if self._verbose:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [LangGraph] [{level}] {message}", flush=True)

    def _router_node(self, state: AgentState) -> AgentState:
        """
        路由节点：判断是否需要检索

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        query = state["query"]

        self._log(f"[节点: router] 开始执行查询: {query[:30]}...")

        if self._rag_workflow:
            need_retrieve = self._rag_workflow.should_retrieve(query)
            self._log(f"[节点: router] 决策: {'需要检索' if need_retrieve else '不需要检索'}")
        else:
            need_retrieve = False
            self._log(f"[节点: router] RAG 不可用，直接调用 Agent")

        return {"need_retrieve": need_retrieve}

    def _retrieve_node(self, state: AgentState) -> AgentState:
        """
        检索节点：执行检索

        Args:
            state: 当前状态

        Returns:
            更新后的状态（包含检索到的文档）
        """
        query = state["query"]

        self._log(f"[节点: retrieve] 开始执行")

        if self._rag_workflow:
            kb = self._rag_workflow.select_knowledge_base(query)
            self._rag_workflow.switch_knowledge_base(kb)
            documents = self._rag_workflow.retrieve(query)
            self._log(f"[节点: retrieve] 检索到 {len(documents)} 个文档")
        else:
            documents = []
            self._log(f"[节点: retrieve] RAG 不可用，返回空文档")

        return {"documents": documents}

    def _generate_node(self, state: AgentState) -> AgentState:
        """
        生成节点：基于检索结果生成回答

        Args:
            state: 当前状态

        Returns:
            更新后的状态（包含生成的回答）
        """
        query = state["query"]
        documents = state.get("documents", [])
        session_id = state.get("session_id", "default")

        self._log(f"[节点: generate] 开始执行文档数: {len(documents)}")

        if self._rag_workflow:
            answer = self._rag_workflow.generate(query, documents, session_id)
        else:
            answer = "RAG 服务不可用，请稍后重试"

        self._log(f"[节点: generate] 生成完成: {answer[:30]}...")

        return {"answer": answer}

    def _call_model_node(self, state: AgentState) -> AgentState:
        """
        调用模型节点：直接调用 LangChain Agent

        Args:
            state: 当前状态

        Returns:
            更新后的状态（包含 Agent 的回答）
        """
        query = state["query"]
        session_id = state.get("session_id", "default")

        self._log(f"[节点: call_model] 开始执行")

        if self._langchain_agent:
            result = self._langchain_agent.process_message(session_id, query)
            answer = result.get("content", "")
        else:
            answer = "Agent 服务不可用，请稍后重试"

        self._log(f"[节点: call_model] 执行完成: {answer[:30]}...")

        return {"answer": answer}

    def _should_retrieve(self, state: AgentState) -> Literal["retrieve", "call_model"]:
        """
        条件路由

        Args:
            state: 当前状态

        Returns:
            下一个节点名称
        """
        decision = "retrieve" if state.get("need_retrieve", False) else "call_model"
        self._log(f"[条件路由] 决策: {decision}")
        return decision

    def _build_graph(self):
        """
        构建状态图

        节点：
        - router: 路由节点
        - retrieve: 检索节点
        - generate: 生成节点
        - call_model: 调用 Agent 节点
        """
        self._log("开始构建 LangGraph 状态图...")

        self._graph = StateGraph(AgentState)

        self._graph.add_node("router", self._router_node)
        self._graph.add_node("retrieve", self._retrieve_node)
        self._graph.add_node("generate", self._generate_node)
        self._graph.add_node("call_model", self._call_model_node)

        self._graph.add_edge(START, "router")

        self._graph.add_conditional_edges(
            "router",
            self._should_retrieve,
            {"retrieve": "retrieve", "call_model": "call_model"}
        )

        self._graph.add_edge("retrieve", "generate")
        self._graph.add_edge("generate", END)
        self._graph.add_edge("call_model", END)

        self._graph = self._graph.compile(checkpointer=self._checkpointer)
        self._log("LangGraph 状态图构建完成")

    def invoke(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """
        执行 Agent

        Args:
            query: 用户查询
            session_id: 会话 ID

        Returns:
            包含 answer 的结果
        """
        self._log(f"=== 开始处理请求 ===")
        self._log(f"会话ID: {session_id}")
        self._log(f"用户查询: {query}")

        result = self._graph.invoke(
            {
                "query": query,
                "session_id": session_id,
                "need_retrieve": False,
                "documents": [],
                "answer": ""
            },
            config={"configurable": {"thread_id": session_id}}
        )

        self._log(f"=== 请求处理完成 ===")
        return {"answer": result.get("answer", "")}

    def process_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """
        处理消息（兼容接口）

        Args:
            session_id: 会话 ID
            user_message: 用户消息

        Returns:
            包含 content 和 tool_calls 的结果
        """
        result = self.invoke(user_message, session_id)
        return {"content": result["answer"], "tool_calls": []}

    def get_graph(self):
        """
        获取编译后的状态图

        Returns:
            编译后的图
        """
        return self._graph
