"""
核心配置模块。

这个文件集中管理所有可配置参数。采用"单一配置源"的设计模式：
所有配置项都定义在 Settings 类中，其他模块通过 from app.core.config import settings
来获取配置值，避免在代码各处硬编码配置。

pydantic-settings 是 Pydantic 的配置管理扩展，它的核心能力是：
  1. 自动从 .env 文件或系统环境变量中读取配置值。
  2. 对配置值进行类型校验（比如 PORT 必须是整数）。
  3. 设置默认值（当环境变量不存在时使用）。
这样做的好处是：同一套代码在开发环境和生产环境只需要改变量值，不需要改代码。
"""

# 导入 BaseSettings 类。它继承自 Pydantic 的 BaseModel，
# 额外增加了从环境变量和 .env 文件加载配置的能力。
from pydantic_settings import BaseSettings

# 导入 List 类型注解，用于声明配置项的类型（比如 CORS_ORIGINS 是一个字符串列表）。
from typing import List


class Settings(BaseSettings):
    """应用配置类。所有配置项都以类属性的形式定义，支持类型校验和默认值。"""

    # ==================== 应用基础配置 ====================

    # APP_NAME：应用名称，会显示在 Swagger 文档页面和日志中，用于标识当前服务。
    APP_NAME: str = "兰州大学生活助手"

    # APP_VERSION：应用版本号，配合文档和日志使用，方便排查问题时确认服务版本。
    APP_VERSION: str = "1.0.0"

    # DEBUG：调试模式开关。
    # True 时 uvicorn 会开启热重载（代码修改后自动重启），日志更详细。
    # False 时关闭热重载，适用于生产环境。
    # 这个值也可以通过环境变量 DEBUG=true 来覆盖。
    DEBUG: bool = True

    # SECRET_KEY：应用级密钥，通常用于签名、加密等通用场景。
    # 注意：这是一个占位默认值，生产环境必须通过 .env 文件或环境变量覆盖为一个随机强密钥。
    # 如果使用默认值，任何人都可以伪造签名，造成严重安全问题。
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # ==================== 数据库配置 ====================

    # DATABASE_URL：MySQL 数据库的连接字符串。
    # 格式为：mysql+pymysql://用户名:密码@主机:端口/数据库名
    # - mysql+pymysql：表示使用 PyMySQL 驱动连接 MySQL。
    # - lzu_user:lzu_password：数据库的用户名和密码（Docker 中预设）。
    # - mysql：Docker 环境中 MySQL 容器的主机名（Docker 内部 DNS 会解析为容器 IP）。
    # - 3306：MySQL 默认端口。
    # - lzu_helper：数据库名称。
    # 本地开发时需要改成本地地址，比如 mysql+pymysql://root:123456@localhost:3306/lzu_helper。
    DATABASE_URL: str = "mysql+pymysql://lzu_user:lzu_password@mysql:3306/lzu_helper"

    # DATABASE_ECHO：是否在终端打印 SQL 语句。
    # True 时每次执行 SQL 都会在终端输出，方便调试但影响性能。
    # False 时关闭输出，适用于生产环境。
    DATABASE_ECHO: bool = False

    # ==================== Redis 配置 ====================

    # REDIS_HOST：Redis 服务器的主机名。
    # Docker 环境下使用容器名 "redis"（Docker 内部 DNS 会自动解析）。
    # 本地开发时需要改成 "localhost"。
    REDIS_HOST: str = "redis"

    # REDIS_PORT：Redis 服务的端口号。6379 是 Redis 的默认端口。
    REDIS_PORT: int = 6379

    # REDIS_DB：Redis 数据库编号。Redis 默认有 16 个数据库（编号 0-15），
    # 这里使用 0 号数据库。不同的编号可以用来隔离不同业务的数据。
    REDIS_DB: int = 0

    # REDIS_PASSWORD：Redis 连接密码。空字符串表示无密码。
    # 生产环境建议设置密码防止未授权访问。
    REDIS_PASSWORD: str = ""

    # ==================== JWT 配置 ====================

    # JWT_SECRET_KEY：JWT 令牌的签名密钥。
    # JWT 的签名机制：服务端用这个密钥对令牌内容进行 HMAC 签名，
    # 客户端发回令牌后，服务端用同一个密钥验证签名是否被篡改。
    # 同样，这个默认值只用于开发，生产环境必须替换为随机强密钥。
    JWT_SECRET_KEY: str = "your-jwt-secret-key"

    # JWT_ALGORITHM：JWT 签名算法。
    # HS256（HMAC-SHA256）是对称签名算法，即签名和验证用同一个密钥。
    # 它的优点是速度快，适合单服务架构。如果是微服务架构，
    # 可能需要考虑 RS256（非对称签名，公钥验证）。
    JWT_ALGORITHM: str = "HS256"

    # ACCESS_TOKEN_EXPIRE_MINUTES：访问令牌（Access Token）的过期时间，单位是分钟。
    # 30 分钟是行业常见值。过期时间越短越安全（令牌泄露后攻击窗口小），
    # 但用户体验会下降（需要频繁重新登录）。30 分钟是安全性和便利性的平衡点。
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # REFRESH_TOKEN_EXPIRE_DAYS：刷新令牌（Refresh Token）的过期时间，单位是天。
    # Refresh Token 的作用是：当 Access Token 过期后，用户不需要重新输入密码，
    # 而是用 Refresh Token 换一个新的 Access Token。
    # 7 天是常见值，比 Access Token 长很多，减少用户重新登录的频率。
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ==================== 文件上传配置 ====================

    # UPLOAD_DIR：用户上传文件的存储目录。
    # "./uploads" 表示相对于项目根目录的 uploads 文件夹。
    # 主应用启动时会自动创建这个目录（在 main.py 中的 os.makedirs）。
    UPLOAD_DIR: str = "./uploads"

    # MAX_UPLOAD_SIZE：允许上传的最大文件大小，单位是字节。
    # 10485760 字节 = 10 MB（1024 * 1024 * 10）。
    # 限制文件大小是为了防止恶意用户上传超大文件耗尽服务器磁盘空间。
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB

    # ALLOWED_EXTENSIONS：允许上传的文件扩展名白名单。
    # 只允许图片格式（jpg、jpeg、png、gif、webp），防止用户上传可执行文件（.exe、.sh）。
    # 白名单比黑名单更安全：黑名单需要列出所有危险扩展名（永远列不完），
    # 白名单只列出允许的扩展名（明确且安全）。
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]

    # ==================== CORS 配置 ====================

    # CORS_ORIGINS：允许跨域访问的前端来源地址列表。
    # localhost:3000 是 Create React App 的默认开发端口。
    # localhost:5173 是 Vite 的默认开发端口。
    # 生产环境需要改为实际的前端域名（比如 https://lzu-helper.example.com）。
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ==================== 场馆预约配置 ====================

    # VENUE_BOOKING_DAYS：允许预约的未来天数。
    # 值为 3 表示用户只能预约未来 3 天内的场馆，不能预约太远的日期。
    # 限制预约范围可以减少场馆资源被长期锁定的问题。
    VENUE_BOOKING_DAYS: int = 3

    # VENUE_BOOKING_LOCK_TIMEOUT：预约锁定超时时间，单位是秒。
    # 在用户提交预约时，需要先锁定场馆（防止同一时段被两人同时预约），
    # 30 秒后如果用户没有完成操作，锁会自动释放，让其他人可以预约。
    # 这是分布式系统中常见的"乐观锁/悲观锁"策略的简化实现。
    VENUE_BOOKING_LOCK_TIMEOUT: int = 30

    # ==================== 内部配置类 ====================

    class Config:
        # env_file：指定 .env 文件的路径。pydantic-settings 会自动读取这个文件中的变量，
        # 并覆盖类属性中的默认值。这样不同环境（开发、测试、生产）可以使用不同的 .env 文件。
        env_file = ".env"

        # case_sensitive：是否区分环境变量名的大小写。
        # 设为 True 表示环境变量名必须与属性名完全一致（包括大小写）。
        # 比如 DATABASE_URL 必须写成 DATABASE_URL，不能写成 database_url。
        # 这样可以避免因大小写不一致导致配置读取失败的隐蔽 bug。
        case_sensitive = True


# 创建全局配置单例。
# 整个应用中只需要一个 Settings 实例，所有模块通过 import settings 来使用。
# 这个实例在应用启动时创建一次，后续不再重复创建。
settings = Settings()
