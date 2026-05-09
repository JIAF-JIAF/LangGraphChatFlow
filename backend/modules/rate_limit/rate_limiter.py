"""
限流模块
封装 Flask-Limiter，提供可配置的 API 限流功能
"""

import json
from functools import wraps
from typing import Optional, Any, Callable
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


class RateLimiter:
    """API 限流管理器
    
    基于 Flask-Limiter 实现，支持通过配置文件灵活配置限流规则。
    """

    def __init__(self, config_path: str = "config.json"):
        """初始化限流管理器。
        
        Args:
            config_path: 配置文件路径，默认为 "config.json"
        """
        self.config = self._load_config(config_path)
        self.limiter: Optional[Limiter] = None
        self.enabled = self.config.get("rate_limit", {}).get("enabled", True)
        
    def _load_config(self, config_path: str) -> dict:
        """从配置文件加载配置。
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典，加载失败时返回空字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}
    
    def _format_limit(self, limit_value: Any) -> Optional[str]:
        """格式化限流规则。
        
        将数字格式的限流值转换为 "X per minute" 格式字符串。
        
        Args:
            limit_value: 限流值，可以是 int、float 或 str
            
        Returns:
            格式化后的限流规则字符串
        """
        if isinstance(limit_value, (int, float)):
            return f"{int(limit_value)} per minute"
        return limit_value
    
    def init_app(self, app: Flask) -> Optional[Limiter]:
        """初始化 Flask 应用的限流功能。
        
        Args:
            app: Flask 应用实例
            
        Returns:
            初始化后的 Limiter 实例，限流禁用时返回 None
        """
        if not self.enabled:
            print("限流功能已禁用")
            return None
            
        rate_limit_config = self.config.get("rate_limit", {})
        
        storage_uri = rate_limit_config.get("storage_uri", "memory://")
        key_prefix = rate_limit_config.get("key_prefix", "langchain_chatflow")
        default_limit = self._format_limit(rate_limit_config.get("default_limit", 100))
        
        self.limiter = Limiter(
            get_remote_address,
            app=app,
            storage_uri=storage_uri,
            key_prefix=key_prefix,
            default_limits=[default_limit]
        )
        
        print(f"限流功能已启用: 默认限制 {default_limit}")
        return self.limiter
    
    def get_limit(self, limit_name: str) -> Optional[str]:
        """获取指定名称的限流规则。
        
        Args:
            limit_name: 限流规则名称，如 "chat_limit"、"start_limit"
            
        Returns:
            格式化后的限流规则字符串，限流禁用时返回 None
        """
        if not self.enabled:
            return None
        limit_value = self.config.get("rate_limit", {}).get(limit_name)
        return self._format_limit(limit_value)
    
    def limit(self, limit_name: str) -> Callable:
        """限流装饰器工厂函数。
        
        创建一个装饰器，用于为 Flask 路由添加限流功能。
        
        Args:
            limit_name: 限流规则名称，对应配置文件中的键名
            
        Returns:
            装饰器函数
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not self.enabled or not self.limiter:
                    return f(*args, **kwargs)
                
                limit = self.get_limit(limit_name)
                if not limit:
                    return f(*args, **kwargs)
                
                return self.limiter.limit(limit)(f)(*args, **kwargs)
            return decorated_function
        return decorator


__all__ = ['RateLimiter']
