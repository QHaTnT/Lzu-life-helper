"""
文件上传 API
"""
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.response import ok
from app.utils.file_upload import save_multiple_files

router = APIRouter()


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """上传文件（支持多文件），返回文件URL列表"""
    try:
        urls = await save_multiple_files(files, subfolder="general")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {e}")
    return ok({"urls": urls}, msg="上传成功")
