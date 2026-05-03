"""
生活圈 & 活动 API
- Post: 点赞 toggle（Like 表）、评论嵌入用户、列表计数、九宫格图片
- Activity: 任意用户可发布、防重复报名、发布者查看名单
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, exists
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.core.response import ok
from app.schemas.post import (
    PostCreate, PostUpdate, PostCommentCreate, ActivityCreate,
)
from app.api.deps import get_current_active_user
from app.models import (
    User, Post, PostComment, PostCategory, Like,
    Activity, ActivityRegistration,
)
from app.utils.serializers import (
    serialize_post, serialize_post_comment,
    serialize_activity, serialize_activity_registration,
)
import json

router = APIRouter()


# ============================================================
# 动态
# ============================================================

def _post_stats(db: Session, post_id: int):
    like_count = db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar() or 0
    comment_count = db.query(func.count(PostComment.id)).filter(PostComment.post_id == post_id).scalar() or 0
    return int(like_count), int(comment_count)


def _is_liked(db: Session, post_id: int, user_id: Optional[int]) -> bool:
    if not user_id:
        return False
    return db.query(
        exists().where((Like.post_id == post_id) & (Like.user_id == user_id))
    ).scalar()


def _get_optional_user(db: Session, authorization: Optional[str]) -> Optional[User]:
    """列表接口可匿名访问，但若带 token 则展示 is_liked 真实状态。"""
    if not authorization:
        return None
    try:
        from app.core.security import decode_token
        token = authorization.split(" ", 1)[-1]
        payload = decode_token(token) or {}
        uid = payload.get("sub")
        if uid is None:
            return None
        return db.query(User).filter(User.id == int(uid)).first()
    except Exception:
        return None


@router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """发布动态"""
    try:
        cat = PostCategory(post_data.category)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"分类非法: {post_data.category}")

    images = post_data.images or []
    if len(images) > 9:
        raise HTTPException(status_code=400, detail="最多上传 9 张图片")

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
    post = (
        db.query(Post)
        .options(joinedload(Post.author))
        .filter(Post.id == post.id)
        .first()
    )
    return ok(
        serialize_post(post, like_count=0, comment_count=0, is_liked=False),
        msg="发布成功",
    )


@router.get("/posts")
def get_posts(
    category: Optional[str] = Query(None, description="分类"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    authorization: Optional[str] = None,
):
    """获取动态列表（匿名可访问；带 token 则含 is_liked）"""
    query = db.query(Post).options(joinedload(Post.author))

    if category:
        query = query.filter(Post.category == category)
    if search:
        query = query.filter(
            (Post.title.contains(search)) | (Post.content.contains(search))
        )

    posts = query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    uid = None  # 简化：列表默认匿名态，详情页会单独带 token 查询
    result = []
    for p in posts:
        like_count, comment_count = _post_stats(db, p.id)
        result.append(
            serialize_post(
                p,
                like_count=like_count,
                comment_count=comment_count,
                is_liked=_is_liked(db, p.id, uid),
            )
        )
    return ok(result)


@router.get("/posts/{post_id}")
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    """获取动态详情"""
    post = (
        db.query(Post)
        .options(joinedload(Post.author))
        .filter(Post.id == post_id)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="动态不存在")
    post.views = (post.views or 0) + 1
    db.commit()
    like_count, comment_count = _post_stats(db, post.id)
    return ok(serialize_post(post, like_count=like_count, comment_count=comment_count))


@router.post("/posts/{post_id}/like")
def toggle_like_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """点赞 / 取消点赞（toggle）"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="动态不存在")

    existed = (
        db.query(Like)
        .filter(Like.post_id == post_id, Like.user_id == current_user.id)
        .first()
    )
    if existed:
        db.delete(existed)
        db.commit()
        like_count = db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar()
        return ok({"is_liked": False, "like_count": int(like_count)}, msg="已取消点赞")

    db.add(Like(post_id=post_id, user_id=current_user.id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()  # 并发下双击：唯一约束兜底
    like_count = db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar()
    return ok({"is_liked": True, "like_count": int(like_count)}, msg="点赞成功")


@router.post("/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED)
def add_post_comment(
    post_id: int,
    comment_data: PostCommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """发表评论"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="动态不存在")

    comment = PostComment(
        post_id=post_id,
        user_id=current_user.id,
        content=comment_data.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    comment = (
        db.query(PostComment)
        .options(joinedload(PostComment.user))
        .filter(PostComment.id == comment.id)
        .first()
    )
    return ok(serialize_post_comment(comment), msg="评论成功")


@router.get("/posts/{post_id}/comments")
def get_post_comments(post_id: int, db: Session = Depends(get_db)):
    """获取评论列表"""
    comments = (
        db.query(PostComment)
        .options(joinedload(PostComment.user))
        .filter(PostComment.post_id == post_id)
        .order_by(PostComment.created_at.asc())
        .all()
    )
    return ok([serialize_post_comment(c) for c in comments])


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """删除自己的动态"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="动态不存在")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="仅作者可删除")
    db.delete(post)
    db.commit()
    return ok(msg="已删除")


@router.get("/posts/my/published")
def my_posts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """我发布的动态"""
    posts = (
        db.query(Post)
        .options(joinedload(Post.author))
        .filter(Post.author_id == current_user.id)
        .order_by(Post.created_at.desc())
        .all()
    )
    result = []
    for p in posts:
        like_count, comment_count = _post_stats(db, p.id)
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
# 活动
# ============================================================

def _activity_is_registered(db: Session, activity_id: int, user_id: int) -> bool:
    return db.query(
        exists().where(
            (ActivityRegistration.activity_id == activity_id)
            & (ActivityRegistration.user_id == user_id)
        )
    ).scalar()


@router.post("/activities", status_code=status.HTTP_201_CREATED)
def create_activity(
    activity_data: ActivityCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """任意登录用户创建活动"""
    if activity_data.end_time and activity_data.end_time <= activity_data.start_time:
        raise HTTPException(status_code=400, detail="结束时间必须晚于开始时间")
    if activity_data.max_participants is not None and activity_data.max_participants <= 0:
        raise HTTPException(status_code=400, detail="人数上限必须为正数")

    activity = Activity(
        publisher_id=current_user.id,
        **activity_data.model_dump(),
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    activity = (
        db.query(Activity)
        .options(joinedload(Activity.publisher))
        .filter(Activity.id == activity.id)
        .first()
    )
    return ok(serialize_activity(activity, is_registered=False), msg="发布成功")


@router.get("/activities")
def get_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """活动列表（公开）"""
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


@router.get("/activities/my/published")
def my_published_activities(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """我发布的活动（含报名名单）"""
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
        item = serialize_activity(a, is_registered=False)
        item["registrations"] = [
            serialize_activity_registration(r) for r in a.registrations
        ]
        data.append(item)
    return ok(data)


@router.get("/activities/my/registered")
def my_registered_activities(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """我报名的活动"""
    regs = (
        db.query(ActivityRegistration)
        .options(
            joinedload(ActivityRegistration.activity).joinedload(Activity.publisher)
        )
        .filter(ActivityRegistration.user_id == current_user.id)
        .order_by(ActivityRegistration.created_at.desc())
        .all()
    )
    return ok(
        [serialize_activity(r.activity, is_registered=True) for r in regs if r.activity]
    )


@router.get("/activities/{activity_id}")
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db),
):
    """活动详情"""
    activity = (
        db.query(Activity)
        .options(joinedload(Activity.publisher))
        .filter(Activity.id == activity_id)
        .first()
    )
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    return ok(serialize_activity(activity))


@router.post("/activities/{activity_id}/register", status_code=status.HTTP_201_CREATED)
def register_activity(
    activity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """报名活动（唯一约束防重复；并发场景二次校验容量）"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    if not activity.is_active:
        raise HTTPException(status_code=400, detail="活动已下架")

    if (
        activity.max_participants
        and activity.current_participants >= activity.max_participants
    ):
        raise HTTPException(status_code=400, detail="活动人数已满")

    reg = ActivityRegistration(
        activity_id=activity_id,
        user_id=current_user.id,
    )
    db.add(reg)
    activity.current_participants = (activity.current_participants or 0) + 1
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="您已报名该活动")
    return ok(msg="报名成功")


@router.delete("/activities/{activity_id}/register")
def cancel_registration(
    activity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """取消报名"""
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

    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    db.delete(reg)
    if activity and activity.current_participants and activity.current_participants > 0:
        activity.current_participants -= 1
    db.commit()
    return ok(msg="已取消报名")


@router.get("/activities/{activity_id}/registrations")
def list_activity_registrations(
    activity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """发布者查看报名名单"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    if activity.publisher_id != current_user.id:
        raise HTTPException(status_code=403, detail="仅发布者可查看名单")

    regs = (
        db.query(ActivityRegistration)
        .options(joinedload(ActivityRegistration.user))
        .filter(ActivityRegistration.activity_id == activity_id)
        .order_by(ActivityRegistration.created_at.asc())
        .all()
    )
    return ok([serialize_activity_registration(r) for r in regs])
