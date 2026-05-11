"""
场馆预约 API

本模块处理场馆预约相关的所有接口，包括：
- 获取场馆列表和详情
- 创建和取消预约
- 获取用户预约记录
- 获取场馆空闲时段

功能特点：
- 分布式锁防超卖：使用 Redis 分布式锁防止同一时段被多人同时预约
- 预约记录支持状态筛选
- 时段查询支持多天范围
"""

# 导入 Optional 类型，用于表示参数可以为 None
from typing import Optional

# 导入 FastAPI 核心组件
from fastapi import APIRouter, Depends, HTTPException, status, Query

# 导入 SQLAlchemy ORM 相关
from sqlalchemy.orm import Session, joinedload

# 导入数据库连接依赖
from app.core.database import get_db

# 导入统一响应格式函数
from app.core.response import ok

# 导入 Pydantic 数据模型
# BookingCreate：创建预约时的请求体格式
from app.schemas.venue import BookingCreate

# 导入场馆业务逻辑服务类
# VenueService 封装了场馆预约的核心业务逻辑，包括分布式锁处理
from app.services.venue_service import VenueService

# 导入依赖注入函数
from app.api.deps import get_current_active_user

# 导入模型类
from app.models import User, Venue, Booking, VenueTimeSlot

# 导入序列化函数
from app.utils.serializers import (
    serialize_venue, serialize_time_slot, serialize_booking,
)

# 创建路由实例
router = APIRouter()


# ============================================================
# 获取场馆列表接口
# ============================================================

# @router.get("/")：定义 GET 方法的接口，路径为 /venues/
# 用于获取所有可用场馆的列表
@router.get("/")
def get_venues(db: Session = Depends(get_db)):
    """
    获取场馆列表

    参数说明：
    - db: 数据库会话
    """
    # 查询所有启用的场馆
    # Venue.is_active == True：只查询状态为启用的场馆
    # 对应 SQL：SELECT * FROM venues WHERE is_active = TRUE
    # 这样设计可以隐藏已下架或维护中的场馆
    venues = db.query(Venue).filter(Venue.is_active == True).all()

    # 将所有场馆对象序列化为字典列表返回
    return ok([serialize_venue(v) for v in venues])


# ============================================================
# 获取我的预约记录接口
# ============================================================

# @router.get("/bookings/my")：定义 GET 方法的接口，路径为 /venues/bookings/my
# 注意：这个路由必须在 /{venue_id} 之前定义
# 因为 "bookings" 会被当作 {venue_id} 匹配，导致路由错误
# FastAPI 按照路由定义的顺序匹配，先定义的路由优先级更高
@router.get("/bookings/my")
def get_my_bookings(
    status_q: Optional[str] = Query(None, alias="status", description="预约状态"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取我的预约记录

    参数说明：
    - status_q: 预约状态筛选参数，可选值包括 "pending"（待确认）、"confirmed"（已确认）、"cancelled"（已取消）等
      使用 alias="status" 是因为 FastAPI 不允许参数名与 Python 关键字冲突
      "status" 是 Python 的内置函数名，所以用 status_q 作为参数名
      alias="status" 确保 URL 查询参数名仍然是 "status"
    - current_user: 当前登录用户
    - db: 数据库会话
    """
    # 使用 joinedload 进行急加载，一次查询获取预约、时段、场馆三层关联数据
    # 对应 SQL 类似于：
    # SELECT bookings.*, venue_time_slots.*, venues.*
    # FROM bookings
    # INNER JOIN venue_time_slots ON bookings.time_slot_id = venue_time_slots.id
    # INNER JOIN venues ON venue_time_slots.venue_id = venues.id
    # WHERE bookings.user_id = ?
    # ORDER BY bookings.created_at DESC
    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.time_slot).joinedload(VenueTimeSlot.venue))
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )

    # 如果指定了状态筛选参数，进行 Python 层面的过滤
    # 这里没有在 SQL 层面过滤的原因：
    # 1. booking.status 可能是枚举类型（Enum），需要转换为字符串比较
    # 2. 使用 hasattr 检查是否有 value 属性，兼容不同类型的 status 字段
    # 3. Python 层面过滤代码更简单易维护，且数据量不大时性能差异可忽略
    if status_q:
        bookings = [b for b in bookings if (b.status.value if hasattr(b.status, "value") else b.status) == status_q]

    return ok([serialize_booking(b) for b in bookings])


# ============================================================
# 创建预约接口
# ============================================================

# @router.post("/bookings")：定义 POST 方法的接口，路径为 /venues/bookings
# 用于创建新的预约记录
@router.post("/bookings", status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    创建预约（Redis 分布式锁）

    参数说明：
    - booking_data: 预约请求体，包含要预约的时段 ID
    - current_user: 当前登录用户
    - db: 数据库会话
    """
    # 调用 VenueService 的 create_booking_with_lock 方法创建预约
    # 该方法使用 Redis 分布式锁防止超卖（同一时段被多人同时预约）
    # 分布式锁的工作原理：
    # 1. 用户发起预约请求时，先获取 Redis 锁（基于时段 ID）
    # 2. 如果获取锁成功，检查时段是否可用
    # 3. 如果时段可用，创建预约记录并更新时段状态
    # 4. 释放 Redis 锁
    # 5. 如果获取锁失败（有其他用户正在预约），返回失败
    booking = VenueService.create_booking_with_lock(
        db, current_user.id, booking_data.time_slot_id
    )

    if not booking:
        # 400 Bad Request 表示预约失败，可能原因：
        # 1. 该时段已被其他人预约（超卖）
        # 2. 用户已经预约了该时段（防重复）
        # 3. 时段不存在或已过期
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="预约失败，该时段已满或您已预约",
        )

    # 刷新对象获取最新数据
    db.refresh(booking)

    return ok(serialize_booking(booking), msg="预约成功")


# ============================================================
# 取消预约接口
# ============================================================

# @router.delete("/bookings/{booking_id}")：定义 DELETE 方法的接口
# 用于取消已创建的预约
@router.delete("/bookings/{booking_id}")
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    取消预约

    参数说明：
    - booking_id: 要取消的预约 ID
    - current_user: 当前登录用户
    - db: 数据库会话
    """
    # 调用 VenueService 的 cancel_booking 方法
    # 该方法会验证：
    # 1. 预约是否存在
    # 2. 当前用户是否是预约的所有者
    # 3. 预约是否可以取消（已过期的预约不能取消）
    success = VenueService.cancel_booking(db, booking_id, current_user.id)

    if not success:
        # 404 Not Found 表示预约不存在或无权限取消
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="预约不存在或无权限"
        )
    return ok(msg="已取消")


# ============================================================
# 获取场馆详情接口
# ============================================================

# @router.get("/{venue_id}")：定义 GET 方法的接口，路径为 /venues/{venue_id}
# {venue_id} 是路径参数，FastAPI 会自动提取并转换为 int 类型
@router.get("/{venue_id}")
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    """
    获取场馆详情

    参数说明：
    - venue_id: 场馆 ID
    - db: 数据库会话
    """
    # 查询指定场馆
    # 对应 SQL：SELECT * FROM venues WHERE id = ?
    venue = db.query(Venue).filter(Venue.id == venue_id).first()

    if not venue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="场馆不存在")

    return ok(serialize_venue(venue))


# ============================================================
# 获取场馆空闲时段接口
# ============================================================

# @router.get("/{venue_id}/time-slots")：获取指定场馆的可用时段
# 这是嵌套资源的设计模式：时段是场馆的子资源
@router.get("/{venue_id}/time-slots")
def get_venue_time_slots(
    venue_id: int,
    days: Optional[int] = Query(None, ge=1, le=7, description="查询天数"),
    db: Session = Depends(get_db),
):
    """
    获取场馆空闲时段

    参数说明：
    - venue_id: 场馆 ID
    - days: 查询天数，可选参数，范围 1-7
      如果不指定，默认查询今天或系统配置的天数
      限制最多查询 7 天，防止数据量过大
    - db: 数据库会话
    """
    # 首先验证场馆是否存在
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="场馆不存在")

    # 调用 VenueService 的 get_available_time_slots 方法
    # 该方法会：
    # 1. 查询指定场馆在指定天数内的所有时段
    # 2. 过滤掉已过期的时段
    # 3. 返回可用的时段列表
    # 对应的 SQL 类似于：
    # SELECT * FROM venue_time_slots
    # WHERE venue_id = ? AND date >= CURDATE() AND date <= CURDATE() + ? DAYS
    # ORDER BY date, start_time
    time_slots = VenueService.get_available_time_slots(db, venue_id, days)

    return ok([serialize_time_slot(s) for s in time_slots])
