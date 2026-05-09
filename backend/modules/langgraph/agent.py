"""
LangGraph Agent 实现（渐进式迁移版本）

将现有的 LangChain Agent 封装到 LangGraph 的节点中，
保持原有逻辑不变，逐步迁移到 LangGraph。
"""

import time
from typing import Optional, Dict, Any, List
from langgraph.graph import StateGraph, END, START

from .state import AgentState


class LangGraphAgent:
    """
    基于 LangGraph 的 Agent 实现（渐进式迁移）

    使用 LangGraph 的 StateGraph 来定义 Agent 工作流，
    将现有的 LangChain Agent 封装到节点中执行。
    """

    def __init__(
        self,
        llm_client: Any = None,
        tools: Optional[List[Any]] = None,
        prompt: Optional[Any] = None,
        langchain_agent: Optional[Any] = None,
        checkpointer: Optional[Any] = None,
        verbose: bool = True
    ):
        """
        初始化 LangGraph Agent

        Args:
            llm_client: LLM 客户端（可选，当没有 langchain_agent 时使用）
            tools: 工具列表（可选）
            prompt: 提示词模板（可选）
            langchain_agent: 现有的 LangChain Agent 实例（渐进式迁移使用）
            checkpointer: 状态持久化检查点（可选）
            verbose: 是否输出详细日志（默认 True）
        """
        self.llm_client = llm_client
        self._tools = tools or []
        self.prompt = prompt
        self._langchain_agent = langchain_agent  # 封装的 LangChain Agent
        self._checkpointer = checkpointer
        self._verbose = verbose  # 日志开关
        self._graph = None
        self._build_graph()

    def _log(self, message: str, level: str = "INFO"):
        """
        输出日志

        Args:
            message: 日志消息
            level: 日志级别（INFO, DEBUG, WARNING, ERROR）
        """
        if self._verbose:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [LangGraph] [{level}] {message}", flush=True)

    def _call_model(self, state: AgentState) -> Dict[str, Any]:
        """
        调用模型节点

        如果有封装的 LangChain Agent，则调用它；
        否则直接调用 LLM。

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        input_text = state["input"]
        session_id = state.get("session_id", "default")

        # 输出节点执行日志
        self._log(f"[节点: agent] 开始执行", "DEBUG")
        self._log(f"[节点: agent] 会话ID: {session_id}", "DEBUG")
        self._log(f"[节点: agent] 输入: {input_text[:100]}..." if len(input_text) > 100 else f"[节点: agent] 输入: {input_text}", "DEBUG")

        # 如果有封装的 LangChain Agent，优先调用它
        if self._langchain_agent:
            self._log(f"[节点: agent] 调用封装的 LangChain Agent", "DEBUG")
            result = self._langchain_agent.process_message(session_id, input_text)
            
            output = result.get("content", "")
            self._log(f"[节点: agent] 执行完成输出: {output[:100]}..." if len(output) > 100 else f"[节点: agent] 输出: {output}", "DEBUG")
            
            return {
                "output": output,
                "intermediate_steps": [],
                "tool_messages": result.get("tool_calls", [])
            }

        # 否则直接调用 LLM
        self._log(f"[节点: agent] 直接调用 LLM 客户端", "DEBUG")
        from langchain_core.messages import HumanMessage

        messages = state.get("chat_history", [])
        messages.append(HumanMessage(content=input_text))

        response = self.llm_client.chat(messages)
        output = response.content if hasattr(response, 'content') else str(response)

        self._log(f"[节点: agent] 执行完成输出: {output[:100]}..." if len(output) > 100 else f"[节点: agent] 输出: {output}", "DEBUG")

        return {
            "output": output,
            "intermediate_steps": [],
            "tool_messages": []
        }

    def _build_graph(self):
        """
        构建状态图（简化版）

        工作流:
        START -> agent -> END

        工具调用逻辑暂时在 LangChain Agent 内部处理。
        """
        self._log("开始构建 LangGraph 状态图", "INFO")
        self._graph = StateGraph(AgentState)

        # 添加 agent 节点
        self._graph.add_node("agent", self._call_model)

        # 设置入口和出口
        self._graph.set_entry_point("agent")
        self._graph.add_edge("agent", END)

        # 编译图
        self._graph = self._graph.compile(checkpointer=self._checkpointer)
        self._log("LangGraph 状态图构建完成", "INFO")

    def invoke(self, input: str, session_id: str = "default") -> Dict[str, Any]:
        """
        执行 Agent 处理用户输入

        Args:
            input: 用户输入
            session_id: 会话 ID

        Returns:
            包含 answer、intermediate_steps 和 tool_messages 的字典
        """
        self._log(f"=== 开始处理请求 ===", "INFO")
        self._log(f"会话ID: {session_id}", "INFO")
        self._log(f"用户输入: {input}", "INFO")

        result = self._graph.invoke(
            {
                "input": input,
                "chat_history": [],
                "output": "",
                "intermediate_steps": [],
                "tool_messages": []
            },
            config={"configurable": {"thread_id": session_id}}
        )

        self._log(f"=== 请求处理完成 ===", "INFO")

        return {
            "answer": result.get("output", ""),
            "intermediate_steps": result.get("intermediate_steps", []),
            "tool_messages": result.get("tool_messages", [])
        }

    def process_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """
        处理消息（兼容原有接口）

        Args:
            session_id: 会话 ID
            user_message: 用户消息

        Returns:
            包含 content 和 tool_calls 的字典
        """
        result = self.invoke(user_message, session_id)
        return {
            "content": result["answer"],
            "tool_calls": []
        }

    def get_graph(self):
        """
        获取编译后的图

        Returns:
            CompiledStateGraph
        """
        return self._graph
