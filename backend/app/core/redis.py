"""
Redis 连接配置。

Redis 是一个内存数据库（也支持持久化），常用作：
  1. 缓存：把频繁查询的数据存在 Redis 中，下次直接从内存读取，比查 MySQL 快得多。
  2. 会话存储：存储用户登录状态、Token 黑名单等需要快速读写的数据。
  3. 分布式锁：在多实例部署时，用 Redis 实现跨进程的资源锁定（比如场馆预约防并发）。
  4. 消息队列：用 Redis 的 List 或 Stream 实现简单的任务队列。

这个文件负责创建一个全局的 Redis 客户端实例，供其他模块使用。
"""

# 导入 redis 库。这是 Python 最常用的 Redis 客户端库（redis-py），
# 提供了连接 Redis 服务器和执行各种 Redis 命令的能力。
import redis

# 导入配置对象，从中读取 Redis 的连接参数。
from app.core.config import settings


# ==================== 创建 Redis 客户端 ====================

# 创建一个全局的 Redis 客户端实例。
# 这个实例在整个应用生命周期中只创建一次，所有模块共享使用。
# redis.Redis() 只是创建客户端对象，此时并不真正连接 Redis 服务器，
# 真正的连接会在第一次执行命令时建立（懒连接）。
redis_client = redis.Redis(
    # host：Redis 服务器的地址。
    # Docker 环境下使用容器名 "redis"（Docker 内部 DNS 会自动解析为容器 IP）。
    # 本地开发时需要改为 "localhost"。
    host=settings.REDIS_HOST,

    # port：Redis 服务的端口号。6379 是 Redis 的默认端口。
    port=settings.REDIS_PORT,

    # db：Redis 数据库编号（0-15，共 16 个）。
    # 不同编号的数据库之间数据完全隔离。
    # 通常用不同的编号来区分不同业务，比如 0 号用于缓存，1 号用于会话。
    db=settings.REDIS_DB,

    # password：Redis 连接密码。
    # 如果密码为空字符串（""），说明 Redis 没有设置密码，此时传 None。
    # 如果传空字符串给 redis-py，它会尝试用空密码认证，导致认证失败。
    # 所以需要判断：有密码时传密码字符串，没密码时传 None。
    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,

    # decode_responses=True：让 Redis 客户端自动将返回的字节数据解码为 Python 字符串。
    # Redis 底层存储的是字节（bytes），如果不开启这个选项，所有返回值都是 bytes 类型，
    # 使用时需要手动 .decode()，非常麻烦。开启后直接返回 str，代码更简洁。
    decode_responses=True,

    # socket_connect_timeout=5：连接超时时间（单位：秒）。
    # 如果 5 秒内无法连接到 Redis 服务器，就抛出异常。
    # 这样可以避免在 Redis 不可用时，应用无限等待连接而卡死。
    # 同时，文件开头的说明中提到"Docker 环境下 Redis 必须可用，连接失败直接报错"，
    # 这个超时设置正是实现这个策略的关键参数。
    socket_connect_timeout=5,
)


# ==================== 验证连接 ====================

# 在应用启动时立即验证 Redis 连接是否可用。
# ping() 向 Redis 服务器发送 PING 命令，如果服务器正常运行会返回 True。
# 如果 Redis 不可用（比如未启动、密码错误、网络不通），会抛出 ConnectionError 异常，
# 导致应用启动失败。
# 这样做的好处是：在应用启动时就发现 Redis 问题，而不是等到用户请求时才报错。
# 对于需要 Redis 才能正常工作的应用（比如缓存、分布式锁），启动时验证连接是必要的。
redis_client.ping()
