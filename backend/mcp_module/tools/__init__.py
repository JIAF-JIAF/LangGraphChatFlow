"""
MCP 工具定义模块
包含所有具体的工具实现
"""

from .weather_plugin import get_weather
from .weather_recommend_plugin import get_weather_forecast
from .submit_form_plugin import submit_form

__all__ = [
    'get_weather',
    'get_weather_forecast',
    'submit_form',
]