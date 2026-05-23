"""
统一日志模块

提供项目级别的日志输出功能，所有模块共用。
"""

import time


def log(message: str, module: str = "App"):
    """
    输出日志到控制台

    Args:
        message: 日志消息
        module: 模块名称（如 "Skill.Loader", "Agent" 等）
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{module}] {message}", flush=True)


__all__ = ["log"]
