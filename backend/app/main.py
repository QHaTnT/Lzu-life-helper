"""
FastAPI 主应用入口。

这个文件只负责“应用组装”，不承载具体业务逻辑。
换句话说，它像是整个后端的总装配车间：把配置、数据库、路由、静态资源和异常处理统一拼起来。
"""

# 导入 FastAPI 应用类，用来创建真正的 Web 应用对象。
from fastapi import FastAPI

# 导入 CORS 中间件，用来控制浏览器跨域访问策略。
from fastapi.middleware.cors import CORSMiddleware

# 导入静态文件挂载工具，用来把某个目录暴露成可访问的 URL。
from fastapi.staticfiles import StaticFiles

# 导入项目配置对象，所有可变的环境相关参数都从这里读取。
from app.core.config import settings

# 导入数据库引擎和模型基类，后面会在启动时做一次建表。
from app.core.database import engine, Base

# 导入统一响应函数和异常处理注册函数，保证接口返回格式一致。
from app.core.response import ok, add_exception_handlers

# 导入 v1 版本的路由聚合器，所有接口最终都会挂载到这个入口上。
from app.api.v1 import api_router

# 导入标准库里的 os，用来创建目录。
import os


# 这一行是在应用启动阶段执行的数据库初始化动作。
# Base.metadata 代表所有 ORM 模型对应的表结构元数据。
# create_all(bind=engine) 的意思是：根据模型定义检查数据库里是否已有这些表，如果没有就创建。
# 这样做对开发环境比较方便，但它不是迁移工具，所以复杂的生产环境通常还会配合 Alembic。
Base.metadata.create_all(bind=engine)


# 创建 FastAPI 应用实例。
# title 会显示在接口文档页面上，通常用于标识项目名称。
# version 用来说明当前 API 版本，方便前端和运维确认服务版本。
# description 是文档说明文字，会出现在 Swagger/OpenAPI 页面里。
# docs_url 指定 Swagger 文档路径。
# redoc_url 指定 ReDoc 文档路径。
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="兰州大学生活助手 API（统一响应 {code,msg,data}）",
    docs_url="/docs",
    redoc_url="/redoc",
)


# 给应用添加 CORS 中间件。
# 跨域的本质是浏览器安全策略限制，不是后端接口本身不能访问。
# 这里把允许访问的前端来源、是否允许携带凭证、允许的方法和请求头都交给配置控制。
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 确保上传目录存在。
# exist_ok=True 表示：如果目录已经存在，不要报错，直接继续。
# 这样做的目的，是避免后面的文件上传保存逻辑和静态目录挂载因为目录不存在而失败。
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


# 把上传目录挂载成静态文件服务。
# 这样浏览器访问 /uploads/xxx 时，实际上会读取 settings.UPLOAD_DIR 里的对应文件。
# name="uploads" 是这个静态挂载点的内部名称，主要用于调试和路由识别。
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# 挂载 API 路由。
# prefix="/api/v1" 表示：路由文件里定义的路径，都会自动加上这个前缀。
# 这么做的好处是版本管理清晰，后续如果升级到 v2，可以并存两个版本的 API。
app.include_router(api_router, prefix="/api/v1")


# 注册全局异常处理器。
# 它的作用是：把不同类型的异常转换成统一格式的响应，避免前端收到杂乱的错误结构。
# 统一错误结构和统一成功响应结构配合使用，前端处理会更稳定。
add_exception_handlers(app)


# 下面这个装饰器表示：当有人访问根路径 / 时，调用 root 函数。
@app.get("/")
def root():
    # 这里返回的是服务最基础的信息。
    # 它通常用于快速确认服务是否在线，以及版本号、文档地址是否正确。
    return ok(
        {
            # 当前项目名称，来自配置文件。
            "name": settings.APP_NAME,
            # 当前项目版本号，来自配置文件。
            "version": settings.APP_VERSION,
            # 文档地址写死为 /docs，是因为上面 FastAPI 已经把 Swagger 文档挂在这个路径下。
            "docs": "/docs",
        },
        # msg 是统一响应里的提示信息字段，用来告诉调用方这个接口返回的含义。
        msg="欢迎使用兰州大学生活助手 API",
    )


# 这个接口是健康检查接口。
# 运维、容器编排、负载均衡器经常会请求它，确认服务是否存活。
@app.get("/health")
def health_check():
    # 这里返回一个非常简单的状态值，表示服务运行正常。
    return ok({"status": "healthy"})


# 下面这个判断表示：只有当本文件被直接执行时，才启动 uvicorn。
# 如果是通过其他模块 import 进来的，这段代码不会运行。
if __name__ == "__main__":
    # 导入 uvicorn，一个常用的 ASGI 服务器，用来真正承载 FastAPI 应用。
    import uvicorn

    # 通过 uvicorn.run 启动服务。
    # 第一个参数是 ASGI 应用的导入路径。
    # host="0.0.0.0" 表示监听所有网卡，这样局域网或容器外部也能访问到服务。
    # port=8000 表示监听 8000 端口。
    # reload=settings.DEBUG 表示开发模式下可以自动重载代码，生产环境一般关闭。
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
