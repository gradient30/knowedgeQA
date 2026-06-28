import os
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.files.services import FileService
from app.modules.files.schemas import FileUploadResponse, FileInfo
from app.modules.files.models import FileType
from app.modules.users.models import User, UserRole
from app.modules.users.services import (
    AuthService,
    get_auth_service,
    get_current_active_user,
)

router = APIRouter()
optional_security = HTTPBearer(auto_error=False)


async def get_optional_active_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[User]:
    if credentials is None:
        return None

    current_user = await auth_service.get_current_user(credentials.credentials)
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账户已被禁用")
    return current_user


def can_access_file(db_file, current_user: Optional[User]) -> bool:
    if db_file.is_public:
        return True
    if current_user is None:
        return False
    if db_file.user_id == current_user.id:
        return True
    return current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]


def ensure_file_access(db_file, current_user: Optional[User]) -> None:
    if not can_access_file(db_file, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问此文件")


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    is_public: bool = Query(False, description="是否公开文件"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    文件上传接口
    支持图片、文档、压缩包等文件类型
    - 自动压缩大尺寸图片
    - 生成缩略图
    - 文件类型和大小验证
    - 安全性检查
    """
    try:
        file_service = FileService(db)

        # 保存文件
        file_info = await file_service.save_file(file, str(current_user.id), is_public)

        return FileUploadResponse(success=True, message="文件上传成功", file_info=file_info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


@router.post("/upload-multiple", response_model=List[FileUploadResponse])
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    is_public: bool = Query(False, description="是否公开文件"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    批量文件上传接口
    支持同时上传多个文件，每个文件独立处理
    """
    file_service = FileService(db)

    results = []
    for file in files:
        try:
            file_info = await file_service.save_file(
                file, str(current_user.id), is_public
            )
            results.append(
                FileUploadResponse(success=True, message="文件上传成功", file_info=file_info)
            )
        except Exception as e:
            results.append(
                FileUploadResponse(success=False, message=str(e), file_info=None)
            )
    return results


@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: Optional[User] = Depends(get_optional_active_user),
):
    """
    文件下载接口
    支持普通文件和缩略图下载
    """
    file_service = FileService(db)

    db_file = await file_service.get_file_by_id(file_id)
    file_path = await file_service.get_file_path(file_id)
    if not db_file or not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    ensure_file_access(db_file, current_user)

    # 更新下载次数（仅对非缩略图文件）
    if not file_id.endswith("_thumb"):
        await file_service.update_download_count(file_id)

    # 获取原始文件名
    filename = db_file.original_name if db_file else os.path.basename(file_path)

    return FileResponse(
        path=file_path, filename=filename, media_type="application/octet-stream"
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    删除文件接口
    只有文件上传者可以删除自己的文件
    """
    file_service = FileService(db)
    can_delete_any = current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

    await file_service.delete_file(file_id, str(current_user.id), can_delete_any)
    return {"message": "文件删除成功"}


@router.get("/list", response_model=dict)
async def list_user_files(
    file_type: Optional[FileType] = Query(None, description="文件类型过滤"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取用户文件列表
    支持按文件类型过滤和分页
    """
    file_service = FileService(db)

    result = await file_service.get_user_files(
        str(current_user.id), file_type, page, size
    )
    return result


@router.get("/info/{file_id}", response_model=dict)
async def get_file_info(
    file_id: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: Optional[User] = Depends(get_optional_active_user),
):
    """
    获取文件详细信息
    """
    file_service = FileService(db)
    db_file = await file_service.get_file_by_id(file_id)

    if not db_file:
        raise HTTPException(status_code=404, detail="文件不存在")

    ensure_file_access(db_file, current_user)

    return {
        "id": str(db_file.id),
        "original_name": db_file.original_name,
        "file_name": db_file.file_name,
        "file_size": db_file.file_size,
        "mime_type": db_file.mime_type,
        "file_type": db_file.file_type,
        "status": db_file.status,
        "download_count": db_file.download_count,
        "is_public": db_file.is_public,
        "metadata": db_file.file_metadata,
        "created_at": db_file.created_at,
        "updated_at": db_file.updated_at,
        "file_url": f"/api/v1/files/download/{db_file.id}",
        "thumbnail_url": f"/api/v1/files/download/{db_file.id}_thumb"
        if db_file.thumbnail_path
        else None,
    }


@router.get("/avatars/{filename}")
async def get_avatar(filename: str):
    """
    获取用户头像
    """
    avatar_path = f"uploads/avatars/{filename}"

    if not os.path.exists(avatar_path):
        raise HTTPException(status_code=404, detail="头像文件不存在")

    return FileResponse(path=avatar_path, media_type="image/jpeg")
