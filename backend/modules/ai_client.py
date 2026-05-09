"""
LangChain LLM 模块
封装 LangChain 的 ChatOpenAI 客户端
"""

import json
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_community.embeddings.dashscope import DashScopeEmbeddings
from openai import OpenAI

from .rate_limit import create_rate_limiter


class LLMClient:
    """LangChain LLM 客户端封装"""

    def __init__(
        self,
        config_path: Optional[str] = None,
        temperature: float = 0.7
    ):
        self.temperature = temperature
        self.config_path = config_path
        self._client = None  # ChatOpenAI
        self._embedding_client = None  # OpenAIEmbeddings
        self._openai_client = None  # OpenAI SDK 客户端

        if config_path:
            self._load_from_config()
        else:
            raise ValueError("请提供 API 密钥和 base_url 或配置文件路径")

        self._init_clients()

    def _load_from_config(self):
        """从配置文件加载 API 配置。

        从指定的配置文件路径读取 API 密钥、base_url 和 model 等配置。

        Raises:
            Exception: 读取或解析配置文件失败时抛出
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.api_key = config.get('api_key')
            self.base_url = config.get('base_url')
            self.model = config.get('model')
            
            # 解析限流配置
            # embedding_limit = self._parse_rate_limit_config(config)
            
            # 创建限流器
            # self._llm_rate_limiter = create_rate_limiter(llm_limit, max_bucket_size=10)
            # self._embedding_rate_limiter = create_rate_limiter(embedding_limit, max_bucket_size=20)
            
            print(f"从配置文件 {self.config_path} 读取 API 配置")
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            raise

    def _parse_rate_limit_config(self, config: dict) -> tuple[int, int]:
        """解析限流配置
        
        Args:
            config: 配置字典
            
        Returns:
            (llm_limit, embedding_limit) 元组
        """
        rate_limit_config = config.get("rate_limit", {})
        enabled = rate_limit_config.get("enabled", True)
        
        if enabled:
            llm_limit = rate_limit_config.get("llm_limit", 30)
            embedding_limit = rate_limit_config.get("embedding_limit", 100)
            print(f"LLM 限流已启用: {llm_limit} 次/分钟")
            print(f"Embedding 限流已启用: {embedding_limit} 次/分钟")
        else:
            # 禁用时设置很大的限流值（相当于无限流）
            llm_limit = 1000000  # 每分钟 100 万次
            embedding_limit = 1000000
            print("LLM/Embedding 限流已禁用")
        
        return llm_limit, embedding_limit

    def _init_clients(self):
        """初始化 LangChain ChatOpenAI 客户端。

        使用配置文件中的 model、api_key 和 base_url 创建 ChatOpenAI 实例。
        """
        # 初始化 LLM 客户端（直接挂 rate_limiter，统一接口）
        self._client = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=self.temperature,
            # rate_limiter=self._llm_rate_limiter,
        )
        
        # 初始化 Embedding 客户端（DashScope 专用）
        self._embedding_client = DashScopeEmbeddings(
            model="text-embedding-v3",
            dashscope_api_key=self.api_key,
        )
        
        # 初始化 OpenAI SDK 客户端（用于直接调用）
        self._openai_client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        print(f"LangChain LLM 客户端初始化成功 (model={self.model})")

    @property
    def chat(self):
        """获取 ChatOpenAI 客户端"""
        if self._client is None:
            raise RuntimeError("LLM client 未初始化")
        return self._client

    @property
    def embeddings(self):
        """获取 Embeddings 客户端"""
        if self._embedding_client is None:
            raise RuntimeError("Embedding client 未初始化")
        return self._embedding_client

    def create_embedding(self, text: str) -> list[float]:
        """创建文本嵌入向量。

        Args:
            text: 要嵌入的文本内容

        Returns:
            文本的嵌入向量表示，失败时返回空列表
        """
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            print(f"生成嵌入失败: {e}")
            return []


class AIClient(LLMClient):
    """兼容原有 AIClient 接口"""
    pass


__all__ = ['LLMClient', 'AIClient']
