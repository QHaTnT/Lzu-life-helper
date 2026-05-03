"""
场馆预约服务 - 核心业务逻辑
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Venue, VenueTimeSlot, Booking, BookingStatus
from app.core.config import settings


_is_sqlite = settings.DATABASE_URL.startswith("sqlite")


class VenueService:
    """场馆预约服务"""

    @staticmethod
    def get_available_time_slots(
        db: Session, venue_id: int, days: int = None
    ) -> List[VenueTimeSlot]:
        """获取场馆未来N天的空闲时段"""
        if days is None:
            days = settings.VENUE_BOOKING_DAYS

        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=days)

        time_slots = (
            db.query(VenueTimeSlot)
            .filter(
                and_(
                    VenueTimeSlot.venue_id == venue_id,
                    VenueTimeSlot.date >= start_date,
                    VenueTimeSlot.date < end_date,
                    VenueTimeSlot.is_available == True,
                    VenueTimeSlot.booked_count < VenueTimeSlot.capacity,
                )
            )
            .order_by(VenueTimeSlot.date, VenueTimeSlot.start_time)
            .all()
        )

        return time_slots

    @staticmethod
    def create_booking_with_lock(
        db: Session, user_id: int, time_slot_id: int
    ) -> Optional[Booking]:
        """
        创建预约（有 Redis 时用分布式锁，无 Redis 时用数据库事务保证并发安全）
        """
        from app.core.redis import redis_client

        lock_key = f"booking_lock:{time_slot_id}"
        lock_value = f"{user_id}:{datetime.now().timestamp()}"
        lock_timeout = settings.VENUE_BOOKING_LOCK_TIMEOUT
        use_redis = redis_client is not None

        if use_redis:
            lock_acquired = redis_client.set(lock_key, lock_value, nx=True, ex=lock_timeout)
            if not lock_acquired:
                return None

        try:
            # with_for_update 在 MySQL/PostgreSQL 下加行锁；SQLite 靠事务串行化
            q = db.query(VenueTimeSlot).filter(VenueTimeSlot.id == time_slot_id)
            if not _is_sqlite:
                q = q.with_for_update()
            time_slot = q.first()

            if not time_slot:
                return None

            if time_slot.booked_count >= time_slot.capacity:
                return None

            existing_booking = (
                db.query(Booking)
                .filter(
                    and_(
                        Booking.user_id == user_id,
                        Booking.time_slot_id == time_slot_id,
                        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                    )
                )
                .first()
            )

            if existing_booking:
                return None

            booking = Booking(
                user_id=user_id,
                time_slot_id=time_slot_id,
                status=BookingStatus.CONFIRMED,
            )
            db.add(booking)

            time_slot.booked_count += 1
            if time_slot.booked_count >= time_slot.capacity:
                time_slot.is_available = False

            db.commit()
            db.refresh(booking)
            return booking

        finally:
            if use_redis:
                redis_client.delete(lock_key)

    @staticmethod
    def cancel_booking(db: Session, booking_id: int, user_id: int) -> bool:
        """取消预约"""
        booking = (
            db.query(Booking)
            .filter(
                and_(
                    Booking.id == booking_id,
                    Booking.user_id == user_id,
                    Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                )
            )
            .first()
        )

        if not booking:
            return False

        # 更新预约状态
        booking.status = BookingStatus.CANCELLED

        # 更新时段信息
        time_slot = db.query(VenueTimeSlot).filter(
            VenueTimeSlot.id == booking.time_slot_id
        ).first()

        if time_slot:
            time_slot.booked_count = max(0, time_slot.booked_count - 1)
            time_slot.is_available = True

        db.commit()
        return True

    @staticmethod
    def get_user_bookings(
        db: Session, user_id: int, status: Optional[str] = None
    ) -> List[Booking]:
        """获取用户的预约记录"""
        query = db.query(Booking).filter(Booking.user_id == user_id)

        if status:
            query = query.filter(Booking.status == status)

        bookings = query.order_by(Booking.created_at.desc()).all()
        return bookings
