"""
用户认证 API

本模块处理用户身份认证相关的所有接口，包括：
- 用户注册（register）
- 用户登录（login）
- 获取当前用户信息（get_current_user_info）
- 更新当前用户信息（update_current_user）

认证流程说明：
1. 用户注册时提供用户名、密码等信息，系统存储用户信息（密码会加密存储）
2. 用户登录时提供用户名和密码，验证通过后返回 JWT（JSON Web Token）令牌
3. 客户端在后续请求中携带 JWT 令牌，服务端验证令牌有效性后获取用户身份
"""

# 导入 FastAPI 核心组件
from fastapi import APIRouter, Depends, HTTPException, status

# 导入 SQLAlchemy 的 Session 类，用于数据库操作
# Session 是 SQLAlchemy ORM 的核心概念，代表一个数据库连接会话
# 通过 Session 可以执行查询、添加、修改、删除等数据库操作
from sqlalchemy.orm import Session

# 导入数据库连接依赖，get_db 是一个生成器函数，用于获取数据库 Session
from app.core.database import get_db

# 导入 JWT 令牌生成函数
# create_access_token 生成短期有效的访问令牌（通常 15-30 分钟）
# create_refresh_token 生成长期有效的刷新令牌（通常 7 天）
from app.core.security import create_access_token, create_refresh_token

# 导入统一响应格式函数，ok() 用于返回成功响应
from app.core.response import ok

# 导入 Pydantic 数据模型，用于请求数据的验证和序列化
# UserCreate：注册时的请求体格式
# UserLogin：登录时的请求体格式
# UserUpdate：更新用户信息时的请求体格式
from app.schemas.user import UserCreate, UserLogin, UserUpdate

# 导入用户业务逻辑服务类，封装了用户相关的数据库操作
from app.services.user_service import UserService

# 导入依赖注入函数，用于获取当前登录用户
from app.api.deps import get_current_active_user

# 导入用户模型类，用于类型注解
from app.models import User

# 导入用户序列化函数，将 User 模型对象转换为字典格式返回给前端
from app.utils.serializers import serialize_user

# 创建路由实例，所有认证相关的接口都注册在这个 router 上
router = APIRouter()


# ============================================================
# 用户注册接口
# ============================================================

# @router.post("/register")：定义一个 POST 方法的接口，路径为 /register
# 为什么用 POST：注册操作会创建新资源（用户），符合 RESTful 规范中 POST 用于创建资源的约定
# status_code=status.HTTP_201_CREATED：设置成功时返回 201 状态码
# 201 Created 表示服务器成功创建了资源，这是 HTTP 规范中创建资源的标准响应码
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册

    参数说明：
    - user_data: 请求体数据，由 Pydantic 根据 UserCreate 模型自动验证
      FastAPI 会自动解析 JSON 请求体，并验证字段类型和必填项
      如果验证失败，会自动返回 422 错误
    - db: 数据库会话，通过 Depends(get_db) 依赖注入获取
      Depends 是 FastAPI 的依赖注入机制，get_db 会创建一个数据库 Session
      请求结束后 Session 会自动关闭，避免资源泄漏
    """
    try:
        # 调用 UserService 的 create_user 方法创建新用户
        # UserService 封装了用户创建的业务逻辑，包括密码加密、用户名重复检查等
        user = UserService.create_user(db, user_data)
    except ValueError as e:
        # 如果业务逻辑抛出 ValueError（如用户名已存在），
        # 转换为 HTTP 400 错误返回给客户端
        # 400 Bad Request 表示客户端请求有误，服务器无法处理
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # 使用自定义的 ok 函数包装成功响应
    # serialize_user 将 User 模型对象转换为字典，移除密码等敏感信息
    return ok(serialize_user(user), msg="注册成功")


# ============================================================
# 用户登录接口
# ============================================================

# @router.post("/login")：定义 POST 方法的登录接口
# 为什么用 POST：登录操作虽然不创建资源，但会传输敏感信息（密码）
# 使用 POST 可以避免密码出现在 URL 中（GET 请求的参数会在 URL 中暴露）
# 另外，登录会创建会话（生成令牌），语义上也符合 POST 的使用场景
@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录

    参数说明：
    - login_data: 登录请求体，包含 username 和 password 字段
    - db: 数据库会话，用于查询用户信息和验证密码
    """
    # 调用 UserService 的 authenticate_user 方法验证用户身份
    # 该方法会查询数据库中的用户记录，并使用 bcrypt 等算法验证密码哈希
    # 如果验证成功返回 User 对象，失败返回 None
    user = UserService.authenticate_user(db, login_data.username, login_data.password)

    if not user:
        # 401 Unauthorized 表示未通过身份验证
        # 这里使用 "用户名或密码错误" 而不是 "用户不存在"，
        # 是为了防止攻击者通过错误信息推测出有效的用户名（信息泄露攻击）
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )

    # 生成访问令牌（Access Token）
    # JWT（JSON Web Token）是一种开放标准（RFC 7519），用于在各方之间安全地传输信息
    # 令牌中包含用户ID等信息，服务端可以验证令牌有效性而无需查询数据库
    # data={"sub": str(user.id)}：sub 是 JWT 标准字段（subject），表示令牌的主体
    # 这里将用户 ID 作为主体，后续验证时可以提取出用户 ID
    # 为什么用 str(user.id)：JWT 规范要求 sub 字段必须是字符串类型
    access_token = create_access_token(data={"sub": str(user.id)})

    # 生成刷新令牌（Refresh Token）
    # 刷新令牌的有效期比访问令牌长，用于在访问令牌过期时获取新的访问令牌
    # 这样用户不需要频繁重新登录，同时保证了安全性
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # 返回登录成功响应，包含令牌信息和用户信息
    return ok(
        {
            "access_token": access_token,      # 访问令牌，客户端需要在后续请求的 Header 中携带
            "refresh_token": refresh_token,     # 刷新令牌，用于获取新的访问令牌
            "token_type": "bearer",             # 令牌类型，按照 OAuth 2.0 规范使用 "bearer" 值
            "user": serialize_user(user),       # 用户基本信息，前端用于显示用户头像、昵称等
        },
        msg="登录成功",
    )


# ============================================================
# 获取当前用户信息接口
# ============================================================

# @router.get("/me")：定义 GET 方法的接口，路径为 /me
# 为什么用 GET：获取信息不修改任何数据，符合 GET 的语义
# /me 是一个约定俗成的路径，表示获取当前登录用户自己的信息
@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    获取当前登录用户信息

    参数说明：
    - current_user: 当前登录的用户对象，通过依赖注入自动获取
      get_current_active_user 会验证请求头中的 JWT 令牌
      如果令牌有效且用户处于活跃状态，返回 User 对象
      如果令牌无效或用户被禁用，会自动抛出 401/403 错误
    """
    # 直接返回当前用户信息，不需要额外的数据库查询
    # current_user 已经是完整的 User 模型对象
    return ok(serialize_user(current_user))


# ============================================================
# 更新当前用户信息接口
# ============================================================

# @router.put("/me")：定义 PUT 方法的接口，路径为 /me
# 为什么用 PUT：更新已存在的资源，符合 RESTful 规范中 PUT 用于更新的约定
# 有些场景下也可以使用 PATCH（部分更新），但这里使用 PUT 更简单直接
@router.put("/me")
def update_current_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    更新当前用户信息

    参数说明：
    - update_data: 更新请求体，包含要更新的字段
      UserUpdate 模型的所有字段都是可选的，只更新客户端发送的字段
    - current_user: 当前登录的用户对象，通过依赖注入获取
      这里同时验证了令牌有效性和用户活跃状态
    - db: 数据库会话，用于执行更新操作
    """
    # model_dump(exclude_unset=True) 将 Pydantic 模型转换为字典
    # exclude_unset=True 表示只包含客户端明确发送的字段
    # 例如：如果客户端只发送了 {"nickname": "新昵称"}，那么只有 nickname 字段会被更新
    # 如果不加这个参数，未发送的字段会以 None 值覆盖数据库中的原有值
    update_dict = update_data.model_dump(exclude_unset=True)

    # 调用 UserService 的 update_user 方法执行更新
    # 该方法会验证用户是否存在，并执行数据库更新操作
    user = UserService.update_user(db, current_user.id, update_dict)

    if not user:
        # 404 Not Found 表示请求的资源不存在
        # 虽然当前用户理论上一定存在（已经通过认证），
        # 但这里作为防御性编程，防止数据库中用户被意外删除的情况
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    return ok(serialize_user(user), msg="更新成功")
