from sqlalchemy import Column, String, Text, Integer, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class FileType(str, enum.Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    OTHER = "other"


class FileStatus(str, enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)  # 存储的文件名
    file_path = Column(Text, nullable=False)  # 文件存储路径
    file_size = Column(Integer, nullable=False)  # 文件大小（字节）
    mime_type = Column(String(100), nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    status = Column(Enum(FileStatus), default=FileStatus.UPLOADING, nullable=False)
    thumbnail_path = Column(Text)  # 缩略图路径（图片文件）
    file_metadata = Column(JSON)  # 文件元数据（尺寸、时长等）
    download_count = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    uploader = relationship("User")