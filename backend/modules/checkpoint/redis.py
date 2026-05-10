"""
Redis 检查点存储实现

使用 Redis 存储检查点数据，适合生产环境。
支持持久化存储，重启服务后数据不会丢失。

依赖：redis 库
"""

import os
import pickle
import redis
from typing import Optional, Dict, List, Any, Iterator, Tuple, Sequence
from langgraph.checkpoint.base import (
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    PendingWrite,
)

from .base import BaseCheckpointSaver


class RedisSaver(BaseCheckpointSaver):
    """
    Redis 检查点存储

    使用 Redis 存储检查点，特点：
    - 需要 Redis 服务
    - 数据持久化，重启后不丢失
    - 支持分布式部署
    - 适合生产环境

    Example:
        >>> from modules.checkpoint import RedisSaver
        >>> checkpointer = RedisSaver(host='localhost', port=6379, db=0)
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = "langgraph:checkpoint:",
        ttl: Optional[int] = None,
    ):
        """
        初始化 Redis 存储

        Args:
            host: Redis 服务器地址
            port: Redis 端口
            db: Redis 数据库编号
            password: Redis 密码（可选）
            prefix: 键名前缀
            ttl: 检查点过期时间（秒），None 表示永不过期
        """
        self._redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False,
        )
        self._redis.ping()

        self._prefix = prefix
        self._ttl = ttl

    def _get_key(self, config: Dict[str, Any]) -> str:
        """从配置中提取 thread_id 作为存储键"""
        thread_id = config.get("configurable", {}).get("thread_id", "default")
        return f"{self._prefix}{thread_id}"

    def _get_history_key(self, config: Dict[str, Any]) -> str:
        """获取历史记录键"""
        thread_id = config.get("configurable", {}).get("thread_id", "default")
        return f"{self._prefix}{thread_id}:history"

    def _serialize(self, data: Any) -> bytes:
        """序列化数据"""
        return pickle.dumps(data)

    def _deserialize(self, data: bytes) -> Any:
        """反序列化数据"""
        return pickle.loads(data)

    def get(self, config: Dict[str, Any]) -> Optional[Checkpoint]:
        """
        获取检查点

        Args:
            config: 配置信息，必须包含 configurable.thread_id

        Returns:
            检查点数据，如果不存在返回 None
        """
        key = self._get_key(config)
        data = self._redis.get(key)
        if data:
            return self._deserialize(data)
        return None

    def get_tuple(self, config: Dict[str, Any]) -> Optional[CheckpointTuple]:
        """
        获取检查点元组（检查点 + 元数据）

        Args:
            config: 配置信息

        Returns:
            CheckpointTuple，如果不存在返回 None
        """
        key = self._get_key(config)
        data = self._redis.get(key)
        if data:
            checkpoint = self._deserialize(data)
            history_key = self._get_history_key(config)
            history_data = self._redis.lrange(history_key, -1, -1)
            if history_data:
                _, metadata = self._deserialize(history_data[0])
            else:
                metadata = CheckpointMetadata()
            return CheckpointTuple(config, checkpoint, metadata)
        return None

    def put(
        self,
        config: Dict[str, Any],
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: Dict[str, Any],
    ):
        """
        保存检查点

        Args:
            config: 配置信息
            checkpoint: 检查点数据
            metadata: 检查点元数据
            new_versions: 新版本信息
        """
        key = self._get_key(config)
        history_key = self._get_history_key(config)

        serialized_checkpoint = self._serialize(checkpoint)
        self._redis.set(key, serialized_checkpoint)

        if self._ttl:
            self._redis.expire(key, self._ttl)

        history_item = (checkpoint, metadata)
        serialized_history = self._serialize(history_item)
        self._redis.rpush(history_key, serialized_history)

        if self._ttl:
            self._redis.expire(history_key, self._ttl)

    def put_writes(
        self,
        config: Dict[str, Any],
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
    ):
        """
        保存待写入的数据

        Args:
            config: 配置信息
            writes: 待写入的数据列表
            task_id: 任务 ID
        """
        pass

    def list(
        self,
        config: Dict[str, Any],
        limit: Optional[int] = None,
        before: Optional[Checkpoint] = None,
    ) -> Iterator[CheckpointTuple]:
        """
        列出检查点

        Args:
            config: 配置信息
            limit: 返回数量限制
            before: 只返回此检查点之前的检查点

        Returns:
            检查点迭代器
        """
        history_key = self._get_history_key(config)
        history_data = self._redis.lrange(history_key, 0, -1)

        items = []
        for item in history_data:
            checkpoint, metadata = self._deserialize(item)
            if before and checkpoint == before:
                break
            items.append(CheckpointTuple(config, checkpoint, metadata))

        if limit:
            items = items[-limit:]

        yield from items

    def clear(self, thread_id: Optional[str] = None):
        """
        清除检查点

        Args:
            thread_id: 线程 ID，如果为 None 则清除所有检查点
        """
        if thread_id:
            key = f"{self._prefix}{thread_id}"
            history_key = f"{self._prefix}{thread_id}:history"
            self._redis.delete(key)
            self._redis.delete(history_key)
        else:
            pattern = f"{self._prefix}*"
            keys = self._redis.keys(pattern)
            if keys:
                self._redis.delete(*keys)

    def get_stats(self) -> Dict[str, Any]:
        """
        获取存储统计信息

        Returns:
            统计信息字典
        """
        pattern = f"{self._prefix}*"
        keys = self._redis.keys(pattern)

        total_threads = 0
        total_checkpoints = 0

        for key in keys:
            key_str = key.decode('utf-8') if isinstance(key, bytes) else key
            if key_str.endswith(":history"):
                length = self._redis.llen(key)
                total_checkpoints += length
                total_threads += 1

        return {
            "total_threads": total_threads,
            "total_checkpoints": total_checkpoints,
            "storage_type": "redis",
        }

    def close(self):
        """关闭 Redis 连接"""
        self._redis.close()

    @classmethod
    def build(cls, **kwargs) -> "RedisSaver":
        """
        构建 RedisSaver 实例

        从环境变量获取 Redis 配置参数

        Returns:
            RedisSaver 实例
        """
        host = kwargs.get("host") or os.getenv("REDIS_HOST", "localhost")
        port = kwargs.get("port") or int(os.getenv("REDIS_PORT", 6379))
        db = kwargs.get("db") or int(os.getenv("REDIS_DB", 0))
        password = kwargs.get("password") or os.getenv("REDIS_PASSWORD")

        return cls(
            host=host,
            port=port,
            db=db,
            password=password,
        )


from modules.checkpoint.factory import CheckpointFactory
CheckpointFactory.register("redis", RedisSaver)