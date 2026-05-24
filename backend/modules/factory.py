"""
系统组件初始化工厂
提供共享的 LangGraph Agent 初始化逻辑
"""

import os
from modules.ai_client import AIClient
from modules.langgraph import LangGraphAgent, TaskPlanner
from modules.rag import RAGWorkflow
from modules.checkpoint import CheckpointFactory
from modules.assistant import Agent as LangChainAgent
from modules.prompt import create_prompt
from modules.feeling import FeelingDetector
from modules.tools import ToolManager
from modules.logger import log


class AssistantFactory:
    """Assistant 实例工厂"""

    @staticmethod
    def create_assistant():
        """
        创建 Assistant 实例

        Returns:
            tuple: (assistant_instance, components_dict)
        """
        components = AssistantFactory._init_components()
        assistant = components['assistant']
        return assistant, components

    @staticmethod
    def _init_components():
        """初始化所有系统组件"""
        log("初始化 AI 客户端...", "Factory")
        ai_client = AIClient()
        log("AI 客户端初始化完成", "Factory")

        log("初始化 RAG 工作流...", "Factory")
        rag_workflow = AssistantFactory._try_init_rag_workflow(ai_client)
        log("RAG 工作流初始化完成", "Factory")

        log("初始化 LangChain Agent（含技能工具）...", "Factory")
        langchain_agent = AssistantFactory._try_init_langchain_agent(ai_client)
        log("LangChain Agent 初始化完成", "Factory")

        log("初始化 LangGraph 调度层...", "Factory")
        checkpointer, task_planner = AssistantFactory._init_langgraph_components(ai_client)
        feeling_detector = AssistantFactory._try_init_feeling_detector(ai_client)

        assistant = LangGraphAgent(
            agent=langchain_agent,
            rag_workflow=rag_workflow,
            checkpointer=checkpointer,
            feeling_detector=feeling_detector,
            task_planner=task_planner,
            verbose=True,
        )
        log("LangGraph 调度层初始化完成", "Factory")

        return {
            'assistant': assistant,
            'ai_client': ai_client,
            'feeling_detector': feeling_detector,
            'rag_workflow': rag_workflow,
            'langchain_agent': langchain_agent,
            'checkpointer': checkpointer,
            'task_planner': task_planner,
        }

    @staticmethod
    def _try_init_feeling_detector(ai_client):
        try:
            return FeelingDetector(llm_client=ai_client)
        except Exception as e:
            log("感情侦测器初始化失败: {}".format(e), "Factory")
            return None

    @staticmethod
    def _try_init_rag_workflow(ai_client):
        try:
            workflow = RAGWorkflow(llm_client=ai_client)
            workflow.build_index()
            return workflow
        except Exception as e:
            log("RAG 工作流初始化警告: {}".format(e), "Factory")
            return None

    @staticmethod
    def _try_init_langchain_agent(ai_client):
        try:
            # 使用工具管理器获取所有工具
            tool_manager = ToolManager(llm_client=ai_client)
            all_tools = tool_manager.get_all_tools()

            return LangChainAgent(options={
                "prompt": create_prompt(feeling={"feeling": "default", "score": 5}),
                "tools": all_tools,
                "aiClient": ai_client
            })
        except Exception as e:
            log("LangChain Agent 初始化失败: {}".format(e), "Factory")
            return None

    @staticmethod
    def _init_langgraph_components(ai_client):
        checkpoint_storage = os.getenv("CHECKPOINT_STORAGE", "memory").lower()
        checkpointer = CheckpointFactory.build(name=checkpoint_storage)
        task_planner = TaskPlanner(llm_client=ai_client)
        return checkpointer, task_planner


__all__ = ['AssistantFactory']
