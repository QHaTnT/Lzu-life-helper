"""
FastAPI 主应用
- 统一响应封装接入
- 全局异常处理
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import engine, Base
from app.core.response import ok, add_exception_handlers
from app.api.v1 import api_router
import os

# 首次启动自动建表（init_db.py 会显式 drop_all+create_all）
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="兰州大学生活助手 API（统一响应 {code,msg,data}）",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(api_router, prefix="/api/v1")
add_exception_handlers(app)


@app.get("/")
def root():
    return ok(
        {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
        },
        msg="欢迎使用兰州大学生活助手 API",
    )


@app.get("/health")
def health_check():
    return ok({"status": "healthy"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
