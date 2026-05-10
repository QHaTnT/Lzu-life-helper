"""
Redis连接配置
Docker 环境下 Redis 必须可用，连接失败直接报错。
"""
import redis
from app.core.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
    decode_responses=True,
    socket_connect_timeout=5,
)

# 启动时验证连接
redis_client.ping()
