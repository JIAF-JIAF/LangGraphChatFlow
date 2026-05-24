"""
统一日志模块

提供项目级别的日志输出功能，所有模块共用。
使用 Python logging 模块，但通过 print 输出到控制台。
"""

import logging
import logging.config
import time
import os
from typing import Optional


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] [%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": os.environ.get("LOG_LEVEL", "INFO"),
            "propagate": False
        }
    }
}


def setup_logging():
    """
    初始化项目统一日志配置
    """
    logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name: str = "App") -> logging.Logger:
    """
    获取指定名称的 Logger 实例

    Args:
        name: 模块名称（如 "Skill.Loader", "Agent" 等）

    Returns:
        Logger 实例
    """
    return logging.getLogger(name)


class PrintHandler(logging.Handler):
    """
    自定义 Handler，使用 print 输出到控制台
    """
    def emit(self, record):
        try:
            msg = self.format(record)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [{record.name}] {msg}", flush=True)
        except Exception:
            self.handleError(record)


def log(message: str, module: str = "App", level: str = "INFO"):
    """
    输出日志到控制台（兼容旧接口）

    Args:
        message: 日志消息
        module: 模块名称（如 "Skill.Loader", "Agent" 等）
        level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{module}] {message}", flush=True)


def exception(message: str, module: str = "App", exc: Optional[Exception] = None):
    """
    输出异常日志到控制台

    Args:
        message: 日志消息
        module: 模块名称（如 "Skill.Loader", "Agent" 等）
        exc: 异常对象（可选，暂不消费）
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{module}] {message}", flush=True)


setup_logging()


__all__ = ["log", "exception", "get_logger", "setup_logging"]
