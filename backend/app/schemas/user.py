"""
Pydantic Schemas - 用户相关
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    student_id: str = Field(..., min_length=1, max_length=20, description="学号/工号")
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$", description="手机号")
    email: Optional[EmailStr] = Field(None, description="邮箱")


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名或学号")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """用户更新模型"""
    real_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    avatar: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """令牌响应模型"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
