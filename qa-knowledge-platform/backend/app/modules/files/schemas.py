from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FileInfo(BaseModel):
    """文件信息模型"""
    id: str
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    file_extension: str
    file_url: str
    thumbnail_url: Optional[str] = None
    upload_time: datetime
    
    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    success: bool
    message: str
    file_info: Optional[FileInfo] = None


class ImageProcessOptions(BaseModel):
    """图片处理选项"""
    max_width: Optional[int] = 1920
    max_height: Optional[int] = 1080
    quality: Optional[int] = 85
    create_thumbnail: Optional[bool] = True
    thumbnail_size: Optional[tuple] = (300, 300)