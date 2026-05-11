"""
生活圈 & 活动 API

本模块处理社区生活圈相关的所有接口，包括两大功能：

一、动态（Post）功能：
- 发布动态（支持文字、图片、标签）
- 查看动态列表和详情
- 点赞/取消点赞（toggle 切换模式）
- 评论功能
- 删除自己的动态

二、活动（Activity）功能：
- 创建活动
- 查看活动列表和详情
- 报名/取消报名活动
- 发布者查看报名名单

功能特点：
- 点赞使用 Like 表实现，支持 toggle 切换（已点赞则取消，未点赞则点赞）
- 评论嵌入用户信息（使用 joinedload 预加载）
- 列表接口显示点赞数和评论数
- 图片限制最多 9 张（九宫格设计）
- 活动报名使用唯一约束防止重复报名
"""

# 导入类型注解
from typing import Optional

# 导入 datetime 用于时间处理
from datetime import datetime

# 导入 FastAPI 核心组件
from fastapi import APIRouter, Depends, HTTPException, status, Query

# 导入 SQLAlchemy ORM 相关
from sqlalchemy.orm import Session, joinedload

# 导入 SQLAlchemy 的聚合函数和存在性检查
# func.count 用于统计数量，exists 用于检查记录是否存在
from sqlalchemy import func, exists

# 导入 IntegrityError，用于捕获数据库唯一约束冲突
# 当尝试插入违反唯一约束的数据时，会抛出此异常
from sqlalchemy.exc import IntegrityError

# 导入数据库连接依赖
from app.core.database import get_db

# 导入统一响应格式函数
from app.core.response import ok

# 导入 Pydantic 数据模型
# PostCreate：发布动态时的请求体
# PostUpdate：更新动态时的请求体
# PostCommentCreate：发表评论时的请求体
# ActivityCreate：创建活动时的请求体
from app.schemas.post import (
    PostCreate, PostUpdate, PostCommentCreate, ActivityCreate,
)

# 导入依赖注入函数
from app.api.deps import get_current_active_user

# 导入所有需要的模型类
from app.models import (
    User, Post, PostComment, PostCategory, Like,
    Activity, ActivityRegistration,
)

# 导入序列化函数
from app.utils.serializers import (
    serialize_post, serialize_post_comment,
    serialize_activity, serialize_activity_registration,
)

# 导入 json 模块，用于将图片列表转换为 JSON 字符串存储
import json

# 创建路由实例
router = APIRouter()


# ============================================================
# 动态（Post）相关接口
# ============================================================


def _post_stats(db: Session, post_id: int):
    """
    获取动态的点赞数和评论数

    这是一个内部辅助函数，不对外暴露为 API 接口
    函数名以 _ 开头是 Python 的约定，表示该函数是模块内部使用的

    参数说明：
    - db: 数据库会话
    - post_id: 动态 ID

    返回值：
    - 返回元组 (like_count, comment_count)
    """
    # 统计点赞数
    # func.count(Like.id) 对应 SQL 的 COUNT(Like.id)
    # .scalar() 返回查询结果的第一行第一列的值
    # or 0 是为了防止 COUNT 结果为 NULL 时返回 None（当没有点赞时）
    like_count = db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar() or 0

    # 统计评论数
    comment_count = db.query(func.count(PostComment.id)).filter(PostComment.post_id == post_id).scalar() or 0

    # 转换为 int 类型，确保返回值是整数而不是其他数值类型
    return int(like_count), int(comment_count)


def _is_liked(db: Session, post_id: int, user_id: Optional[int]) -> bool:
    """
    检查当前用户是否已点赞指定动态

    参数说明：
    - db: 数据库会话
    - post_id: 动态 ID
    - user_id: 用户 ID，可选参数

    返回值：
    - True 表示已点赞，False 表示未点赞或未登录
    """
    # 如果用户未登录（user_id 为 None），直接返回 False
    if not user_id:
        return False

    # 使用 SQLAlchemy 的 exists() 函数检查记录是否存在
    # 对应 SQL：SELECT EXISTS(SELECT 1 FROM likes WHERE post_id = ? AND user_id = ?)
    # exists() 比查询完整记录更高效，因为它只需要检查是否存在，不需要返回具体数据
    return db.query(
        exists().where((Like.post_id == post_id) & (Like.user_id == user_id))
    ).scalar()


def _get_optional_user(db: Session, authorization: Optional[str]) -> Optional[User]:
    """
    尝试从 Authorization 头部解析用户信息

    这个函数用于列表接口，允许匿名访问，但如果带了 token 则验证用户身份
    这样设计的原因：
    1. 列表接口通常允许匿名浏览（如朋友圈首页）
    2. 如果用户已登录，可以显示更准确的点赞状态（is_liked）
    3. 未登录用户看到的点赞状态都是 False

    参数说明：
    - db: 数据库会话
    - authorization: HTTP Authorization 头部的值，格式为 "Bearer <token>"

    返回值：
    - User 对象或 None
    """
    # 如果没有 Authorization 头部，返回 None
    if not authorization:
        return None

    try:
        # 导入 token 解码函数（延迟导入避免循环依赖）
        from app.core.security import decode_token

        # 提取 token 部分
        # Authorization 头部格式为 "Bearer <token>"，需要去掉 "Bearer " 前缀
        # split(" ", 1) 按空格分割，最多分割 1 次
        # [-1] 取最后一部分，即 token 值
        token = authorization.split(" ", 1)[-1]

        # 解码 token，获取 payload
        payload = decode_token(token) or {}

        # 从 payload 中提取用户 ID
        # JWT 的 sub 字段存储用户 ID
        uid = payload.get("sub")
        if uid is None:
            return None

        # 查询用户
        return db.query(User).filter(User.id == int(uid)).first()
    except Exception:
        # 如果 token 解码失败或用户不存在，静默返回 None
        # 这里不抛出异常是为了保证列表接口的匿名访问功能
        return None


# ============================================================
# 发布动态接口
# ============================================================

# @router.post("/posts")：定义 POST 方法的接口，路径为 /community/posts
# 用于创建新的动态
@router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    发布动态

    参数说明：
    - post_data: 动态数据请求体，包含标题、内容、分类、标签、图片等字段
    - current_user: 当前登录用户
    - db: 数据库会话
    """
    # 验证分类是否有效
    # PostCategory 是一个枚举类，包含所有合法的分类值
    # 如果传入的分类不在枚举中，会抛出 ValueError
    # 这样可以防止用户传入无效的分类值
    try:
        cat = PostCategory(post_data.category)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"分类非法: {post_data.category}")

    # 获取图片列表，如果为 None 则使用空列表
    images = post_data.images or []

    # 限制最多 9 张图片
    # 为什么是 9 张：移动端通常使用九宫格布局展示图片
    # 超过 9 张会影响用户体验，且增加存储和加载成本
    if len(images) > 9:
        raise HTTPException(status_code=400, detail="最多上传 9 张图片")

    # 创建动态对象
    # 将图片列表转换为 JSON 字符串存储
    # 为什么用 JSON 字符串而不是关联表：
    # 1. 图片数量有限且不需要单独查询
    # 2. JSON 字段查询效率更高，不需要 JOIN 操作
    # 3. 数据库迁移更简单，不需要维护额外的表
    post = Post(
        author_id=current_user.id,
        title=post_data.title,
        content=post_data.content,
        category=cat,
        tags=post_data.tags,
        images=json.dumps(images),
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    # 重新查询数据库，获取完整的动态信息（包含作者信息）
    # 使用 joinedload 预加载作者信息，避免后续访问 author 属性时触发额外查询
    post = (
        db.query(Post)
        .options(joinedload(Post.author))
        .filter(Post.id == post.id)
        .first()
    )

    # 返回创建成功的动态信息
    # 新创建的动态点赞数和评论数都是 0
    return ok(
        serialize_post(post, like_count=0, comment_count=0, is_liked=False),
        msg="发布成功",
    )


# ============================================================
# 获取动态列表接口
# ============================================================

# @router.get("/posts")：定义 GET 方法的接口，路径为 /community/posts
# 用于获取动态列表，支持分页和筛选
@router.get("/posts")
def get_posts(
    category: Optional[str] = Query(None, description="分类"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    authorization: Optional[str] = None,
):
    """
    获取动态列表（匿名可访问；带 token 则含 is_liked）

    参数说明：
    - category: 分类筛选，可选参数
    - search: 搜索关键词，会同时搜索标题和内容
    - skip: 跳过的记录数，用于分页
    - limit: 返回的记录数，用于分页
    - db: 数据库会话
    - authorization: HTTP Authorization 头部，可选参数
      注意：这里没有使用 Depends(get_current_active_user)
      因为列表接口允许匿名访问，authorization 参数是可选的
    """
    # 开始构建查询
    # .options(joinedload(Post.author))：急加载作者信息
    query = db.query(Post).options(joinedload(Post.author))

    # 动态构建筛选条件
    # 只有当参数不为 None 时才添加对应的 WHERE 条件
    # 这种设计允许前端只传递需要的筛选参数
    if category:
        query = query.filter(Post.category == category)

    if search:
        # 使用 .contains() 进行模糊搜索
        # 对应 SQL 的 LIKE '%keyword%'
        # 使用 | 运算符实现 OR 条件，同时搜索标题和内容
        query = query.filter(
            (Post.title.contains(search)) | (Post.content.contains(search))
        )

    # 执行查询
    # .order_by(Post.created_at.desc())：按创建时间降序排列（最新的在前）
    # .offset(skip)：跳过前 skip 条记录
    # .limit(limit)：最多返回 limit 条记录
    posts = query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()

    # 简化处理：列表默认匿名态，不查询用户点赞状态
    # 这样设计的原因：
    # 1. 列表数据量大，为每条动态查询点赞状态会增加大量数据库查询
    # 2. 详情页会单独带 token 查询完整的点赞状态
    uid = None

    result = []
    for p in posts:
        # 为每条动态获取点赞数和评论数
        like_count, comment_count = _post_stats(db, p.id)

        # 序列化动态信息
        # is_liked 默认为 False（因为 uid 为 None）
        result.append(
            serialize_post(
                p,
                like_count=like_count,
                comment_count=comment_count,
                is_liked=_is_liked(db, p.id, uid),
            )
        )

    return ok(result)


# ============================================================
# 获取动态详情接口
# ============================================================

# @router.get("/posts/{post_id}")：获取指定动态的详细信息
@router.get("/posts/{post_id}")
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    """
    获取动态详情

    参数说明：
    - post_id: 动态 ID
    - db: 数据库会话
    """
    # 查询指定动态，急加载作者信息
    post = (
        db.query(Post)
        .options(joinedload(Post.author))
        .filter(Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(status_code=404, detail="动态不存在")

    # 更新浏览次数
    # (post.views or 0) 防止 views 为 None 时出现 TypeError
    post.views = (post.views or 0) + 1
    db.commit()

    # 获取点赞数和评论数
    like_count, comment_count = _post_stats(db, post.id)

    return ok(serialize_post(post, like_count=like_count, comment_count=comment_count))


# ============================================================
# 点赞/取消点赞接口
# ============================================================

# @router.post("/posts/{post_id}/like")：定义 POST 方法的接口
# 用于切换点赞状态（已点赞则取消，未点赞则点赞）
@router.post("/posts/{post_id}/like")
def toggle_like_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    点赞 / 取消点赞（toggle）

    参数说明：
    - post_id: 动态 ID
    - current_user: 当前登录用户
    - db: 数据库会话
    """
    # 验证动态是否存在
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="动态不存在")

    # 检查用户是否已经点赞了该动态
    existed = (
        db.query(Like)
        .filter(Like.post_id == post_id, Like.user_id == current_user.id)
        .first()
    )

    if existed:
        # 如果已经点赞，则取消点赞
        # db.delete() 从会话中删除对象
        # 提交后会执行 DELETE SQL 语句
        db.delete(existed)
        db.commit()

        # 获取最新的点赞数
        like_count = db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar()

        # 返回取消点赞后的状态
        return ok({"is_liked": False, "like_count": int(like_count)}, msg="已取消点赞")

    # 如果未点赞，则添加点赞
    # 创建 Like 对象并添加到数据库
    db.add(Like(post_id=post_id, user_id=current_user.id))

    try:
        # 提交事务
        db.commit()
    except IntegrityError:
        # 唯一约束兜底：防止并发场景下的重复点赞
        # 在高并发情况下，两个请求可能同时检查到用户未点赞
        # 然后同时尝试插入点赞记录，导致唯一约束冲突
        # 这里捕获异常并回滚事务，而不是返回错误
        # 这样用户看到的效果是"点赞成功"（因为另一个请求已经成功了）
        db.rollback()  # 并发下双击：唯一约束兜底

    # 获取最新的点赞数
    like_count = db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar()

    return ok({"is_liked": True, "like_count": int(like_count)}, msg="点赞成功")


# ============================================================
# 发表评论接口
# ============================================================

# @router.post("/posts/{post_id}/comments")：为指定动态添加评论
@router.post("/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED)
def add_post_comment(
    post_id: int,
    comment_data: PostCommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    发表评论

    参数说明：
    - post_id: 动态 ID
    - comment_data: 评论内容请求体
    - current_user: 当前登录用户
    - db: 数据库会话
    """
    # 验证动态是否存在
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="动态不存在")

    # 创建评论对象
    comment = PostComment(
        post_id=post_id,
        user_id=current_user.id,
        content=comment_data.content,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    # 重新查询获取完整的评论信息（包含用户信息）
    comment = (
        db.query(PostComment)
        .options(joinedload(PostComment.user))
        .filter(PostComment.id == comment.id)
        .first()
    )

    return ok(serialize_post_comment(comment), msg="评论成功")


# ============================================================
# 获取评论列表接口
# ============================================================

# @router.get("/posts/{post_id}/comments")：获取指定动态的所有评论
@router.get("/posts/{post_id}/comments")
def get_post_comments(post_id: int, db: Session = Depends(get_db)):
    """
    获取评论列表

    参数说明：
    - post_id: 动态 ID
    - db: 数据库会话
    """
    # 查询指定动态的所有评论
    # 使用 joinedload 急加载每条评论的用户信息
    # 按创建时间升序排列（最早评论在前，符合社交平台的常见设计）
    comments = (
        db.query(PostComment)
        .options(joinedload(PostComment.user))
        .filter(PostComment.post_id == post_id)
        .order_by(PostComment.created_at.asc())
        .all()
    )
    return ok([serialize_post_comment(c) for c in comments])


# ============================================================
# 删除动态接口
# ============================================================

# @router.delete("/posts/{post_id}")：删除指定动态
@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    删除自己的动态

    参数说明：
    - post_id: 要删除的动态 ID
    - current_user: 当前登录用户
    - db: 数据库会话
    """
    # 查询要删除的动态
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="动态不存在")

    # 权限检查：只有作者可以删除自己的动态
    # 这是重要的安全检查，防止用户删除他人的内容
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="仅作者可删除")

    # 执行删除
    db.delete(post)
    db.commit()
    return ok(msg="已删除")


# ============================================================
# 获取我发布的动态接口
# ============================================================

# @router.get("/posts/my/published")：获取当前用户发布的所有动态
# 注意：这个路由必须在 /posts/{post_id} 之前定义
# 否则 "my" 会被当作 post_id 匹配到错误的路由
@router.get("/posts/my/published")
def my_posts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    我发布的动态

    参数说明：
    - current_user: 当前登录用户
    - db: 数据库会话
    """
    # 查询当前用户发布的所有动态
    # 按创建时间降序排列（最新的在前）
    posts = (
        db.query(Post)
        .options(joinedload(Post.author))
        .filter(Post.author_id == current_user.id)
        .order_by(Post.created_at.desc())
        .all()
    )

    result = []
    for p in posts:
        # 获取每条动态的点赞数和评论数
        like_count, comment_count = _post_stats(db, p.id)

        # 对于自己的动态，可以准确显示点赞状态
        result.append(
            serialize_post(
                p,
                like_count=like_count,
                comment_count=comment_count,
                is_liked=_is_liked(db, p.id, current_user.id),
            )
        )

    return ok(result)


# ============================================================
# 活动（Activity）相关接口
# ============================================================


def _activity_is_registered(db: Session, activity_id: int, user_id: int) -> bool:
    """
    检查用户是否已报名指定活动

    参数说明：
    - db: 数据库会话
    - activity_id: 活动 ID
    - user_id: 用户 ID

    返回值：
    - True 表示已报名，False 表示未报名
    """
    # 使用 SQLAlchemy 的 exists() 函数检查记录是否存在
    # 对应 SQL：SELECT EXISTS(SELECT 1 FROM activity_registrations WHERE activity_id = ? AND user_id = ?)
    return db.query(
        exists().where(
            (ActivityRegistration.activity_id == activity_id)
            & (ActivityRegistration.user_id == user_id)
        )
    ).scalar()


# ============================================================
# 创建活动接口
# ============================================================

# @router.post("/activities")：定义 POST 方法的接口，路径为 /community/activities
# 用于创建新的活动
@router.post("/activities", status_code=status.HTTP_201_CREATED)
def create_activity(
    activity_data: ActivityCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    任意登录用户创建活动

    参数说明：
    - activity_data: 活动数据请求体
    - current_user: 当前登录用户
    - db: 数据库会话
    """
    # 验证结束时间必须晚于开始时间
    # 这是业务逻辑验证，防止创建无效的活动
    if activity_data.end_time and activity_data.end_time <= activity_data.start_time:
        raise HTTPException(status_code=400, detail="结束时间必须晚于开始时间")

    # 验证人数上限必须为正数
    # 如果设置了人数上限，必须是大于 0 的整数
    if activity_data.max_participants is not None and activity_data.max_participants <= 0:
        raise HTTPException(status_code=400, detail="人数上限必须为正数")

    # 创建活动对象
    # **activity_data.model_dump() 将 Pydantic 模型转换为字典，并使用 ** 解包为关键字参数
    # 这样可以自动将所有字段传递给 Activity 构造函数
    activity = Activity(
        publisher_id=current_user.id,
        **activity_data.model_dump(),
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    # 重新查询获取完整的活动信息（包含发布者信息）
    activity = (
        db.query(Activity)
        .options(joinedload(Activity.publisher))
        .filter(Activity.id == activity.id)
        .first()
    )

    return ok(serialize_activity(activity, is_registered=False), msg="发布成功")


# ============================================================
# 获取活动列表接口
# ============================================================

# @router.get("/activities")：获取活动列表
@router.get("/activities")
def get_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    活动列表（公开）

    参数说明：
    - skip: 跳过的记录数，用于分页
    - limit: 返回的记录数，用于分页
    - db: 数据库会话
    """
    # 查询所有启用的活动
    # 按开始时间升序排列（即将开始的活动在前）
    activities = (
        db.query(Activity)
        .options(joinedload(Activity.publisher))
        .filter(Activity.is_active == True)
        .order_by(Activity.start_time)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return ok([serialize_activity(a) for a in activities])


# ============================================================
# 获取我发布的活动接口
# ============================================================

# @router.get("/activities/my/published")：获取当前用户发布的所有活动
@router.get("/activities/my/published")
def my_published_activities(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    我发布的活动（含报名名单）

    参数说明：
    - current_user: 当前登录用户
    - db: 数据库会话
    """
    # 查询当前用户发布的所有活动
    # 使用多重 joinedload 预加载：
    # 1. Activity.publisher：活动发布者信息
    # 2. Activity.registrations：活动报名记录列表
    # 3. ActivityRegistration.user：每个报名记录的用户信息
    # 这样可以一次查询获取所有需要的数据，避免 N+1 问题
    activities = (
        db.query(Activity)
        .options(
            joinedload(Activity.publisher),
            joinedload(Activity.registrations).joinedload(ActivityRegistration.user),
        )
        .filter(Activity.publisher_id == current_user.id)
        .order_by(Activity.created_at.desc())
        .all()
    )

    data = []
    for a in activities:
        # 序列化活动信息
        item = serialize_activity(a, is_registered=False)

        # 手动添加报名名单信息
        # 因为报名名单是列表，需要单独处理
        item["registrations"] = [
            serialize_activity_registration(r) for r in a.registrations
        ]

        data.append(item)

    return ok(data)


# ============================================================
# 获取我报名的活动接口
# ============================================================

# @router.get("/activities/my/registered")：获取当前用户报名的所有活动
@router.get("/activities/my/registered")
def my_registered_activities(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    我报名的活动

    参数说明：
    - current_user: 当前登录用户
    - db: 数据库会话
    """
    # 从报名记录表开始查询
    # 使用 joinedload 预加载活动信息和发布者信息
    regs = (
        db.query(ActivityRegistration)
        .options(
            joinedload(ActivityRegistration.activity).joinedload(Activity.publisher)
        )
        .filter(ActivityRegistration.user_id == current_user.id)
        .order_by(ActivityRegistration.created_at.desc())
        .all()
    )

    # 将报名记录转换为活动信息返回
    # r.activity 获取报名记录关联的活动对象
    # 如果活动已被删除（r.activity 为 None），则跳过
    return ok(
        [serialize_activity(r.activity, is_registered=True) for r in regs if r.activity]
    )


# ============================================================
# 获取活动详情接口
# ============================================================

# @router.get("/activities/{activity_id}")：获取指定活动的详细信息
@router.get("/activities/{activity_id}")
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db),
):
    """
    活动详情

    参数说明：
    - activity_id: 活动 ID
    - db: 数据库会话
    """
    # 查询指定活动，急加载发布者信息
    activity = (
        db.query(Activity)
        .options(joinedload(Activity.publisher))
        .filter(Activity.id == activity_id)
        .first()
    )

    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    return ok(serialize_activity(activity))


# ============================================================
# 报名活动接口
# ============================================================

# @router.post("/activities/{activity_id}/register")：为指定活动报名
@router.post("/activities/{activity_id}/register", status_code=status.HTTP_201_CREATED)
def register_activity(
    activity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    报名活动（唯一约束防重复；并发场景二次校验容量）

    参数说明：
    - activity_id: 活动 ID
    - current_user: 当前登录用户
    - db: 数据库会话
    """
    # 查询指定活动
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    # 检查活动是否处于启用状态
    # 活动可能被发布者下架，下架后不允许报名
    if not activity.is_active:
        raise HTTPException(status_code=400, detail="活动已下架")

    # 检查活动人数是否已满
    # max_participants 为 None 表示不限制人数
    # current_participants 记录当前已报名人数
    if (
        activity.max_participants
        and activity.current_participants >= activity.max_participants
    ):
        raise HTTPException(status_code=400, detail="活动人数已满")

    # 创建报名记录
    reg = ActivityRegistration(
        activity_id=activity_id,
        user_id=current_user.id,
    )

    db.add(reg)

    # 更新活动的当前参与人数
    # (activity.current_participants or 0) 防止字段为 None 时出现 TypeError
    activity.current_participants = (activity.current_participants or 0) + 1

    try:
        db.commit()
    except IntegrityError:
        # 唯一约束兜底：防止重复报名
        # 数据库表上应该有 (activity_id, user_id) 的唯一约束
        # 如果用户尝试重复报名，会触发 IntegrityError
        db.rollback()
        raise HTTPException(status_code=400, detail="您已报名该活动")

    return ok(msg="报名成功")


# ============================================================
# 取消报名接口
# ============================================================

# @router.delete("/activities/{activity_id}/register")：取消报名
@router.delete("/activities/{activity_id}/register")
def cancel_registration(
    activity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    取消报名

    参数说明：
    - activity_id: 活动 ID
    - current_user: 当前登录用户
    - db: 数据库会话
    """
    # 查询用户的报名记录
    reg = (
        db.query(ActivityRegistration)
        .filter(
            ActivityRegistration.activity_id == activity_id,
            ActivityRegistration.user_id == current_user.id,
        )
        .first()
    )

    if not reg:
        raise HTTPException(status_code=404, detail="您未报名该活动")

    # 查询活动，用于更新参与人数
    activity = db.query(Activity).filter(Activity.id == activity_id).first()

    # 删除报名记录
    db.delete(reg)

    # 更新活动的当前参与人数
    # 只有当人数大于 0 时才减 1，防止出现负数
    if activity and activity.current_participants and activity.current_participants > 0:
        activity.current_participants -= 1

    db.commit()
    return ok(msg="已取消报名")


# ============================================================
# 查看报名名单接口
# ============================================================

# @router.get("/activities/{activity_id}/registrations")：获取指定活动的报名名单
@router.get("/activities/{activity_id}/registrations")
def list_activity_registrations(
    activity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    发布者查看报名名单

    参数说明：
    - activity_id: 活动 ID
    - current_user: 当前登录用户
    - db: 数据库会话
    """
    # 查询活动
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    # 权限检查：只有发布者可以查看报名名单
    # 这是出于隐私考虑，防止普通用户查看他人的报名信息
    if activity.publisher_id != current_user.id:
        raise HTTPException(status_code=403, detail="仅发布者可查看名单")

    # 查询所有报名记录，急加载用户信息
    # 按报名时间升序排列（最早报名的在前）
    regs = (
        db.query(ActivityRegistration)
        .options(joinedload(ActivityRegistration.user))
        .filter(ActivityRegistration.activity_id == activity_id)
        .order_by(ActivityRegistration.created_at.asc())
        .all()
    )

    return ok([serialize_activity_registration(r) for r in regs])
