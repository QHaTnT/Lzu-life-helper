"""
文件上传工具
"""
import os
import uuid
from typing import List
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from PIL import Image


def validate_image(file: UploadFile) -> bool:
    """验证图片文件"""
    # 检查文件扩展名
    ext = file.filename.split(".")[-1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        return False

    return True


async def save_upload_file(file: UploadFile, subfolder: str = "") -> str:
    """
    保存上传文件
    返回文件URL
    """
    # 验证文件
    if not validate_image(file):
        raise HTTPException(status_code=400, detail="不支持的文件格式")

    # 生成唯一文件名
    ext = file.filename.split(".")[-1].lower()
    filename = f"{uuid.uuid4()}.{ext}"

    # 创建子目录
    upload_path = os.path.join(settings.UPLOAD_DIR, subfolder)
    os.makedirs(upload_path, exist_ok=True)

    # 保存文件
    file_path = os.path.join(upload_path, filename)

    # 读取并保存
    contents = await file.read()

    # 检查文件大小
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制")

    with open(file_path, "wb") as f:
        f.write(contents)

    # 返回URL
    url = f"/uploads/{subfolder}/{filename}" if subfolder else f"/uploads/{filename}"
    return url


async def save_multiple_files(files: List[UploadFile], subfolder: str = "") -> List[str]:
    """批量保存文件"""
    urls = []
    for file in files:
        url = await save_upload_file(file, subfolder)
        urls.append(url)
    return urls
