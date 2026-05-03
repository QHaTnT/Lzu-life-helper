"""
Pydantic Schemas - 二手市场相关
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductBase(BaseModel):
    """商品基础模型"""
    title: str = Field(..., min_length=1, max_length=100, description="商品标题")
    description: Optional[str] = Field(None, description="商品描述")
    price: float = Field(..., gt=0, description="价格")
    category: str = Field(..., description="分类")


class ProductCreate(ProductBase):
    """商品创建模型"""
    images: Optional[List[str]] = Field(default=[], description="图片URL列表")


class ProductUpdate(BaseModel):
    """商品更新模型"""
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    status: Optional[str] = None


class ProductResponse(ProductBase):
    """商品响应模型"""
    id: int
    status: str
    images: List[str]
    seller_id: int
    views: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductCommentCreate(BaseModel):
    """商品留言创建模型"""
    content: str = Field(..., min_length=1, max_length=500, description="留言内容")


class ProductCommentResponse(BaseModel):
    """商品留言响应模型"""
    id: int
    product_id: int
    user_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
