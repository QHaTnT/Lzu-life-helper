"""
安全工具模块：密码加密与 JWT 令牌管理。

这个文件提供两个核心安全功能：

1. 密码加密：
   - 用户注册时，将明文密码转换为哈希值（不可逆的单向加密）存储到数据库。
   - 用户登录时，用同样的算法验证输入的密码是否匹配存储的哈希值。
   - 绝对不能在数据库中存储明文密码，否则数据库泄露就等于所有用户密码泄露。

2. JWT（JSON Web Token）令牌：
   - 用户登录成功后，服务器生成一个 JWT 令牌返回给前端。
   - 前端在后续请求中携带这个令牌，服务器验证令牌的合法性来确认用户身份。
   - JWT 的优势是"无状态"：服务器不需要存储会话信息，令牌本身包含了用户身份和过期时间。
   - JWT 的结构是三段 Base64 编码用 "." 连接：header.payload.signature
     - header：声明令牌类型和签名算法。
     - payload：包含用户信息（比如 user_id）和过期时间。
     - signature：用密钥对前两部分进行签名，防止篡改。
"""

# 导入 datetime 和 timedelta，用于计算令牌的过期时间。
# datetime.utcnow() 获取当前的 UTC 时间。
# timedelta 表示一个时间间隔，比如 timedelta(minutes=30) 表示 30 分钟。
from datetime import datetime, timedelta

# 导入 Optional 类型注解。用于声明函数参数或返回值可以是 None。
from typing import Optional

# 导入 jose 库的 JWTError 和 jwt 模块。
# python-jose 是一个 JWT（JSON Web Token）处理库，
# 提供令牌的编码（生成）和解码（验证）功能。
# JWTError 是所有 JWT 相关异常的基类，包括签名无效、令牌过期等。
from jose import JWTError, jwt

# 导入 passlib 的 CryptContext 类。
# passlib 是 Python 的密码哈希库，支持多种哈希算法（bcrypt、scrypt、argon2 等）。
# CryptContext 用于管理密码哈希策略，比如选择算法、自动处理盐值（salt）生成。
from passlib.context import CryptContext

# 导入配置对象，读取 JWT 密钥、算法和令牌过期时间等参数。
from app.core.config import settings


# ==================== 密码加密 ====================

# 创建密码加密上下文对象。
# schemes=["bcrypt"]：指定使用 bcrypt 算法。
#   bcrypt 是专门用于密码哈希的算法，它的特点包括：
#   - 自动加盐（salt）：即使两个用户密码相同，哈希值也不同（防止彩虹表攻击）。
#   - 可调节的计算成本：通过 cost factor 参数控制计算时间（默认约 100ms），
#     让暴力破解变得非常慢，但用户登录时的延迟可以接受。
# deprecated="auto"：如果有旧的哈希格式存在，自动迁移到新的 bcrypt 格式。
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确。

    参数：
      plain_password：用户在登录时输入的明文密码。
      hashed_password：数据库中存储的哈希值（用户注册时生成的）。

    返回值：
      True：密码匹配（用户输入正确）。
      False：密码不匹配（用户输入错误）。

    原理：
      pwd_context.verify() 内部会做三步：
      1. 从 hashed_password 中提取盐值（bcrypt 哈希值中嵌入了盐值）。
      2. 用提取出的盐值对 plain_password 进行哈希计算。
      3. 比较计算结果和 hashed_password 是否相同。
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    生成密码的哈希值。

    参数：
      password：用户的明文密码（通常来自注册表单）。

    返回值：
      bcrypt 哈希字符串，例如 "$2b$12$LJ3m4is5Dz3ZQZ..."。
      这个字符串会被存入数据库，永远不能还原为明文密码。

    注意：
      每次调用这个函数，即使传入相同的密码，生成的哈希值也不同（因为 bcrypt 每次随机生成盐值）。
      这是正常行为，验证时 bcrypt 会自动处理盐值。
    """
    return pwd_context.hash(password)


# ==================== JWT 令牌管理 ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌（Access Token）。

    Access Token 是短期令牌，用户用它来访问受保护的 API 接口。
    过期后需要使用 Refresh Token 换取新的 Access Token。

    参数：
      data：要编码到令牌中的数据，通常包含用户身份信息。
        例如 {"sub": "user123"}，其中 "sub"（subject）是 JWT 标准字段，
        用于标识令牌的持有者。
      expires_delta：自定义的过期时间间隔。
        如果传了，就用这个值；如果不传，就用配置文件中设置的默认值（30分钟）。

    返回值：
      编码后的 JWT 字符串，格式为 "xxxxx.yyyyy.zzzzz"（三段 Base64 编码）。

    实现步骤：
      1. 复制 data 字典（避免修改原始数据）。
      2. 计算过期时间（当前时间 + 有效时长）。
      3. 将过期时间作为 "exp" 字段添加到令牌数据中。
      4. 用密钥和算法对数据进行签名编码。
    """
    # 复制原始数据，因为后续会修改这个字典（添加 exp 字段）。
    # 如果不复制直接修改 data，会影响调用方传入的原始字典（Python 字典是引用传递）。
    to_encode = data.copy()

    # 计算令牌的过期时间。
    if expires_delta:
        # 如果调用方传了自定义过期时间，使用自定义值。
        expire = datetime.utcnow() + expires_delta
    else:
        # 如果没有传自定义过期时间，使用配置文件中的默认值（30分钟）。
        # utcnow() 返回 UTC 时间（国际标准时间），而不是本地时间。
        # 使用 UTC 时间可以避免时区问题：不同服务器可能在不同时区，
        # 但 UTC 是统一的，令牌过期时间在全球一致。
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # 将过期时间作为 "exp" 字段添加到令牌 payload 中。
    # "exp" 是 JWT 标准定义的字段名，所有 JWT 库都会自动检查这个字段，
    # 如果当前时间超过 exp 的值，解码时会抛出过期异常。
    to_encode.update({"exp": expire})

    # 对数据进行 JWT 编码。
    # jwt.encode() 接收三个参数：
    #   - to_encode：要编码的字典数据（payload）。
    #   - settings.JWT_SECRET_KEY：签名密钥，用于生成和验证签名。
    #   - algorithm：签名算法，HS256 表示 HMAC-SHA256（对称签名）。
    # 编码后的字符串格式为 "header.payload.signature"，其中 signature 确保数据未被篡改。
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    创建刷新令牌（Refresh Token）。

    Refresh Token 是长期令牌，它的唯一用途是在 Access Token 过期后，
    用来换取新的 Access Token，而不需要用户重新输入密码。

    参数：
      data：要编码到令牌中的数据，通常包含用户身份信息。

    返回值：
      编码后的 JWT 字符串。

    与 Access Token 的区别：
      - 过期时间更长（默认 7 天，而 Access Token 是 30 分钟）。
      - 通常只用于"换取新 Access Token"这一个接口，不用于访问其他 API。
      - 安全性考虑：Refresh Token 泄露的危害更大（可以长期冒充用户），
        所以存储和传输时需要更加小心。
    """
    to_encode = data.copy()
    # 计算过期时间，使用配置中的刷新令牌过期天数（默认 7 天）。
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    # 使用相同的密钥和算法进行编码。
    # 注意：Access Token 和 Refresh Token 使用同一个密钥，
    # 区分它们的方式是 payload 中的数据不同（或者在 payload 中加入 "type" 字段来区分）。
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    解码并验证 JWT 令牌。

    当前端发送请求时，在 Authorization 头中携带 JWT 令牌。
    后端调用这个函数来验证令牌的合法性并提取其中的数据。

    参数：
      token：前端传来的 JWT 字符串。

    返回值：
      解码成功：返回 payload 字典，包含用户身份等信息（如 {"sub": "user123", "exp": ...}）。
      解码失败：返回 None（可能是令牌过期、签名无效、格式错误等原因）。

    安全考虑：
      jwt.decode() 会自动验证以下内容：
      1. 签名是否有效（防止令牌被篡改）。
      2. 令牌是否过期（检查 exp 字段）。
      3. 算法是否匹配（防止算法替换攻击，比如把 HS256 改成 none）。
      任何一项验证失败都会抛出 JWTError，被 except 捕获后返回 None。
    """
    try:
        # jwt.decode() 接收三个参数：
        #   - token：待解码的 JWT 字符串。
        #   - settings.JWT_SECRET_KEY：签名密钥，必须与编码时使用的密钥一致。
        #   - algorithms=[settings.JWT_ALGORITHM]：指定允许的算法列表。
        #     注意：这里是一个列表，因为 JWT 标准允许多个算法。
        #     必须显式指定允许的算法，否则可能遭受"算法替换攻击"
        #     （攻击者把算法改成 none，绕过签名验证）。
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        # JWTError 捕获所有 JWT 相关异常，包括：
        #   - ExpiredSignatureError：令牌已过期。
        #   - JWTError：签名无效、格式错误等。
        # 返回 None 表示令牌无效，调用方应该拒绝这个请求。
        return None
