"""
LangChain Agent 模块
结合 LLM + Tools 的 Agent 实现
"""

from typing import Optional, Dict, Any, List
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor


class Agent:
    """LangChain Agent 封装"""

    def __init__(
        self,
        options: Optional[Dict] = None,
        config_path: str = "config.json"
    ):
        if options is None:
            options = {}

        self.llm_client = options.get('aiClient')
        self._tools = options.get('tools', [])
        self.prompt = options.get('prompt')

        self.verbose = True
        self._chat_history_store: Dict[str, InMemoryChatMessageHistory] = {}

        self._build_agent()

    def _get_chat_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """获取或创建会话历史。

        Args:
            session_id: 会话 ID

        Returns:
            对应会话 ID 的聊天历史记录对象
        """
        if session_id not in self._chat_history_store:
            self._chat_history_store[session_id] = InMemoryChatMessageHistory()
        return self._chat_history_store[session_id]

    def _build_agent(self):
        """构建 Agent。

        使用 create_tool_calling_agent 创建 agent，
        并配置 RunnableWithMessageHistory 以支持多会话对话历史管理。
        """
        tools = self._tools.copy()

        self._agent = create_tool_calling_agent(
            llm=self.llm_client.chat,
            tools=tools,
            prompt=self.prompt
        )

        self._agent_executor = AgentExecutor(
            agent=self._agent,
            tools=tools,
            verbose=self.verbose,
            handle_parsing_errors=True
        )

        self._agent_chain = RunnableWithMessageHistory(
            self._agent_executor,
            self._get_chat_history,
            input_messages_key="input",
            history_messages_key="chat_history"
        )

    def invoke(self, input: str, session_id: str = "default") -> Dict[str, Any]:
        """执行 Agent 处理用户输入。

        Args:
            input: 用户输入的文本
            session_id: 会话 ID，用于管理对话历史，默认 "default"

        Returns:
            包含 answer、intermediate_steps 和 tool_messages 的字典
        """
        result = self._agent_chain.invoke(
            {"input": input},
            config={"configurable": {"session_id": session_id}}
        )

        return {
            "answer": result["output"] if hasattr(result, 'output') else str(result),
            "intermediate_steps": result.get("intermediate_steps", []),
            "tool_messages": []
        }

    def process_message(self, session_id, user_message):
        """发送对话（兼容原有接口）。

        Args:
            session_id: 会话 ID
            user_message: 用户消息内容

        Returns:
            包含 content 和 tool_calls 的字典
        """
        print(f"\n[Agent] 收到消息 - Session: {session_id}, Message: {user_message}", flush=True)
        result = self.invoke(user_message, session_id)
        return {
            "content": result["answer"],
            "tool_calls": []
        }


__all__ = ['Agent']
