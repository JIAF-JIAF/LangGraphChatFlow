"""
MCP 客户端模块
用于连接独立部署的 MCP 服务器
支持 Streamable HTTP 传输协议
"""

import asyncio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

import mcp_module.config as config


async def get_tools_from_server(url: str = config.MCP_URL):
    """
    从 MCP 服务器获取工具列表

    Args:
        url: MCP 服务器地址，默认为 config.MCP_URL

    Returns:
        工具列表
    """
    async with streamable_http_client(url) as (read_stream, write_stream, get_session_id):
        async with ClientSession(
            read_stream=read_stream,
            write_stream=write_stream,
            client_info={"name": "chartflow-client", "version": "1.0.0"}
        ) as session:
            await session.initialize()
            tools = await session.list_tools()
            return tools.tools


__all__ = ['get_tools_from_server']