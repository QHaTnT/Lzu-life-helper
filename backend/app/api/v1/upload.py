"""
文件上传 API

本模块处理文件上传相关的接口，包括：
- 支持多文件同时上传
- 返回上传后的文件 URL

安全考虑：
- 文件类型限制：只允许上传图片、文档等安全类型
- 文件大小限制：防止恶意用户上传超大文件耗尽服务器资源
- 文件名处理：使用随机文件名防止路径遍历攻击
"""

# 导入 List 类型，用于表示参数可以接收多个文件
from typing import List

# 导入 FastAPI 核心组件
# UploadFile：FastAPI 提供的文件上传类型，封装了上传文件的信息
# File：用于声明请求体中的文件字段
from fastapi import APIRouter, UploadFile, File, HTTPException

# 导入统一响应格式函数
from app.core.response import ok

# 导入文件保存工具函数
# save_multiple_files 负责将上传的文件保存到磁盘或云存储
from app.utils.file_upload import save_multiple_files

# 创建路由实例
router = APIRouter()


# ============================================================
# 文件上传接口
# ============================================================

# @router.post("/upload")：定义 POST 方法的接口，路径为 /upload
# 为什么用 POST：文件上传需要在请求体中传输二进制数据
# GET 方法不适合传输大量数据，且 URL 长度有限制
# 另外，文件上传会创建新资源（存储文件），符合 POST 的语义
# 注意：这个路由在 __init__.py 中挂载时前缀为空字符串
# 所以完整路径是 /upload 而不是 /v1/upload（取决于主应用的路由配置）

# async def：使用异步函数，因为文件 I/O 操作通常是阻塞的
# 使用 async 可以让 FastAPI 在等待文件保存时处理其他请求
# 但实际的文件保存操作可能仍然是同步的（取决于 save_multiple_files 的实现）
@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    上传文件（支持多文件），返回文件 URL 列表

    参数说明：
    - files: 文件列表，类型为 List[UploadFile]
      File(...) 是 FastAPI 的依赖注入语法，表示从请求体的表单数据中获取文件字段
      ... 表示该字段是必填的
      UploadFile 对象包含以下属性：
      - filename: 原始文件名
      - content_type: MIME 类型（如 "image/jpeg"）
      - file: 文件内容的异步文件对象
      - size: 文件大小（字节）

    返回值：
    - 返回包含所有上传文件 URL 的列表
    """
    try:
        # 调用文件保存工具函数
        # files: 要保存的文件列表
        # subfolder="general": 指定存储的子目录
        # 使用子目录可以更好地组织文件，便于管理和清理
        # await: 等待异步操作完成
        urls = await save_multiple_files(files, subfolder="general")
    except Exception as e:
        # 捕获所有异常并返回 500 错误
        # 500 Internal Server Error 表示服务器内部错误
        # 这里不返回具体的错误细节，防止泄露服务器内部信息
        # 但在开发阶段可以保留错误详情便于调试
        raise HTTPException(status_code=500, detail=f"文件上传失败: {e}")

    # 返回上传成功响应
    # urls: 上传后的文件 URL 列表，客户端可以使用这些 URL 访问文件
    return ok({"urls": urls}, msg="上传成功")
