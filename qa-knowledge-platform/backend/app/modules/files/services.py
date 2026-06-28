import os
import uuid
import aiofiles
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import UploadFile, HTTPException, Depends
from PIL import Image, ImageOps
import mimetypes
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.config import settings
from app.core.database import get_async_session
from app.modules.files.schemas import FileInfo, ImageProcessOptions
from app.modules.files.models import UploadedFile, FileType, FileStatus


class FileService:
    """文件服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.upload_dir = settings.UPLOAD_DIR
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = settings.ALLOWED_FILE_TYPES

        # 文件类型映射
        self.file_type_mapping = {
            # 图片类型
            ".jpg": FileType.IMAGE,
            ".jpeg": FileType.IMAGE,
            ".png": FileType.IMAGE,
            ".gif": FileType.IMAGE,
            ".bmp": FileType.IMAGE,
            ".webp": FileType.IMAGE,
            ".svg": FileType.IMAGE,
            ".tiff": FileType.IMAGE,
            # 文档类型
            ".pdf": FileType.DOCUMENT,
            ".doc": FileType.DOCUMENT,
            ".docx": FileType.DOCUMENT,
            ".txt": FileType.DOCUMENT,
            ".rtf": FileType.DOCUMENT,
            ".odt": FileType.DOCUMENT,
            ".xls": FileType.DOCUMENT,
            ".xlsx": FileType.DOCUMENT,
            ".ppt": FileType.DOCUMENT,
            ".pptx": FileType.DOCUMENT,
            ".md": FileType.DOCUMENT,
            # 压缩文件
            ".zip": FileType.ARCHIVE,
            ".rar": FileType.ARCHIVE,
            ".7z": FileType.ARCHIVE,
            ".tar": FileType.ARCHIVE,
            ".gz": FileType.ARCHIVE,
        }

        # 确保上传目录存在
        self._ensure_directories()

    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            self.upload_dir,
            os.path.join(self.upload_dir, "images"),
            os.path.join(self.upload_dir, "documents"),
            os.path.join(self.upload_dir, "archives"),
            os.path.join(self.upload_dir, "thumbnails"),
            os.path.join(self.upload_dir, "temp"),
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def _coerce_uuid(self, value: str) -> Optional[uuid.UUID]:
        try:
            return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
        except (TypeError, ValueError):
            return None

    async def validate_file(self, file: UploadFile) -> Dict[str, Any]:
        """验证文件并返回文件信息"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")

        # 检查文件名安全性（防止路径遍历攻击）
        if ".." in file.filename or "/" in file.filename or "\\" in file.filename:
            raise HTTPException(status_code=400, detail="文件名包含非法字符")

        # 检查文件名长度
        if len(file.filename) > 255:
            raise HTTPException(status_code=400, detail="文件名过长")

        # 获取文件内容以检查实际大小
        content = await file.read()
        await file.seek(0)  # 重置文件指针

        file_size = len(content)

        # 检查文件大小
        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制 ({self.max_file_size / 1024 / 1024:.1f}MB)",
            )

        # 检查文件扩展名
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_extension}。支持的类型: {', '.join(self.allowed_extensions)}",
            )

        # 获取MIME类型
        mime_type = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

        # 验证MIME类型与扩展名是否匹配（安全检查）
        if not self._validate_mime_type(mime_type, file_extension):
            raise HTTPException(status_code=400, detail="文件类型与扩展名不匹配，可能存在安全风险")

        return {
            "content": content,
            "size": file_size,
            "extension": file_extension,
            "mime_type": mime_type,
            "file_type": self.file_type_mapping.get(file_extension, FileType.OTHER),
        }

    def _validate_mime_type(self, mime_type: str, extension: str) -> bool:
        """验证MIME类型与文件扩展名是否匹配"""
        mime_mapping = {
            ".jpg": ["image/jpeg"],
            ".jpeg": ["image/jpeg"],
            ".png": ["image/png"],
            ".gif": ["image/gif"],
            ".pdf": ["application/pdf"],
            ".txt": ["text/plain"],
            ".doc": ["application/msword"],
            ".docx": [
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ],
            # 添加更多映射...
        }

        expected_mimes = mime_mapping.get(extension, [])
        if expected_mimes and mime_type not in expected_mimes:
            return False
        return True

    async def save_file(
        self, file: UploadFile, user_id: str, is_public: bool = False
    ) -> FileInfo:
        """保存文件到文件系统和数据库"""
        # 验证文件
        file_info = await self.validate_file(file)

        # 生成唯一文件ID和文件名
        file_id_obj = uuid.uuid4()
        file_id = str(file_id_obj)
        file_extension = file_info["extension"]
        new_filename = f"{file_id}{file_extension}"

        # 确定保存路径
        file_type = file_info["file_type"]
        if file_type == FileType.IMAGE:
            subdirectory = "images"
        elif file_type == FileType.ARCHIVE:
            subdirectory = "archives"
        else:
            subdirectory = "documents"

        file_path = os.path.join(self.upload_dir, subdirectory, new_filename)

        try:
            # 创建数据库记录
            db_file = UploadedFile(
                id=file_id_obj,
                user_id=self._coerce_uuid(user_id),
                original_name=file.filename,
                file_name=new_filename,
                file_path=file_path,
                file_size=file_info["size"],
                mime_type=file_info["mime_type"],
                file_type=file_type,
                status=FileStatus.UPLOADING,
                is_public=is_public,
            )

            self.db.add(db_file)
            await self.db.flush()  # 获取ID但不提交

            # 保存文件到磁盘
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(file_info["content"])

            # 处理图片（压缩和生成缩略图）
            thumbnail_path = None
            file_metadata = {}

            if file_type == FileType.IMAGE:
                thumbnail_path, metadata = await self._process_image(
                    file_path, file_id, file_extension
                )
                file_metadata = metadata
                db_file.thumbnail_path = thumbnail_path

            # 更新文件状态和元数据
            db_file.status = FileStatus.READY
            db_file.file_metadata = file_metadata

            await self.db.commit()

            # 构建返回信息
            file_url = f"/api/v1/files/download/{file_id}"
            thumbnail_url = (
                f"/api/v1/files/download/{file_id}_thumb" if thumbnail_path else None
            )

            return FileInfo(
                id=file_id,
                filename=new_filename,
                original_filename=file.filename,
                file_size=file_info["size"],
                file_type=file_info["mime_type"],
                file_extension=file_extension,
                file_url=file_url,
                thumbnail_url=thumbnail_url,
                upload_time=db_file.created_at,
            )

        except Exception as e:
            # 回滚数据库操作
            await self.db.rollback()
            # 删除已保存的文件
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

    async def _process_image(
        self, image_path: str, file_id: str, extension: str
    ) -> tuple[Optional[str], Dict[str, Any]]:
        """处理图片（压缩、格式转换和生成缩略图）"""
        metadata = {}
        thumbnail_path = None

        try:
            with Image.open(image_path) as img:
                # 记录原始图片信息
                original_width, original_height = img.size
                metadata.update(
                    {
                        "original_width": original_width,
                        "original_height": original_height,
                        "original_mode": img.mode,
                        "original_format": img.format,
                    }
                )

                # 自动旋转图片（基于EXIF信息）
                img = ImageOps.exif_transpose(img)

                # 转换为RGB模式（处理RGBA等格式）
                if img.mode in ("RGBA", "LA", "P"):
                    # 对于透明图片，创建白色背景
                    if img.mode == "RGBA":
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])  # 使用alpha通道作为mask
                        img = background
                    else:
                        img = img.convert("RGB")

                # 压缩原图（如果尺寸过大）
                max_width, max_height = 1920, 1080
                if img.width > max_width or img.height > max_height:
                    # 计算缩放比例，保持宽高比
                    ratio = min(max_width / img.width, max_height / img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                    # 保存压缩后的图片
                    save_format = (
                        "JPEG" if extension.lower() in [".jpg", ".jpeg"] else "PNG"
                    )
                    img.save(image_path, format=save_format, quality=85, optimize=True)

                    metadata.update(
                        {
                            "compressed": True,
                            "final_width": new_size[0],
                            "final_height": new_size[1],
                        }
                    )
                else:
                    metadata.update(
                        {
                            "compressed": False,
                            "final_width": original_width,
                            "final_height": original_height,
                        }
                    )

                # 生成缩略图
                thumbnail_img = img.copy()
                thumbnail_img.thumbnail((300, 300), Image.Resampling.LANCZOS)

                # 缩略图始终保存为JPEG格式以减小文件大小
                thumbnail_filename = f"{file_id}_thumb.jpg"
                thumbnail_full_path = os.path.join(
                    self.upload_dir, "thumbnails", thumbnail_filename
                )
                thumbnail_img.save(
                    thumbnail_full_path, format="JPEG", quality=80, optimize=True
                )

                thumbnail_path = thumbnail_full_path
                metadata.update(
                    {
                        "thumbnail_width": thumbnail_img.width,
                        "thumbnail_height": thumbnail_img.height,
                        "thumbnail_size": os.path.getsize(thumbnail_full_path),
                    }
                )

        except Exception as e:
            print(f"图片处理失败: {e}")
            metadata["processing_error"] = str(e)

        return thumbnail_path, metadata

    async def get_file_by_id(self, file_id: str) -> Optional[UploadedFile]:
        """根据ID获取文件记录"""
        # 处理缩略图请求
        if file_id.endswith("_thumb"):
            base_id = file_id.replace("_thumb", "")
            base_uuid = self._coerce_uuid(base_id)
            if base_uuid is None:
                return None
            result = await self.db.execute(
                select(UploadedFile).where(UploadedFile.id == base_uuid)
            )
            return result.scalar_one_or_none()

        file_uuid = self._coerce_uuid(file_id)
        if file_uuid is None:
            return None
        result = await self.db.execute(
            select(UploadedFile).where(UploadedFile.id == file_uuid)
        )
        return result.scalar_one_or_none()

    async def get_file_path(self, file_id: str) -> Optional[str]:
        """获取文件路径"""
        # 检查是否是缩略图请求
        if file_id.endswith("_thumb"):
            base_id = file_id.replace("_thumb", "")
            db_file = await self.get_file_by_id(base_id)
            if db_file and db_file.thumbnail_path:
                return db_file.thumbnail_path
            return None

        # 获取普通文件
        db_file = await self.get_file_by_id(file_id)
        if db_file and os.path.exists(db_file.file_path):
            return db_file.file_path

        return None

    async def delete_file(
        self, file_id: str, user_id: str, can_delete_any: bool = False
    ) -> bool:
        """删除文件（包括数据库记录和物理文件）"""
        try:
            # 获取文件记录
            db_file = await self.get_file_by_id(file_id)
            if not db_file:
                raise HTTPException(status_code=404, detail="文件不存在")

            # 检查权限（只有文件上传者可以删除）
            user_uuid = self._coerce_uuid(user_id)
            if db_file.user_id != user_uuid and not can_delete_any:
                raise HTTPException(status_code=403, detail="无权限删除此文件")

            # 删除物理文件
            if os.path.exists(db_file.file_path):
                os.remove(db_file.file_path)

            # 删除缩略图
            if db_file.thumbnail_path and os.path.exists(db_file.thumbnail_path):
                os.remove(db_file.thumbnail_path)

            # 删除数据库记录
            await self.db.delete(db_file)
            await self.db.commit()

            return True
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")

    async def get_user_files(
        self,
        user_id: str,
        file_type: Optional[FileType] = None,
        page: int = 1,
        size: int = 20,
    ) -> Dict[str, Any]:
        """获取用户的文件列表"""
        offset = (page - 1) * size

        user_uuid = self._coerce_uuid(user_id)
        if user_uuid is None:
            return {"files": [], "total": 0, "page": page, "size": size, "pages": 0}

        query = select(UploadedFile).where(UploadedFile.user_id == user_uuid)
        if file_type:
            query = query.where(UploadedFile.file_type == file_type)

        # 获取总数
        count_result = await self.db.execute(
            select(func.count(UploadedFile.id)).where(UploadedFile.user_id == user_uuid)
        )
        total = count_result.scalar()

        # 获取分页数据
        query = (
            query.order_by(UploadedFile.created_at.desc()).offset(offset).limit(size)
        )
        result = await self.db.execute(query)
        files = result.scalars().all()

        return {
            "files": [
                {
                    "id": str(db_file.id),
                    "original_name": db_file.original_name,
                    "file_name": db_file.file_name,
                    "file_size": db_file.file_size,
                    "mime_type": db_file.mime_type,
                    "file_type": db_file.file_type.value,
                    "status": db_file.status.value,
                    "download_count": db_file.download_count,
                    "is_public": db_file.is_public,
                    "metadata": db_file.file_metadata,
                    "created_at": db_file.created_at,
                    "updated_at": db_file.updated_at,
                    "file_url": f"/api/v1/files/download/{db_file.id}",
                    "thumbnail_url": (
                        f"/api/v1/files/download/{db_file.id}_thumb"
                        if db_file.thumbnail_path
                        else None
                    ),
                }
                for db_file in files
            ],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
        }

    async def update_download_count(self, file_id: str):
        """更新文件下载次数"""
        try:
            db_file = await self.get_file_by_id(file_id)
            if db_file:
                db_file.download_count += 1
                await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            # 下载计数更新失败不应该影响文件下载，所以只记录日志
            print(f"更新下载次数失败: {str(e)}")
