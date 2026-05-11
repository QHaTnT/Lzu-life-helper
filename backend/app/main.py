"""
FastAPI 主应用入口。

这个文件是整个后端服务的启动文件，负责把所有组件组装在一起。
它的职责不包含具体的业务逻辑（比如查询数据库、处理用户请求），
它只负责三件事：
  1. 创建 FastAPI 应用实例（告诉框架"我要启动一个 Web 服务"）。
  2. 注册中间件、路由、异常处理器（告诉框架"收到请求后该怎么处理"）。
  3. 在启动时做一些一次性初始化工作（比如建表、确保目录存在）。
"""

# ==================== 导入部分 ====================

# 导入 FastAPI 类。这是 FastAPI 框架的核心类，
# 创建它的实例就等于创建了一个 Web 应用，后续所有路由、中间件都挂在这个实例上。
from fastapi import FastAPI

# 导入 CORSMiddleware（跨域中间件）。
# 浏览器的同源策略（Same-Origin Policy）会阻止网页向不同域名/端口发请求。
# 前端通常运行在 localhost:3000 或 localhost:5173，后端运行在 localhost:8000，
# 两边端口不同，浏览器会视为"跨域"，如果没有这个中间件，前端的请求会被浏览器拦截。
from fastapi.middleware.cors import CORSMiddleware

# 导入 StaticFiles 类，它可以将服务器上的某个目录"挂载"成 HTTP 可访问的静态资源。
# 比如用户上传了头像图片保存在 ./uploads 目录下，
# 挂载后浏览器通过 /uploads/xxx.jpg 就能直接访问到这个文件。
from fastapi.staticfiles import StaticFiles

# 导入自定义的配置对象。这个对象从 .env 文件或环境变量中读取所有配置参数，
# 这样代码里不需要硬编码数据库密码、密钥等敏感信息。
from app.core.config import settings

# 导入 SQLAlchemy 的 engine（数据库引擎）和 Base（ORM 模型基类）。
# engine 负责与 MySQL 数据库建立连接；
# Base 是所有 ORM 模型类的父类，通过它可以自动根据模型定义创建数据库表。
from app.core.database import engine, Base

# 导入 ok 函数和 add_exception_handlers 函数。
# ok() 用于构造统一格式的成功响应：{"code": 0, "msg": "success", "data": ...}。
# add_exception_handlers() 用于注册全局异常处理器，把各种错误统一转成相同格式返回给前端。
from app.core.response import ok, add_exception_handlers

# 导入 v1 版本的 API 路由聚合器。
# 在 app/api/v1/__init__.py 中，所有子路由（用户、文章、预约等）
# 都会被注册到 api_router 上，这里一次性挂载到主应用中。
from app.api.v1 import api_router

# 导入 Python 标准库的 os 模块，主要用 os.makedirs 来创建目录。
import os


# ==================== 数据库初始化 ====================

# 在应用启动时执行一次数据库建表操作。
# Base.metadata 包含了所有继承自 Base 的 ORM 模型对应的表结构信息（列名、类型、约束等）。
# create_all() 会对比 metadata 中的表定义和数据库中实际存在的表，
# 如果数据库里缺少某些表，就自动创建；已存在的表不会被修改或删除。
# bind=engine 指定使用哪个数据库连接来执行建表。
# 注意：这只适合开发环境快速建表，生产环境应该用 Alembic 做数据库迁移，
# 因为 create_all 不支持修改已有表结构（比如加列、改类型）。
Base.metadata.create_all(bind=engine)


# ==================== 创建应用实例 ====================

# 创建 FastAPI 应用实例，这个实例是整个后端服务的核心对象。
# title：显示在 Swagger 文档页面顶部的项目名称。
# version：API 版本号，方便前端和运维确认当前服务版本。
# description：API 的文字说明，出现在 Swagger 文档页面中。
# docs_url="/docs"：指定 Swagger UI 的访问路径，访问 /docs 就能看到所有接口文档。
# redoc_url="/redoc"：指定 ReDoc 文档的访问路径，ReDoc 是另一种风格的 API 文档。
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="兰州大学生活助手 API（统一响应 {code,msg,data}）",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ==================== 中间件配置 ====================

# 添加 CORS（跨域资源共享）中间件。
# 浏览器在检测到跨域请求时，会先发送一个 OPTIONS "预检请求"（preflight request），
# 如果服务端不返回允许跨域的响应头，浏览器就会阻止后续请求。
# allow_origins：指定哪些域名可以跨域访问。这里配置了 localhost:3000（前端开发服务器）
#   和 localhost:5173（Vite 开发服务器），说明开发时前后端是分开运行的。
# allow_credentials=True：允许浏览器在跨域请求中携带 Cookie 和 Authorization 头。
#   如果设为 false，前端即使发了 Token，后端也收不到。
# allow_methods=["*"]：允许所有 HTTP 方法（GET、POST、PUT、DELETE 等）。
# allow_headers=["*"]：允许所有自定义请求头（比如 Authorization、Content-Type）。
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 静态资源目录 ====================

# 创建上传文件的存储目录。
# settings.UPLOAD_DIR 默认值是 "./uploads"，即当前工作目录下的 uploads 文件夹。
# exist_ok=True 表示如果目录已经存在，不抛出异常，直接跳过。
# 这行代码的目的是确保目录一定存在，避免后续文件上传或静态资源挂载时因目录缺失而报错。
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


# 将 uploads 目录挂载为静态文件服务。
# 挂载后，对 /uploads/xxx.jpg 的 HTTP 请求会被自动映射到 ./uploads/xxx.jpg 文件。
# name="uploads" 是给这个挂载点取的内部名称，主要用于调试日志和路由识别。
# 这样前端可以直接通过 URL 访问用户上传的图片，而不需要专门写一个下载接口。
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# ==================== 路由挂载 ====================

# 将 v1 版本的 API 路由注册到主应用上。
# prefix="/api/v1" 表示所有子路由都会自动加上 /api/v1 前缀。
# 例如，用户路由文件里定义了 /register，实际访问路径就变成 /api/v1/register。
# 这样做的好处是版本管理清晰：未来升级到 v2 时，可以同时挂载 v1 和 v2 的路由，
# 两套 API 共存，前端可以逐步迁移。
app.include_router(api_router, prefix="/api/v1")


# ==================== 异常处理 ====================

# 注册全局异常处理器。
# 当路由处理函数抛出异常时（比如数据库查询失败、参数校验不通过、未捕获的运行时错误），
# 这些处理器会把异常信息转换成统一格式的 JSON 响应返回给前端。
# 统一格式是 {"code": xxx, "msg": "具体错误信息", "data": null}，
# 这样前端不需要针对不同类型的错误做不同的解析逻辑。
add_exception_handlers(app)


# ==================== 根路由 ====================

# 定义根路由 "/" 的处理函数。
# 当用户访问 http://localhost:8000/ 时，会调用这个函数。
# @app.get("/") 表示只处理 GET 请求。
@app.get("/")
def root():
    # 返回服务的基本信息，用于快速确认服务是否正常运行。
    # 使用 ok() 函数包装，确保返回格式与所有其他接口一致。
    return ok(
        {
            # APP_NAME：项目名称，来自配置文件中的设置。
            "name": settings.APP_NAME,
            # APP_VERSION：项目版本号，方便排查问题时确认服务版本。
            "version": settings.APP_VERSION,
            # docs 指向 Swagger 文档路径，方便用户快速找到接口文档。
            "docs": "/docs",
        },
        # msg 字段是统一响应结构中的提示信息，这里用中文说明接口含义。
        msg="欢迎使用兰州大学生活助手 API",
    )


# ==================== 健康检查接口 ====================

# 定义健康检查接口 "/health"。
# 这个接口不承载任何业务逻辑，它存在的唯一目的是让外部系统确认服务是否存活。
# 使用场景：
#   - Docker 容器的 HEALTHCHECK 指令会定期请求这个接口。
#   - Kubernetes 的存活探针（livenessProbe）和就绪探针（readinessProbe）会探测这个接口。
#   - 负载均衡器（如 Nginx）会用它来判断后端实例是否健康。
@app.get("/health")
def health_check():
    # 返回 {"code": 0, "msg": "success", "data": {"status": "healthy"}}，
    # 表示服务正常运行。
    return ok({"status": "healthy"})


# ==================== 本地开发启动 ====================

# __name__ 是 Python 的内置变量。当这个文件被直接运行时（python main.py），
# __name__ 的值是 "__main__"；如果是被其他文件 import 的，值是 "app.main"。
# 这个判断确保只有直接运行此文件时才启动服务，被 import 时不会重复启动。
if __name__ == "__main__":
    # 导入 uvicorn。uvicorn 是一个 ASGI 服务器，
    # ASGI（Asynchronous Server Gateway Interface）是 Python 异步 Web 服务的标准接口，
    # FastAPI 正是基于 ASGI 构建的，所以需要用 uvicorn 来运行它。
    import uvicorn

    # 启动服务：
    #   "app.main:app"：告诉 uvicorn 去 app/main.py 文件中找名为 app 的对象（即 FastAPI 实例）。
    #   host="0.0.0.0"：监听所有网络接口，不仅本机 localhost 能访问，
    #     同一局域网内的其他设备（比如手机）也能访问。
    #     如果只写 127.0.0.1，则只有本机能访问。
    #   port=8000：监听 8000 端口，前端请求会发到这个端口。
    #   reload=settings.DEBUG：开发模式下开启自动重载，
    #     当代码发生修改时 uvicorn 会自动重启服务，不需要手动重启。
    #     生产环境 DEBUG=False，关闭此功能以提高性能和稳定性。
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
