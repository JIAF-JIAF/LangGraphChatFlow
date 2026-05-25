"""
SSE 事件格式化工具
"""

import json


def format_sse_event(data: dict) -> str:
    """
    格式化 SSE 事件
    
    Args:
        data: 事件数据字典
        
    Returns:
        格式化后的 SSE 字符串
    """
    return "data: {}\n\n".format(json.dumps(data, ensure_ascii=False))
