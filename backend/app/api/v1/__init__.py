"""
API路由汇总

本文件的作用是将所有 API 模块的路由统一注册到一个总的 APIRouter 中。
FastAPI 使用路由（Router）来组织和管理不同的 API 端点（endpoint）。
这种模块化的设计可以让每个功能模块（如认证、商品、场馆）独立维护，
最后在本文件中汇总，方便主应用统一加载。
"""

# 导入 FastAPI 的 APIRouter 类，用于创建和组合路由
from fastapi import APIRouter

# 从 v1 子模块中导入各个功能模块的路由
# 每个模块文件（如 auth.py, products.py）内部都定义了自己的 router 对象
# 这里导入的是每个模块文件内部创建的 router 实例
from app.api.v1 import auth, products, venues, posts, bus, upload

# 创建一个总的 APIRouter 实例，作为所有 v1 版本 API 路由的父级容器
api_router = APIRouter()

# 使用 include_router 将各子模块的路由挂载到父级路由上
# prefix 参数为该模块的所有路由添加统一的路径前缀
# tags 参数用于在 Swagger/OpenAPI 文档中对该模块的接口进行分组显示

# 认证模块：处理用户注册、登录、获取当前用户信息等接口
# 前缀 /auth 表示该模块所有接口路径都以 /auth 开头，如 /auth/register, /auth/login
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 二手市场模块：处理商品发布、查询、更新、删除、留言等接口
# 前缀 /products 表示该模块所有接口路径都以 /products 开头
api_router.include_router(products.router, prefix="/products", tags=["二手市场"])

# 场馆预约模块：处理场馆列表查询、预约创建、取消预约等接口
# 前缀 /venues 表示该模块所有接口路径都以 /venues 开头
api_router.include_router(venues.router, prefix="/venues", tags=["场馆预约"])

# 生活圈模块：处理动态发布、点赞、评论、活动创建和报名等接口
# 前缀 /community 表示该模块所有接口路径都以 /community 开头
# 注意：实际模块文件名是 posts.py，但对外暴露的路径前缀是 /community
api_router.include_router(posts.router, prefix="/community", tags=["生活圈"])

# 校车服务模块：处理校车路线和时刻表查询接口
# 前缀 /bus 表示该模块所有接口路径都以 /bus 开头
api_router.include_router(bus.router, prefix="/bus", tags=["校车服务"])

# 文件上传模块：处理文件上传接口
# 前缀为空字符串，表示该模块的接口直接挂在根路径下，如 /upload
# 这样设计是因为文件上传是通用功能，不需要特定的业务前缀
api_router.include_router(upload.router, prefix="", tags=["文件上传"])
