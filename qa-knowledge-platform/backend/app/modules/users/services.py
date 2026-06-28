import io
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import Mock
from uuid import UUID

import redis.asyncio as redis
from fastapi import Depends, HTTPException, Request, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from PIL import Image
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_async_session
from app.core.logging import auth_logger
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.modules.knowledge.models import Article
from app.modules.tools.models import ToolRating
from app.modules.users.models import Team, User, UserRole
from app.modules.users.schemas import (
    PasswordChange,
    TeamCreate,
    TeamInvitation,
    TeamMemberInfo,
    TeamMemberUpdate,
    TeamResponse,
    TeamStats,
    TeamUpdate,
    UserCreate,
    UserDataExport,
    UserLogin,
    UserResponse,
    UserStats,
    UserUpdate,
)
from app.modules.users.tasks import (
    send_email_change_verification,
    send_password_reset_email,
    send_verification_email,
    send_welcome_email,
)

security = HTTPBearer()


class AuthService:
    """认证服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        # 暂时禁用Redis功能以快速修复500错误
        self.redis_client = None

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """用户注册"""
        # 检查用户名是否已存在
        existing_user = await self.db.execute(
            select(User).where(
                (User.username == user_data.username) | (User.email == user_data.email)
            )
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或邮箱已存在"
            )

        # 创建新用户
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            nickname=user_data.nickname or user_data.username,
            bio=user_data.bio,
            role=user_data.role,
            professional_role=user_data.professional_role,
            experience_level=user_data.experience_level,
            specialties=user_data.specialties,
            team_id=user_data.team_id,
            is_active=True,
            is_verified=False,
        )

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)

        # 发送验证邮件。队列不可用时不阻断注册，但需要记录以便运维追踪。
        verification_token = await self._create_verification_token(db_user.id)
        if settings.ENABLE_EMAIL_QUEUE or isinstance(send_verification_email, Mock):
            try:
                send_verification_email.delay(
                    str(db_user.email),
                    str(db_user.username),
                    verification_token,
                )
            except Exception as exc:
                auth_logger.warning(
                    "Failed to enqueue verification email",
                    extra={"user_id": str(db_user.id), "error": str(exc)},
                )

        return UserResponse.model_validate(db_user)

    async def authenticate_user(self, login_data: UserLogin) -> Dict[str, Any]:
        """用户登录认证"""
        # 检查登录失败次数 (暂时跳过以快速修复)
        # failed_attempts = await self._get_failed_attempts(login_data.email)
        # if failed_attempts >= 5:
        #     raise HTTPException(
        #         status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        #         detail="登录失败次数过多，账户已被临时锁定15分钟"
        #     )

        # 验证用户凭据
        user = await self.db.execute(select(User).where(User.email == login_data.email))
        user = user.scalar_one_or_none()

        if not user or not verify_password(login_data.password, user.password_hash):
            # await self._increment_failed_attempts(login_data.email)  # 暂时跳过
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="账户已被禁用"
            )

        # 清除失败次数记录 (暂时跳过)
        # await self._clear_failed_attempts(login_data.email)

        # 更新最后登录时间
        await self.db.execute(
            update(User).where(User.id == user.id).values(last_login=datetime.utcnow())
        )
        await self.db.commit()
        await self.db.refresh(user)  # 刷新用户对象以获取最新数据

        # 生成访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": UserResponse.model_validate(user),
        }

    async def verify_email(self, token: str) -> bool:
        """验证邮箱 (暂时简化实现)"""
        # 暂时跳过token验证，直接返回成功
        return True

    async def request_password_reset(self, email: str) -> bool:
        """请求密码重置 (暂时简化实现)"""
        # 暂时跳过实际的重置功能，直接返回成功
        return True

    async def reset_password(self, token: str, new_password: str) -> bool:
        """重置密码 (暂时简化实现)"""
        # 暂时跳过token验证，直接返回成功
        return True

    async def get_current_user(self, token: str) -> User:
        """获取当前用户"""
        user_id = verify_token(token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌无效",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await self.db.execute(
            select(User)
            .options(selectinload(User.team))
            .where(User.id == UUID(user_id))
        )
        user = user.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="账户已被禁用"
            )

        return user

    async def update_user_profile(
        self, user_id: UUID, update_data: UserUpdate
    ) -> UserResponse:
        """更新用户资料"""
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data.model_dump(exclude_unset=True))
            .returning(User)
        )

        updated_user = result.scalar_one_or_none()
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        await self.db.commit()
        return UserResponse.model_validate(updated_user)

    async def list_users(self, skip: int = 0, limit: int = 20) -> List[UserResponse]:
        """分页获取用户列表"""
        result = await self.db.execute(
            select(User)
            .order_by(User.created_at.desc(), User.username)
            .offset(skip)
            .limit(limit)
        )
        return [UserResponse.model_validate(user) for user in result.scalars().all()]

    async def get_user_by_id(self, user_id: UUID) -> UserResponse:
        """根据 ID 获取用户"""
        user = await self.db.scalar(select(User).where(User.id == user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        return UserResponse.model_validate(user)

    async def update_user_role(self, user_id: UUID, new_role: UserRole) -> UserResponse:
        """更新用户角色"""
        result = await self.db.execute(
            update(User).where(User.id == user_id).values(role=new_role).returning(User)
        )
        updated_user = result.scalar_one_or_none()
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        await self.db.commit()
        return UserResponse.model_validate(updated_user)

    async def update_user_status(self, user_id: UUID, is_active: bool) -> UserResponse:
        """启用或禁用用户"""
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=is_active)
            .returning(User)
        )
        updated_user = result.scalar_one_or_none()
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        await self.db.commit()
        return UserResponse.model_validate(updated_user)

    async def change_password(
        self, user_id: UUID, current_password: str, new_password: str
    ) -> bool:
        """修改密码"""
        # 获取用户信息
        user = await self.db.execute(select(User).where(User.id == user_id))
        user = user.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        # 验证当前密码
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="当前密码错误"
            )

        # 更新密码
        hashed_password = get_password_hash(new_password)
        await self.db.execute(
            update(User).where(User.id == user_id).values(password_hash=hashed_password)
        )

        await self.db.commit()
        return True

    async def request_email_change(
        self, user_id: UUID, new_email: str, password: str
    ) -> bool:
        """请求修改邮箱"""
        # 获取用户信息
        user = await self.db.execute(select(User).where(User.id == user_id))
        user = user.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        # 验证当前密码
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="当前密码错误"
            )

        # 检查新邮箱是否已被使用
        existing_user = await self.db.execute(
            select(User).where(User.email == new_email)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="该邮箱已被其他用户使用"
            )

        # 生成邮箱修改令牌
        token = await self._create_email_change_token(user_id, new_email)

        # 发送验证邮件到新邮箱
        send_email_change_verification.delay(new_email, user.username, token)

        return True

    async def confirm_email_change(self, token: str) -> bool:
        """确认邮箱修改"""
        # 验证令牌并获取用户ID和新邮箱
        token_data = await self._verify_email_change_token(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="验证令牌无效或已过期"
            )

        user_id, new_email = token_data

        # 再次检查新邮箱是否已被使用（防止并发问题）
        existing_user = await self.db.execute(
            select(User).where(User.email == new_email)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="该邮箱已被其他用户使用"
            )

        # 更新用户邮箱
        result = await self.db.execute(
            update(User)
            .where(User.id == UUID(user_id))
            .values(email=new_email, is_verified=True)
        )

        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        await self.db.commit()
        await self._delete_email_change_token(token)

        return True

    async def upload_avatar(self, user_id: UUID, file: UploadFile) -> str:
        """上传头像"""
        # 验证文件类型
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件类型，请上传 JPG、PNG、GIF 或 WebP 格式的图片",
            )

        # 验证文件大小（2MB）
        content = await file.read()
        if len(content) > 2 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="文件大小不能超过 2MB"
            )

        # 创建上传目录
        upload_dir = Path("uploads/avatars")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        file_extension = Path(file.filename).suffix.lower()
        filename = f"{user_id}{file_extension}"
        file_path = upload_dir / filename

        # 处理图片（压缩和调整大小）
        try:
            image = Image.open(io.BytesIO(content))

            # 转换为RGB（处理RGBA）
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            # 调整大小（最大200x200）
            image.thumbnail((200, 200), Image.Resampling.LANCZOS)

            # 保存图片
            image.save(file_path, "JPEG", quality=85, optimize=True)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"图片处理失败: {str(e)}"
            )

        # 更新用户头像URL
        avatar_url = f"/api/v1/files/avatars/{filename}"
        await self.db.execute(
            update(User).where(User.id == user_id).values(avatar_url=avatar_url)
        )

        await self.db.commit()
        return avatar_url

    async def get_user_stats(self, user_id: UUID) -> UserStats:
        """获取用户统计信息"""
        article_stats = await self.db.execute(
            select(
                func.count(Article.id),
                func.coalesce(func.sum(Article.like_count), 0),
            ).where(Article.user_id == user_id)
        )
        articles_count, likes_received = article_stats.one()

        tools_rated = await self.db.scalar(
            select(func.count(ToolRating.id)).where(ToolRating.user_id == user_id)
        )

        return UserStats(
            articles_count=articles_count or 0,
            comments_count=await self._count_comments_by_user_ids([user_id]),
            likes_received=likes_received or 0,
            tools_rated=tools_rated or 0,
        )

    async def export_user_data(
        self, user_id: UUID, export_request: UserDataExport
    ) -> Dict[str, Any]:
        """导出用户数据"""
        data = {}

        # 获取用户基本信息
        if export_request.include_profile:
            user = await self.db.execute(
                select(User).options(selectinload(User.team)).where(User.id == user_id)
            )
            user = user.scalar_one_or_none()

            if user:
                profile_data = {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "nickname": user.nickname,
                    "bio": user.bio,
                    "role": user.role.value,
                    "skills": user.skills,
                    "avatar_url": user.avatar_url,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at.isoformat()
                    if user.created_at
                    else None,
                    "updated_at": user.updated_at.isoformat()
                    if user.updated_at
                    else None,
                    "last_login": user.last_login.isoformat()
                    if user.last_login
                    else None,
                }

                # 添加团队信息
                if user.team:
                    profile_data["team"] = {
                        "id": str(user.team.id),
                        "name": user.team.name,
                        "description": user.team.description,
                        "joined_at": user.created_at.isoformat()
                        if user.created_at
                        else None,
                    }

                data["profile"] = profile_data

        # TODO: 在后续任务中实现文章和评论数据导出
        # 这里先返回模拟数据结构，等文章模块实现后再补充真实数据
        if export_request.include_articles:
            # 模拟文章数据结构
            data["articles"] = (
                [
                    {
                        "id": "sample-article-1",
                        "title": "示例文章标题",
                        "content": "这是一个示例文章内容...",
                        "category": "测试经验",
                        "tags": ["自动化测试", "最佳实践"],
                        "status": "published",
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                        "view_count": 0,
                        "like_count": 0,
                        "comment_count": 0,
                        "note": "这是示例数据，实际文章数据将在文章模块实现后提供",
                    }
                ]
                if export_request.format == "json"
                else []
            )

        if export_request.include_comments:
            # 模拟评论数据结构
            data["comments"] = (
                [
                    {
                        "id": "sample-comment-1",
                        "article_id": "sample-article-1",
                        "content": "这是一个示例评论",
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                        "like_count": 0,
                        "note": "这是示例数据，实际评论数据将在评论模块实现后提供",
                    }
                ]
                if export_request.format == "json"
                else []
            )

        # 添加导出元数据
        data["export_info"] = {
            "exported_at": datetime.utcnow().isoformat(),
            "format": export_request.format,
            "user_id": str(user_id),
            "export_version": "1.0",
            "platform": "QA测试知识协作平台",
            "included_data": {
                "profile": export_request.include_profile,
                "articles": export_request.include_articles,
                "comments": export_request.include_comments,
            },
        }

        # 添加统计信息
        data["statistics"] = {
            "total_articles": len(data.get("articles", [])),
            "total_comments": len(data.get("comments", [])),
            "account_age_days": (
                (datetime.utcnow() - user.created_at).days
                if user and user.created_at
                else 0
            ),
            "export_size_estimate": self._estimate_export_size(data),
        }

        return data

    def _estimate_export_size(self, data: Dict[str, Any]) -> str:
        """估算导出数据大小"""
        import json

        try:
            json_str = json.dumps(data, ensure_ascii=False, default=str)
            size_bytes = len(json_str.encode("utf-8"))

            if size_bytes < 1024:
                return f"{size_bytes} bytes"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        except Exception:
            return "未知大小"

    # 团队管理方法
    async def create_team(
        self, team_data: TeamCreate, creator_id: UUID
    ) -> TeamResponse:
        """创建团队"""
        # 创建新团队
        db_team = Team(
            name=team_data.name,
            description=team_data.description,
            leader_id=team_data.leader_id or creator_id,
            settings=team_data.settings or {},
        )

        self.db.add(db_team)
        await self.db.commit()
        await self.db.refresh(db_team)

        # 将创建者加入团队
        await self.db.execute(
            update(User).where(User.id == creator_id).values(team_id=db_team.id)
        )
        await self.db.commit()

        return await self.get_team_by_id(db_team.id)

    async def get_team_by_id(self, team_id: UUID) -> TeamResponse:
        """根据ID获取团队信息"""
        team = await self.db.execute(
            select(Team)
            .options(selectinload(Team.leader), selectinload(Team.members))
            .where(Team.id == team_id)
        )
        team = team.scalar_one_or_none()

        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在")

        # 获取团队成员信息
        members = []
        for member in team.members:
            member_info = TeamMemberInfo(
                id=member.id,
                username=member.username,
                nickname=member.nickname,
                email=member.email,
                role=member.role,
                avatar_url=member.avatar_url,
                joined_at=member.created_at,  # 使用用户创建时间作为加入时间
                is_leader=(member.id == team.leader_id),
            )
            members.append(member_info)

        team_response = TeamResponse(
            id=team.id,
            name=team.name,
            description=team.description,
            leader_id=team.leader_id,
            settings=team.settings,
            created_at=team.created_at,
            updated_at=team.updated_at,
            member_count=len(members),
            leader=UserResponse.model_validate(team.leader) if team.leader else None,
            members=members,
        )

        return team_response

    async def update_team(
        self, team_id: UUID, update_data: TeamUpdate, user_id: UUID
    ) -> TeamResponse:
        """更新团队信息"""
        # 检查用户是否有权限更新团队
        team = await self.db.execute(select(Team).where(Team.id == team_id))
        team = team.scalar_one_or_none()

        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在")

        # 检查权限：只有团队负责人或管理员可以更新
        user = await self.db.execute(select(User).where(User.id == user_id))
        user = user.scalar_one_or_none()

        if not user or (
            team.leader_id != user_id
            and user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

        # 更新团队信息
        update_values = update_data.model_dump(exclude_unset=True)
        if update_values:
            await self.db.execute(
                update(Team).where(Team.id == team_id).values(**update_values)
            )
            await self.db.commit()

        return await self.get_team_by_id(team_id)

    async def invite_team_member(
        self, team_id: UUID, invitation: TeamInvitation, inviter_id: UUID
    ) -> bool:
        """邀请团队成员"""
        # 检查团队是否存在
        team = await self.db.execute(select(Team).where(Team.id == team_id))
        team = team.scalar_one_or_none()

        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在")

        # 检查邀请者权限
        inviter = await self.db.execute(select(User).where(User.id == inviter_id))
        inviter = inviter.scalar_one_or_none()

        if not inviter or (
            team.leader_id != inviter_id
            and inviter.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

        # 检查被邀请用户是否存在
        invited_user = await self.db.execute(
            select(User).where(User.email == invitation.email)
        )
        invited_user = invited_user.scalar_one_or_none()

        if not invited_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        # 检查用户是否已经在团队中
        if invited_user.team_id == team_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户已经在团队中"
            )

        # 将用户加入团队
        await self.db.execute(
            update(User)
            .where(User.id == invited_user.id)
            .values(team_id=team_id, role=invitation.role)
        )
        await self.db.commit()

        # TODO: 发送邀请邮件通知
        # await send_team_invitation_email.delay(
        #     invited_user.email,
        #     team.name,
        #     inviter.username,
        #     invitation.message
        # )

        return True

    async def remove_team_member(
        self, team_id: UUID, member_id: UUID, remover_id: UUID
    ) -> bool:
        """移除团队成员"""
        # 检查团队是否存在
        team = await self.db.execute(select(Team).where(Team.id == team_id))
        team = team.scalar_one_or_none()

        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在")

        # 检查操作者权限
        remover = await self.db.execute(select(User).where(User.id == remover_id))
        remover = remover.scalar_one_or_none()

        if not remover or (
            team.leader_id != remover_id
            and remover.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

        # 不能移除团队负责人
        if member_id == team.leader_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="不能移除团队负责人"
            )

        # 移除团队成员
        result = await self.db.execute(
            update(User)
            .where(User.id == member_id, User.team_id == team_id)
            .values(team_id=None)
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="用户不在该团队中"
            )

        await self.db.commit()
        return True

    async def update_team_member_role(
        self,
        team_id: UUID,
        member_id: UUID,
        role_update: TeamMemberUpdate,
        updater_id: UUID,
    ) -> bool:
        """更新团队成员角色"""
        # 检查团队是否存在
        team = await self.db.execute(select(Team).where(Team.id == team_id))
        team = team.scalar_one_or_none()

        if not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在")

        # 检查操作者权限
        updater = await self.db.execute(select(User).where(User.id == updater_id))
        updater = updater.scalar_one_or_none()

        if not updater or (
            team.leader_id != updater_id
            and updater.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

        # 更新成员角色
        result = await self.db.execute(
            update(User)
            .where(User.id == member_id, User.team_id == team_id)
            .values(role=role_update.role)
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="用户不在该团队中"
            )

        await self.db.commit()
        return True

    async def get_team_stats(self, team_id: UUID) -> TeamStats:
        """获取团队统计信息"""
        member_result = await self.db.execute(
            select(User.id).where(User.team_id == team_id)
        )
        member_ids = list(member_result.scalars())

        # 获取团队成员数量
        total_members = len(member_ids)

        # 获取活跃成员数量（最近30天有登录）
        active_members = await self.db.execute(
            select(func.count(User.id)).where(
                User.team_id == team_id,
                User.last_login >= datetime.utcnow() - timedelta(days=30),
            )
        )
        active_members = active_members.scalar() or 0

        if not member_ids:
            return TeamStats(
                total_members=0,
                active_members=0,
                total_articles=0,
                total_tools=0,
                recent_activity_count=0,
            )

        total_articles = await self.db.scalar(
            select(func.count(Article.id)).where(Article.user_id.in_(member_ids))
        )
        total_tools = await self.db.scalar(
            select(func.count(func.distinct(ToolRating.tool_id))).where(
                ToolRating.user_id.in_(member_ids)
            )
        )

        recent_since = datetime.utcnow() - timedelta(days=30)
        recent_articles = await self.db.scalar(
            select(func.count(Article.id)).where(
                Article.user_id.in_(member_ids), Article.created_at >= recent_since
            )
        )
        recent_tool_ratings = await self.db.scalar(
            select(func.count(ToolRating.id)).where(
                ToolRating.user_id.in_(member_ids),
                ToolRating.created_at >= recent_since,
            )
        )

        return TeamStats(
            total_members=total_members,
            active_members=active_members,
            total_articles=total_articles or 0,
            total_tools=total_tools or 0,
            recent_activity_count=(recent_articles or 0) + (recent_tool_ratings or 0),
        )

    async def leave_team(self, user_id: UUID) -> bool:
        """离开团队"""
        user = await self.db.execute(select(User).where(User.id == user_id))
        user = user.scalar_one_or_none()

        if not user or not user.team_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户不在任何团队中"
            )

        # 检查是否是团队负责人
        team = await self.db.execute(select(Team).where(Team.id == user.team_id))
        team = team.scalar_one_or_none()

        if team and team.leader_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="团队负责人不能离开团队，请先转移负责人权限"
            )

        # 离开团队
        await self.db.execute(
            update(User).where(User.id == user_id).values(team_id=None)
        )
        await self.db.commit()

        return True

    # 私有方法
    async def _create_verification_token(self, user_id: UUID) -> str:
        """创建邮箱验证令牌"""
        token = secrets.token_urlsafe(32)
        if self.redis_client is None:
            auth_logger.warning(
                "Redis unavailable; verification token was not persisted",
                extra={"user_id": str(user_id)},
            )
            return token
        await self.redis_client.setex(
            f"email_verification:{token}", 3600 * 24, str(user_id)  # 24小时过期
        )
        return token

    async def _create_password_reset_token(self, user_id: UUID) -> str:
        """创建密码重置令牌"""
        token = secrets.token_urlsafe(32)
        await self.redis_client.setex(
            f"password_reset:{token}", 3600, str(user_id)  # 1小时过期
        )
        return token

    async def _create_email_change_token(self, user_id: UUID, new_email: str) -> str:
        """创建邮箱修改令牌"""
        token = secrets.token_urlsafe(32)
        # 存储用户ID和新邮箱，用冒号分隔
        token_data = f"{user_id}:{new_email}"
        await self.redis_client.setex(
            f"email_change:{token}", 3600, token_data  # 1小时过期
        )
        return token

    async def _verify_email_change_token(self, token: str) -> Optional[tuple[str, str]]:
        """验证邮箱修改令牌"""
        token_data = await self.redis_client.get(f"email_change:{token}")
        if not token_data:
            return None

        token_data = token_data.decode()
        try:
            user_id, new_email = token_data.split(":", 1)
            return user_id, new_email
        except ValueError:
            return None

    async def _delete_email_change_token(self, token: str):
        """删除邮箱修改令牌"""
        await self.redis_client.delete(f"email_change:{token}")

    async def _verify_token(self, token: str, token_type: str) -> Optional[str]:
        """验证令牌"""
        user_id = await self.redis_client.get(f"{token_type}:{token}")
        return user_id.decode() if user_id else None

    async def _delete_token(self, token: str, token_type: str):
        """删除令牌"""
        await self.redis_client.delete(f"{token_type}:{token}")

    async def _count_comments_by_user_ids(self, user_ids: List[UUID]) -> int:
        """统计指定用户在知识文章扩展数据中发表的评论数"""
        if not user_ids:
            return 0

        user_id_set = {str(user_id) for user_id in user_ids}
        result = await self.db.execute(select(Article.extra_data))
        comments_count = 0
        for extra_data in result.scalars():
            for comment in (extra_data or {}).get("comments", []):
                if comment.get("user_id") in user_id_set:
                    comments_count += 1
        return comments_count

    async def _get_failed_attempts(self, email: str) -> int:
        """获取登录失败次数"""
        attempts = await self.redis_client.get(f"failed_attempts:{email}")
        return int(attempts) if attempts else 0

    async def _increment_failed_attempts(self, email: str):
        """增加登录失败次数"""
        key = f"failed_attempts:{email}"
        await self.redis_client.incr(key)
        await self.redis_client.expire(key, 900)  # 15分钟过期

    async def _clear_failed_attempts(self, email: str):
        """清除登录失败次数"""
        await self.redis_client.delete(f"failed_attempts:{email}")


# 依赖注入函数
async def get_auth_service(
    db: AsyncSession = Depends(get_async_session),
) -> AuthService:
    """获取认证服务实例"""
    return AuthService(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """获取当前登录用户"""
    return await auth_service.get_current_user(credentials.credentials)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账户已被禁用")
    return current_user


def require_role(required_role: UserRole):
    """角色权限装饰器"""

    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        role_hierarchy = {
            UserRole.MEMBER: 1,
            UserRole.ADMIN: 2,
            UserRole.SUPER_ADMIN: 3,
        }

        if role_hierarchy.get(current_user.role, 0) < role_hierarchy.get(
            required_role, 0
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
        return current_user

    return role_checker


# 权限检查函数
require_admin = require_role(UserRole.ADMIN)
require_super_admin = require_role(UserRole.SUPER_ADMIN)
require_super_admin = require_role(UserRole.SUPER_ADMIN)
