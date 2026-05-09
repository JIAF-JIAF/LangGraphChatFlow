"""
配置模块
集中管理项目常量配置
"""

# MCP 服务器配置（单个，保持向后兼容）
MCP_HOST = "0.0.0.0"
MCP_PORT = 8080
MCP_PATH = "/mcp"
MCP_URL = f"http://127.0.0.1:{MCP_PORT}{MCP_PATH}"

# 多个 MCP 服务器配置
# 支持配置多个 MCP 服务器，从所有启用的服务器获取工具
MCP_SERVERS = [
    {
        "name": "default",
        "url": MCP_URL,
        "enabled": True,
        "description": "默认 MCP 服务器"
    }
    # 可以添加更多 MCP 服务器
    # {
    #     "name": "weather",
    #     "url": "http://127.0.0.1:8081/mcp",
    #     "enabled": True,
    #     "description": "天气服务 MCP 服务器"
    # },
    # {
    #     "name": "form",
    #     "url": "http://127.0.0.1:8082/mcp",
    #     "enabled": False,
    #     "description": "表单服务 MCP 服务器（暂禁用）"
    # }
]

# 应用服务器配置
APP_HOST = "0.0.0.0"
APP_PORT = 5000

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


__all__ = [
    'MCP_HOST',
    'MCP_PORT',
    'MCP_PATH',
    'MCP_URL',
    'MCP_SERVERS',
    'APP_HOST',
    'APP_PORT',
    'LOG_LEVEL',
    'LOG_FORMAT',
    'LOG_DATE_FORMAT'
]