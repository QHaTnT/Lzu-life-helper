"""
场馆预约 API
- 分布式锁防超卖
- GET /bookings/my 附带场馆/时段详情
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.core.response import ok
from app.schemas.venue import BookingCreate
from app.services.venue_service import VenueService
from app.api.deps import get_current_active_user
from app.models import User, Venue, Booking, VenueTimeSlot
from app.utils.serializers import (
    serialize_venue, serialize_time_slot, serialize_booking,
)

router = APIRouter()


@router.get("/")
def get_venues(db: Session = Depends(get_db)):
    """获取场馆列表"""
    venues = db.query(Venue).filter(Venue.is_active == True).all()
    return ok([serialize_venue(v) for v in venues])


@router.get("/bookings/my")
def get_my_bookings(
    status_q: Optional[str] = Query(None, alias="status", description="预约状态"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取我的预约记录（放在动态路由前，避免被 {venue_id} 捕获）"""
    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.time_slot).joinedload(VenueTimeSlot.venue))
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    if status_q:
        bookings = [b for b in bookings if (b.status.value if hasattr(b.status, "value") else b.status) == status_q]
    return ok([serialize_booking(b) for b in bookings])


@router.post("/bookings", status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """创建预约（Redis 分布式锁）"""
    booking = VenueService.create_booking_with_lock(
        db, current_user.id, booking_data.time_slot_id
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="预约失败，该时段已满或您已预约",
        )
    db.refresh(booking)
    return ok(serialize_booking(booking), msg="预约成功")


@router.delete("/bookings/{booking_id}")
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """取消预约"""
    success = VenueService.cancel_booking(db, booking_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="预约不存在或无权限"
        )
    return ok(msg="已取消")


@router.get("/{venue_id}")
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    """获取场馆详情"""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="场馆不存在")
    return ok(serialize_venue(venue))


@router.get("/{venue_id}/time-slots")
def get_venue_time_slots(
    venue_id: int,
    days: Optional[int] = Query(None, ge=1, le=7, description="查询天数"),
    db: Session = Depends(get_db),
):
    """获取场馆空闲时段"""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="场馆不存在")
    time_slots = VenueService.get_available_time_slots(db, venue_id, days)
    return ok([serialize_time_slot(s) for s in time_slots])
