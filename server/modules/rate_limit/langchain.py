"""
LangChain 限流模块
提供 InMemoryRateLimiter 工厂函数
"""

from langchain_core.rate_limiters import InMemoryRateLimiter


def create_rate_limiter(
    requests_per_minute: int,
    max_bucket_size: int = 10,
) -> InMemoryRateLimiter:
    """创建 InMemoryRateLimiter，磨平启用/禁用差异
    
    Args:
        requests_per_minute: 每分钟最大请求数
        max_bucket_size: 令牌桶最大大小
        
    Returns:
        InMemoryRateLimiter 实例，禁用时设置很大的限流值
    """
    requests_per_second = requests_per_minute / 60
    return InMemoryRateLimiter(
        requests_per_second=requests_per_second,
        max_bucket_size=max_bucket_size,
    )
