"""
依赖注入 - 获取当前用户

本模块提供用户身份验证的依赖注入函数，是整个 API 认证系统的核心。

依赖注入（Dependency Injection）是 FastAPI 的核心特性之一：
- 它允许你声明函数需要的参数（如数据库连接、当前用户）
- FastAPI 会自动处理参数的获取和传递
- 请求结束后自动清理资源（如关闭数据库连接）

本模块提供的函数：
- get_current_user: 从 JWT 令牌中解析用户身份
- get_current_active_user: 在 get_current_user 基础上检查用户是否活跃

认证流程：
1. 客户端在请求头中携带 Authorization: Bearer <token>
2. FastAPI 的 HTTPBearer 安全方案自动提取 token
3. 本模块验证 token 有效性并返回对应的用户对象
4. 如果验证失败，返回 401/403 错误
"""

# 导入 Optional 类型，用于表示参数可以为 None
from typing import Optional

# 导入 FastAPI 核心组件
from fastapi import Depends, HTTPException, status

# 导入 HTTPBearer 安全方案
# HTTPBearer 是 FastAPI 内置的安全方案，用于处理 JWT 令牌
# 它会自动从请求头中提取 Authorization: Bearer <token> 格式的令牌
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 导入 SQLAlchemy 的 Session 类
from sqlalchemy.orm import Session

# 导入数据库连接依赖
from app.core.database import get_db

# 导入 JWT 令牌解码函数
from app.core.security import decode_token

# 导入用户模型
from app.models import User

# 创建 HTTPBearer 安全方案实例
# 这个实例会被 FastAPI 用于自动解析请求头中的令牌
security = HTTPBearer()


# ============================================================
# 获取当前登录用户
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    获取当前登录用户

    这是认证系统的核心函数，负责：
    1. 从请求头中提取 JWT 令牌
    2. 解码令牌获取用户 ID
    3. 查询数据库获取用户信息
    4. 验证用户是否活跃

    参数说明：
    - credentials: HTTPBearer 安全方案自动解析的凭证信息
      HTTPAuthorizationCredentials 对象包含：
      - scheme: 认证方案类型（如 "Bearer"）
      - credentials: 令牌字符串
      通过 Depends(security) 依赖注入获取
    - db: 数据库会话，通过 Depends(get_db) 依赖注入获取

    返回值：
    - User 对象：验证成功的用户

    异常：
    - 401 Unauthorized: 令牌无效、过期或用户不存在
    - 403 Forbidden: 用户被禁用
    """
    # 提取令牌字符串
    # credentials.credentials 包含 "Bearer " 后面的 token 部分
    token = credentials.credentials

    # 解码 JWT 令牌
    # decode_token 函数会验证令牌签名和有效期
    # 如果验证成功，返回令牌的 payload（包含用户 ID 等信息）
    # 如果验证失败（签名无效、过期等），返回 None
    payload = decode_token(token)

    if payload is None:
        # 401 Unauthorized 表示未通过身份验证
        # 这里使用统一的错误消息，不区分具体失败原因
        # 防止攻击者通过错误信息推测系统实现细节
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
        )

    # 从 payload 中提取用户 ID
    # JWT 标准中，sub（subject）字段用于存储主体标识
    # 我们在生成令牌时将用户 ID 存储在 sub 字段中
    user_id = payload.get("sub")

    if user_id is None:
        # 如果 payload 中没有 sub 字段，说明令牌格式不正确
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
        )

    # 查询数据库获取用户信息
    # 虽然令牌中可以存储用户信息，但我们选择查询数据库
    # 原因：
    # 1. 可以获取最新的用户状态（如用户名、头像等）
    # 2. 可以验证用户是否仍然存在（可能已被删除）
    # 3. 可以检查用户是否被禁用
    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        # 用户不存在（可能已被删除）
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    # 检查用户是否处于活跃状态
    # 用户可能被管理员禁用，禁用后不应允许访问系统
    if not user.is_active:
        # 403 Forbidden 表示已通过身份验证但无权限
        # 与 401 的区别：401 表示未认证，403 表示已认证但无权限
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    return user


# ============================================================
# 获取当前活跃用户
# ============================================================

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃用户

    这个函数是对 get_current_user 的封装，提供更清晰的语义：
    - get_current_user: 获取当前用户（可能被禁用）
    - get_current_active_user: 获取当前活跃用户（未被禁用）

    实际上，get_current_user 已经包含了活跃状态检查
    这个函数的存在主要是为了：
    1. 代码可读性：明确表示需要活跃用户
    2. 未来扩展：可以在这里添加更多检查（如邮箱验证等）

    参数说明：
    - current_user: 通过 Depends(get_current_user) 获取的用户对象
      依赖注入会自动调用 get_current_user 函数

    返回值：
    - User 对象：验证成功的活跃用户
    """
    # 直接返回用户对象
    # 因为 get_current_user 已经完成了所有验证
    return current_user
