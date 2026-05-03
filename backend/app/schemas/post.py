"""
Pydantic Schemas - 生活圈相关
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PostBase(BaseModel):
    """动态基础模型"""
    title: Optional[str] = Field(None, max_length=100, description="标题")
    content: str = Field(..., min_length=1, description="内容")
    category: str = Field(..., description="分类")
    tags: Optional[str] = Field(None, description="标签")


class PostCreate(PostBase):
    """动态创建模型"""
    images: Optional[List[str]] = Field(default=[], description="图片URL列表")


class PostUpdate(BaseModel):
    """动态更新模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None


class PostResponse(PostBase):
    """动态响应模型"""
    id: int
    author_id: int
    images: List[str]
    likes: int
    views: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostCommentCreate(BaseModel):
    """动态评论创建模型"""
    content: str = Field(..., min_length=1, max_length=500, description="评论内容")


class PostCommentResponse(BaseModel):
    """动态评论响应模型"""
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityCreate(BaseModel):
    """活动创建模型"""
    title: str = Field(..., min_length=1, max_length=100, description="活动标题")
    description: Optional[str] = Field(None, description="活动描述")
    organizer: Optional[str] = Field(None, description="主办方")
    location: Optional[str] = Field(None, description="活动地点")
    start_time: datetime = Field(..., description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    max_participants: Optional[int] = Field(None, description="最大参与人数")
    cover_image: Optional[str] = Field(None, description="封面图片")


class ActivityResponse(BaseModel):
    """活动响应模型"""
    id: int
    title: str
    description: Optional[str]
    organizer: Optional[str]
    location: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    max_participants: Optional[int]
    current_participants: int
    cover_image: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
