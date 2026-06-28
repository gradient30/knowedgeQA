from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from uuid import UUID

from app.modules.users.models import UserRole, ProfessionalRole, ExperienceLevel


class UserBase(BaseModel):
    """用户基础信息"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")
    bio: Optional[str] = Field(None, description="个人简介")


class UserCreate(UserBase):
    """用户注册请求"""
    password: str = Field(..., min_length=8, max_length=100, description="密码")
    role: Optional[UserRole] = Field(UserRole.MEMBER, description="系统角色")
    professional_role: Optional[ProfessionalRole] = Field(ProfessionalRole.TEST_ENGINEER, description="职业角色")
    experience_level: Optional[ExperienceLevel] = Field(ExperienceLevel.JUNIOR, description="工作经验")
    specialties: Optional[List[str]] = Field(None, description="专业领域")
    team_id: Optional[UUID] = Field(None, description="团队ID")


class UserLogin(BaseModel):
    """用户登录请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """用户信息更新"""
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")
    bio: Optional[str] = Field(None, description="个人简介（支持Markdown格式）")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    professional_role: Optional[ProfessionalRole] = Field(None, description="职业角色")
    experience_level: Optional[ExperienceLevel] = Field(None, description="工作经验")
    specialties: Optional[List[str]] = Field(None, description="专业领域")
    skills: Optional[dict] = Field(None, description="技能信息")


class PasswordChange(BaseModel):
    """密码修改请求"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=8, max_length=100, description="新密码")


class AvatarUpload(BaseModel):
    """头像上传响应"""
    avatar_url: str = Field(..., description="头像URL")


class UserDataExport(BaseModel):
    """用户数据导出请求"""
    format: str = Field("json", description="导出格式：json 或 csv")
    include_articles: bool = Field(True, description="是否包含文章")
    include_comments: bool = Field(True, description="是否包含评论")
    include_profile: bool = Field(True, description="是否包含个人资料")


# 团队相关模型
class TeamBase(BaseModel):
    """团队基础信息"""
    name: str = Field(..., min_length=1, max_length=100, description="团队名称")
    description: Optional[str] = Field(None, description="团队描述")


class TeamCreate(TeamBase):
    """创建团队请求"""
    leader_id: Optional[UUID] = Field(None, description="团队负责人ID")
    settings: Optional[dict] = Field(None, description="团队设置")


class TeamUpdate(BaseModel):
    """更新团队信息"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="团队名称")
    description: Optional[str] = Field(None, description="团队描述")
    leader_id: Optional[UUID] = Field(None, description="团队负责人ID")
    settings: Optional[dict] = Field(None, description="团队设置")


class TeamMemberInfo(BaseModel):
    """团队成员信息"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    nickname: Optional[str]
    email: str
    role: UserRole
    avatar_url: Optional[str]
    joined_at: datetime
    is_leader: bool = False

class TeamResponse(TeamBase):
    """团队信息响应"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    leader_id: Optional[UUID]
    settings: Optional[dict]
    created_at: datetime
    updated_at: Optional[datetime]
    member_count: int = 0
    leader: Optional["UserResponse"] = None
    members: List[TeamMemberInfo] = []

class TeamInvitation(BaseModel):
    """团队邀请"""
    email: str = Field(..., description="邀请用户的邮箱")
    role: UserRole = Field(UserRole.MEMBER, description="用户角色")
    message: Optional[str] = Field(None, description="邀请消息")


class TeamMemberUpdate(BaseModel):
    """更新团队成员"""
    role: UserRole = Field(..., description="用户角色")


class TeamStats(BaseModel):
    """团队统计信息"""
    total_members: int = 0
    active_members: int = 0
    total_articles: int = 0
    total_tools: int = 0
    recent_activity_count: int = 0


class UserResponse(UserBase):
    """用户信息响应"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: UserRole
    professional_role: Optional[ProfessionalRole]
    experience_level: Optional[ExperienceLevel]
    specialties: Optional[List[str]]
    team_id: Optional[UUID]
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class PasswordReset(BaseModel):
    """密码重置请求"""
    email: EmailStr = Field(..., description="邮箱地址")


class PasswordResetConfirm(BaseModel):
    """密码重置确认"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=8, max_length=100, description="新密码")


class EmailVerification(BaseModel):
    """邮箱验证"""
    token: str = Field(..., description="验证令牌")


class EmailChangeRequest(BaseModel):
    """邮箱修改请求"""
    new_email: EmailStr = Field(..., description="新邮箱地址")
    password: str = Field(..., description="当前密码")


class EmailChangeConfirm(BaseModel):
    """邮箱修改确认"""
    token: str = Field(..., description="验证令牌")


class UserStats(BaseModel):
    """用户统计信息"""
    articles_count: int = 0
    comments_count: int = 0
    likes_received: int = 0
    tools_rated: int = 0
