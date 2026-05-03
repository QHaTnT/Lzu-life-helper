"""
Redis连接配置（可选）
连不上 Redis 时降级为 None，场馆预约改用数据库事务锁。
"""
import redis
from app.core.config import settings


def _try_connect():
    try:
        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True,
            socket_connect_timeout=1,
        )
        client.ping()
        return client
    except Exception:
        return None


redis_client = _try_connect()
