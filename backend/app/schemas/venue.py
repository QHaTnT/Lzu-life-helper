"""
Pydantic Schemas - 场馆预约相关
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VenueResponse(BaseModel):
    """场馆响应模型"""
    id: int
    name: str
    venue_type: str
    location: Optional[str]
    capacity: Optional[int]
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class VenueTimeSlotResponse(BaseModel):
    """场馆时段响应模型"""
    id: int
    venue_id: int
    date: datetime
    start_time: str
    end_time: str
    capacity: int
    booked_count: int
    is_available: bool

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    """预约创建模型"""
    time_slot_id: int = Field(..., description="时段ID")


class BookingResponse(BaseModel):
    """预约响应模型"""
    id: int
    user_id: int
    time_slot_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
