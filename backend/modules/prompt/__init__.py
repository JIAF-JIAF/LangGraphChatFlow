"""
Prompt 模块
定义客服系统的提示模板
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.example_selectors import LengthBasedExampleSelector

from modules.logger import log


DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "prompt_config.json"


def _load_prompt_config() -> Dict[str, Any]:
    """
    从配置文件加载 Prompt 配置
    
    支持通过环境变量 PROMPT_CONFIG_PATH 指定配置路径
    如果未指定，使用默认路径 backend/config/prompt_config.json
    
    Returns:
        配置字典
    """
    config_path = os.environ.get("PROMPT_CONFIG_PATH", str(DEFAULT_CONFIG_PATH))
    config_path = Path(config_path)
    
    if not config_path.is_absolute():
        config_path = Path(__file__).parent.parent.parent / config_path
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Prompt 配置文件不存在: {config_path}\n"
            f"请确保配置文件存在，或通过环境变量 PROMPT_CONFIG_PATH 指定正确的路径"
        )
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    log(f"已从配置文件加载: {config_path}", "Prompt")
    return config


_PROMPT_CONFIG: Optional[Dict[str, Any]] = None


def get_prompt_config() -> Dict[str, Any]:
    """
    获取 Prompt 配置（单例模式）
    
    Returns:
        配置字典
    """
    global _PROMPT_CONFIG
    if _PROMPT_CONFIG is None:
        _PROMPT_CONFIG = _load_prompt_config()
    return _PROMPT_CONFIG


def reload_prompt_config() -> Dict[str, Any]:
    """
    重新加载 Prompt 配置
    
    用于运行时更新配置
    
    Returns:
        配置字典
    """
    global _PROMPT_CONFIG
    _PROMPT_CONFIG = _load_prompt_config()
    return _PROMPT_CONFIG


class PromptClass:
    """提示模板管理类"""

    def __init__(self, feeling: dict = None, examples: list = None):
        """
        初始化 PromptClass

        Args:
            feeling: 情绪对象，格式: {"feeling": "default", "score": 5}
            examples: FewShot 示例列表，格式: [{"user_query": "...", "assistant_response": "..."}, ...]
                      传 None 使用默认示例，传 [] 禁用示例
        """
        self.SystemPrompt = None
        self.Prompt = None
        self.feeling = feeling if feeling else {"feeling": "default", "score": 5}
        self.examples = examples

        config = get_prompt_config()
        
        self.MOODS = config.get("moods", {})
        self.SystemPrompt = config.get("system_prompt", "")
        
        self._default_examples = config.get("few_shot_examples", [])

    def _build_few_shot_system_prompt(self, system_prompt: str, max_length: int = 2048) -> str:
        """
        构建带有 FewShot 示例的系统提示文本

        Args:
            system_prompt: 基础系统提示文本
            max_length: 最大提示长度

        Returns:
            带有示例的系统提示文本字符串
        """
        examples = self.examples if self.examples is not None else self._default_examples
        
        if not examples:
            return system_prompt
        
        example_prompt = PromptTemplate(
            input_variables=["user_query", "assistant_response"],
            template="用户: {user_query}\n助手: {assistant_response}"
        )
        
        example_selector = LengthBasedExampleSelector(
            examples=examples,
            example_prompt=example_prompt,
            max_length=max_length
        )
        
        selected_examples = example_selector.select_examples({"input": ""})
        
        if selected_examples:
            examples_text = "\n\n".join([
                f"用户: {ex['user_query']}\n助手: {ex['assistant_response']}"
                for ex in selected_examples
            ])
            return f"{system_prompt}\n\n## 参考示例:\n{examples_text}"
        else:
            return system_prompt

    def Prompt_Structure(self):
        """
        构建提示模板

        Returns:
            ChatPromptTemplate 实例
        """
        feeling = self.feeling if self.feeling["feeling"] in self.MOODS else {"feeling": "default", "score": 5}
        log(f"feeling: {feeling}", "Prompt")

        system_prompt_with_date = self.SystemPrompt.format(
            current_date="{current_date}",
            feelScore="{feelScore}",
            role_set="{role_set}"
        )

        system_prompt = self._build_few_shot_system_prompt(system_prompt_with_date)

        self.Prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        return self.Prompt

    def get_role_set(self, feeling: str = None) -> str:
        """
        根据情绪获取角色描述文本

        Args:
            feeling: 情绪类型，如果为 None 则使用当前的 feeling

        Returns:
            角色描述文本
        """
        feeling = feeling if feeling else self.feeling.get("feeling", "default")
        return self.MOODS.get(feeling, self.MOODS.get("default", {})).get("roleSet", "")


def create_prompt(feeling: dict = None, examples: list = None):
    """
    创建提示模板（便捷函数）

    Args:
        feeling: 情绪对象，格式: {"feeling": "default", "score": 5}
        examples: FewShot 示例列表，传 None 使用默认示例，传 [] 禁用示例

    Returns:
        ChatPromptTemplate 实例
    """
    prompt_class = PromptClass(feeling=feeling, examples=examples)
    return prompt_class.Prompt_Structure()


def get_role_set_from_feeling(feeling_type: str) -> str:
    """
    根据情绪类型获取角色描述文本（便捷函数）

    Args:
        feeling_type: 情绪类型字符串，如 "default", "upbeat", "angry", "cheerful", "depressed", "friendly"

    Returns:
        角色描述文本
    """
    prompt_class = PromptClass()
    return prompt_class.get_role_set(feeling_type)


__all__ = [
    'PromptClass',
    'create_prompt',
    'get_role_set_from_feeling',
    'get_prompt_config',
    'reload_prompt_config',
]
