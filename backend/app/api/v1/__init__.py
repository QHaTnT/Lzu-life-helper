"""
API路由汇总
"""
from fastapi import APIRouter
from app.api.v1 import auth, products, venues, posts, bus, upload

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(products.router, prefix="/products", tags=["二手市场"])
api_router.include_router(venues.router, prefix="/venues", tags=["场馆预约"])
api_router.include_router(posts.router, prefix="/community", tags=["生活圈"])
api_router.include_router(bus.router, prefix="/bus", tags=["校车服务"])
api_router.include_router(upload.router, prefix="", tags=["文件上传"])
