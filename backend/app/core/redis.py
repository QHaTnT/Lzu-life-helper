"""
Redis连接配置
"""
import redis
from app.core.config import settings


class RedisClient:
    """Redis客户端单例"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True,
            )
        return cls._instance

    def get_client(self):
        """获取Redis客户端"""
        return self.client


redis_client = RedisClient().get_client()
