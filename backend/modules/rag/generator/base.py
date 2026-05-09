"""
生成模块基类

定义生成器的通用接口，提供空方法实现作为默认行为。
子类可覆盖这些方法实现具体的生成策略。

生成器负责将用户查询与检索到的文档结合，调用大语言模型生成最终回答。
支持多种生成策略：
- Stuff：将所有文档直接拼接进提示词
- Map-Reduce：先分别处理每个文档，再合并结果
- Refine：迭代式地完善回答

核心职责：
1. 构建提示模板（_build_prompt）
2. 执行生成逻辑（generate）
"""

from typing import List, Optional, Dict, Any
from langchain_core.documents import Document


class BaseGenerator:
    """
    生成器基类
    
    定义生成器的通用接口，提供空方法实现作为默认行为。
    子类可覆盖这些方法实现具体的生成策略。
    
    属性：
        llm_client: LLM 客户端实例，用于调用大语言模型
        config: 配置字典，包含提示词模板、温度等参数
        prompt_template: 构建好的提示模板
    
    方法：
        _build_prompt(): 构建提示模板
        generate(query, documents): 生成回答
    """

    def __init__(self, llm_client=None, config: Optional[Dict] = None):
        """
        初始化生成器
        
        Args:
            llm_client: LLM 客户端实例
            config: 配置参数（可选）
        """
        self.llm_client = llm_client
        self.config = config or {}
        self.prompt_template = self._build_prompt()

    def _build_prompt(self):
        """
        构建提示模板
        
        默认返回 None，子类需覆盖此方法实现具体的提示模板。
        
        Returns:
            提示模板实例，默认返回 None
        """
        print("[WARN] BaseGenerator._build_prompt: 使用基类默认实现（未实现具体逻辑）")
        return None

    def generate(self, query: str, documents: List[Document]) -> str:
        """
        生成回答
        
        默认返回空字符串，子类需覆盖此方法实现具体的生成逻辑。
        
        Args:
            query: 用户查询文本
            documents: 检索到的文档列表
            
        Returns:
            生成的回答文本，默认返回空字符串
        """
        print("[WARN] BaseGenerator.generate: 使用基类默认实现（未实现具体逻辑）")
        return ""
