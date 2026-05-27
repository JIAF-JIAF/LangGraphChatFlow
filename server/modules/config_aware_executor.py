"""
Config-Aware AgentExecutor

解决 langchain_classic 中 AgentExecutor 不传递 config 给工具的问题。

问题根源：
- langchain_classic 的 AgentExecutor._perform_agent_action() 调用 tool.run() 时
  没有传递 config 参数
- 导致工具无法从 RunnableConfig.configurable 获取 skill_name 等配置

解决方案：
- 重写 _perform_agent_action 方法，在调用 tool.run() 时传递 config
- 重写 invoke 方法，保存 config 供 _perform_agent_action 使用
"""

from typing import Any, Dict, Optional
from langchain_core.runnables import RunnableConfig, ensure_config
from langchain_core.agents import AgentAction, AgentStep
from langchain_core.callbacks import CallbackManagerForChainRun
from langchain_core.tools import BaseTool
from langchain_core.utils.input import get_color_mapping
from langchain_classic.agents import AgentExecutor
from langchain_classic.agents.tools import InvalidTool

from modules.logger import log


class ConfigAwareAgentExecutor(AgentExecutor):
    """
    支持 config 传递的 AgentExecutor
    
    重写 _perform_agent_action 方法，确保 config 正确传递给工具。
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_config: Optional[RunnableConfig] = None

    def invoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        重写 invoke 方法，保存 config 供后续使用
        
        Args:
            input: 输入数据
            config: 运行时配置（包含 configurable 中的 skill_name 等）
            **kwargs: 其他参数
        """
        config = ensure_config(config)
        self._current_config = config
        
        log(f"[ConfigAwareAgentExecutor] invoke 接收到 config: {config}", module="Agent")
        
        return super().invoke(input, config=config, **kwargs)

    def _perform_agent_action(
        self,
        name_to_tool_map: Dict[str, BaseTool],
        color_mapping: Dict[str, str],
        agent_action: AgentAction,
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> AgentStep:
        """
        重写 _perform_agent_action 方法，传递 config 给工具
        
        这是关键修复：在调用 tool.run() 时传递 config 参数，
        让工具能够从 config.configurable 获取 skill_name 等配置。
        """
        if run_manager:
            run_manager.on_agent_action(agent_action, color="green")
        
        if agent_action.tool in name_to_tool_map:
            tool = name_to_tool_map[agent_action.tool]
            return_direct = tool.return_direct
            color = color_mapping[agent_action.tool]
            tool_run_kwargs = self.agent.tool_run_logging_kwargs()
            
            if return_direct:
                tool_run_kwargs["llm_prefix"] = ""
            
            log(
                f"[ConfigAwareAgentExecutor] 调用工具: {tool.name}, "
                f"config={self._current_config}",
                module="Agent"
            )
            
            observation = tool.run(
                agent_action.tool_input,
                verbose=self.verbose,
                color=color,
                callbacks=run_manager.get_child() if run_manager else None,
                config=self._current_config,
                **tool_run_kwargs,
            )
        else:
            tool_run_kwargs = self.agent.tool_run_logging_kwargs()
            observation = InvalidTool().run(
                {
                    "requested_tool_name": agent_action.tool,
                    "available_tool_names": list(name_to_tool_map.keys()),
                },
                verbose=self.verbose,
                color=None,
                callbacks=run_manager.get_child() if run_manager else None,
                **tool_run_kwargs,
            )
        
        return AgentStep(action=agent_action, observation=observation)


__all__ = ["ConfigAwareAgentExecutor"]