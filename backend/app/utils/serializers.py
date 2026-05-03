"""
ORM 实例 → 标准 dict 的序列化工具，便于统一响应中嵌入嵌套对象。
所有 datetime 自动 isoformat()，避免 JSONResponse 序列化报错。
"""
from datetime import datetime
from typing import Optional, List
import json

from app.models import (
    User, Product, ProductComment,
    Venue, VenueTimeSlot, Booking,
    BusRoute, BusSchedule,
    Post, PostComment,
    Activity, ActivityRegistration,
)


def _dt(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value else None


def _images(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    try:
        v = json.loads(raw)
        return v if isinstance(v, list) else []
    except Exception:
        return []


# ---------------- User ----------------
def serialize_user_brief(user: User) -> dict:
    """嵌入到帖子/评论里的用户精简卡片"""
    if not user:
        return None
    return {
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "avatar": user.avatar or "",
        "phone": user.phone or "",
    }


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "student_id": user.student_id,
        "username": user.username,
        "real_name": user.real_name,
        "phone": user.phone,
        "email": user.email,
        "avatar": user.avatar or "",
        "role": user.role.value if hasattr(user.role, "value") else user.role,
        "is_active": user.is_active,
        "created_at": _dt(user.created_at),
    }


# ---------------- Product ----------------
def serialize_product(product: Product) -> dict:
    return {
        "id": product.id,
        "title": product.title,
        "description": product.description,
        "price": product.price,
        "category": product.category.value if hasattr(product.category, "value") else product.category,
        "status": product.status.value if hasattr(product.status, "value") else product.status,
        "images": _images(product.images),
        "seller_id": product.seller_id,
        "seller": serialize_user_brief(product.seller) if product.seller else None,
        "views": product.views,
        "created_at": _dt(product.created_at),
        "updated_at": _dt(product.updated_at),
    }


def serialize_product_comment(comment: ProductComment) -> dict:
    return {
        "id": comment.id,
        "product_id": comment.product_id,
        "user_id": comment.user_id,
        "user": serialize_user_brief(comment.user) if comment.user else None,
        "content": comment.content,
        "created_at": _dt(comment.created_at),
    }


# ---------------- Venue ----------------
def serialize_venue(venue: Venue) -> dict:
    return {
        "id": venue.id,
        "name": venue.name,
        "venue_type": venue.venue_type.value if hasattr(venue.venue_type, "value") else venue.venue_type,
        "location": venue.location,
        "capacity": venue.capacity,
        "description": venue.description,
        "is_active": venue.is_active,
    }


def serialize_time_slot(slot: VenueTimeSlot) -> dict:
    return {
        "id": slot.id,
        "venue_id": slot.venue_id,
        "date": _dt(slot.date),
        "start_time": slot.start_time,
        "end_time": slot.end_time,
        "capacity": slot.capacity,
        "booked_count": slot.booked_count,
        "is_available": slot.is_available,
    }


def serialize_booking(booking: Booking) -> dict:
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "time_slot_id": booking.time_slot_id,
        "status": booking.status.value if hasattr(booking.status, "value") else booking.status,
        "created_at": _dt(booking.created_at),
        "time_slot": serialize_time_slot(booking.time_slot) if booking.time_slot else None,
        "venue": serialize_venue(booking.time_slot.venue) if booking.time_slot and booking.time_slot.venue else None,
    }


# ---------------- Bus ----------------
def serialize_bus_route(route: BusRoute) -> dict:
    return {
        "id": route.id,
        "name": route.name,
        "from_campus": route.from_campus,
        "to_campus": route.to_campus,
        "description": route.description,
        "is_active": route.is_active,
    }


def serialize_bus_schedule(s: BusSchedule) -> dict:
    return {
        "id": s.id,
        "route_id": s.route_id,
        "departure_time": s.departure_time,
        "seats": s.seats,
        "booked_seats": s.booked_seats,
        "weekday_only": s.weekday_only,
    }


# ---------------- Post ----------------
def serialize_post(
    post: Post,
    *,
    like_count: int = 0,
    comment_count: int = 0,
    is_liked: bool = False,
) -> dict:
    return {
        "id": post.id,
        "author_id": post.author_id,
        "author": serialize_user_brief(post.author) if post.author else None,
        "title": post.title,
        "content": post.content,
        "category": post.category.value if hasattr(post.category, "value") else post.category,
        "tags": post.tags,
        "images": _images(post.images),
        "views": post.views,
        "like_count": like_count,
        "comment_count": comment_count,
        "is_liked": is_liked,
        "created_at": _dt(post.created_at),
        "updated_at": _dt(post.updated_at),
    }


def serialize_post_comment(comment: PostComment) -> dict:
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "user_id": comment.user_id,
        "user": serialize_user_brief(comment.user) if comment.user else None,
        "content": comment.content,
        "created_at": _dt(comment.created_at),
    }


# ---------------- Activity ----------------
def serialize_activity(
    activity: Activity,
    *,
    is_registered: bool = False,
) -> dict:
    return {
        "id": activity.id,
        "publisher_id": activity.publisher_id,
        "publisher": serialize_user_brief(activity.publisher) if activity.publisher else None,
        "title": activity.title,
        "description": activity.description,
        "organizer": activity.organizer,
        "location": activity.location,
        "start_time": _dt(activity.start_time),
        "end_time": _dt(activity.end_time),
        "max_participants": activity.max_participants,
        "current_participants": activity.current_participants,
        "cover_image": activity.cover_image or "",
        "is_active": activity.is_active,
        "is_registered": is_registered,
        "created_at": _dt(activity.created_at),
    }


def serialize_activity_registration(reg: ActivityRegistration) -> dict:
    return {
        "id": reg.id,
        "activity_id": reg.activity_id,
        "user_id": reg.user_id,
        "user": serialize_user_brief(reg.user) if reg.user else None,
        "status": reg.status,
        "created_at": _dt(reg.created_at),
    }
