from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
import io
import json
import csv
from datetime import datetime

from app.modules.users.schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    PasswordReset, PasswordResetConfirm, EmailVerification,
    UserUpdate, UserStats, PasswordChange, AvatarUpload, UserDataExport,
    TeamCreate, TeamUpdate, TeamResponse, TeamInvitation, TeamMemberUpdate, TeamStats,
    EmailChangeRequest, EmailChangeConfirm
)
from app.modules.users.services import (
    AuthService, get_auth_service, get_current_active_user,
    require_admin, require_super_admin
)
from app.modules.users.models import User, UserRole

router = APIRouter()


# 认证相关路由
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    用户注册
    
    - **username**: 用户名 (3-50字符)
    - **email**: 邮箱地址
    - **password**: 密码 (最少8字符)
    - **nickname**: 昵称 (可选)
    - **bio**: 个人简介 (可选)
    - **role**: 用户角色 (默认为member)
    - **team_id**: 团队ID (可选)
    """
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    用户登录
    
    - **email**: 邮箱地址
    - **password**: 密码
    
    返回访问令牌和用户信息
    """
    result = await auth_service.authenticate_user(login_data)
    return TokenResponse(**result)


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    verification_data: EmailVerification,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    验证邮箱
    
    - **token**: 邮箱验证令牌
    """
    success = await auth_service.verify_email(verification_data.token)
    return {"message": "邮箱验证成功" if success else "邮箱验证失败"}


@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(
    reset_request: PasswordReset,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    请求密码重置
    
    - **email**: 邮箱地址
    """
    await auth_service.request_password_reset(reset_request.email)
    return {"message": "如果邮箱存在，重置链接已发送"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    重置密码
    
    - **token**: 重置令牌
    - **new_password**: 新密码
    """
    success = await auth_service.reset_password(reset_data.token, reset_data.new_password)
    return {"message": "密码重置成功" if success else "密码重置失败"}


# 用户信息相关路由
@router.get("/profile", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户个人资料"""
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    更新个人资料
    
    - **nickname**: 昵称
    - **bio**: 个人简介
    - **avatar_url**: 头像URL
    """
    return await auth_service.update_user_profile(current_user.id, update_data)


@router.get("/profile/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """获取用户统计信息"""
    return await auth_service.get_user_stats(current_user.id)


@router.post("/profile/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    修改密码
    
    - **current_password**: 当前密码
    - **new_password**: 新密码（至少8字符）
    """
    await auth_service.change_password(
        current_user.id, 
        password_data.current_password, 
        password_data.new_password
    )
    return {"message": "密码修改成功"}


@router.post("/profile/request-email-change", status_code=status.HTTP_200_OK)
async def request_email_change(
    email_change_data: EmailChangeRequest,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    请求修改邮箱
    
    - **new_email**: 新邮箱地址
    - **password**: 当前密码
    """
    await auth_service.request_email_change(
        current_user.id,
        email_change_data.new_email,
        email_change_data.password
    )
    return {"message": "邮箱修改验证邮件已发送到新邮箱"}


@router.post("/profile/confirm-email-change", status_code=status.HTTP_200_OK)
async def confirm_email_change(
    confirm_data: EmailChangeConfirm,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    确认邮箱修改
    
    - **token**: 邮箱修改验证令牌
    """
    await auth_service.confirm_email_change(confirm_data.token)
    return {"message": "邮箱修改成功"}


@router.post("/profile/upload-avatar", response_model=AvatarUpload)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    上传头像
    
    - **file**: 头像文件（支持 JPG, PNG, GIF 格式，最大 2MB）
    """
    avatar_url = await auth_service.upload_avatar(current_user.id, file)
    return AvatarUpload(avatar_url=avatar_url)


@router.post("/profile/export-data")
async def export_user_data(
    export_request: UserDataExport,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    导出用户数据
    
    - **format**: 导出格式（json 或 csv）
    - **include_articles**: 是否包含文章
    - **include_comments**: 是否包含评论
    - **include_profile**: 是否包含个人资料
    """
    data = await auth_service.export_user_data(current_user.id, export_request)
    
    if export_request.format.lower() == "csv":
        # CSV 格式导出
        output = io.StringIO()
        
        # 创建CSV内容
        csv_data = []
        
        # 添加个人资料信息
        if export_request.include_profile and data.get("profile"):
            profile = data["profile"]
            csv_data.append({
                "数据类型": "个人资料",
                "标题": "用户信息",
                "内容": f"用户名: {profile.get('username', '')}, 邮箱: {profile.get('email', '')}, 昵称: {profile.get('nickname', '')}, 角色: {profile.get('role', '')}",
                "创建时间": profile.get("created_at", ""),
                "更新时间": profile.get("updated_at", ""),
                "其他信息": f"验证状态: {'已验证' if profile.get('is_verified') else '未验证'}, 活跃状态: {'活跃' if profile.get('is_active') else '非活跃'}"
            })
        
        # 添加文章信息
        if export_request.include_articles and data.get("articles"):
            for article in data["articles"]:
                csv_data.append({
                    "数据类型": "文章",
                    "标题": article.get("title", ""),
                    "内容": article.get("content", "")[:100] + "..." if len(article.get("content", "")) > 100 else article.get("content", ""),
                    "创建时间": article.get("created_at", ""),
                    "更新时间": article.get("updated_at", ""),
                    "其他信息": f"分类: {article.get('category', '')}, 标签: {', '.join(article.get('tags', []))}, 浏览: {article.get('view_count', 0)}, 点赞: {article.get('like_count', 0)}"
                })
        
        # 添加评论信息
        if export_request.include_comments and data.get("comments"):
            for comment in data["comments"]:
                csv_data.append({
                    "数据类型": "评论",
                    "标题": f"评论 - {comment.get('id', '')}",
                    "内容": comment.get("content", ""),
                    "创建时间": comment.get("created_at", ""),
                    "更新时间": comment.get("updated_at", ""),
                    "其他信息": f"文章ID: {comment.get('article_id', '')}, 点赞: {comment.get('like_count', 0)}"
                })
        
        # 写入CSV
        if csv_data:
            fieldnames = ["数据类型", "标题", "内容", "创建时间", "更新时间", "其他信息"]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
        else:
            # 如果没有数据，写入一个说明行
            writer = csv.writer(output)
            writer.writerow(["数据类型", "说明"])
            writer.writerow(["导出结果", "没有找到符合条件的数据"])
        
        response = StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8-sig")),  # 使用utf-8-sig支持中文
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=user_data_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    else:
        # JSON 格式导出
        json_data = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        response = StreamingResponse(
            io.BytesIO(json_data.encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=user_data_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.json"}
        )
    
    return response


@router.get("/profile/export-stats")
async def get_export_stats(
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    获取用户数据导出统计信息
    """
    stats = await auth_service.get_user_stats(current_user.id)
    
    # 估算数据大小
    estimated_sizes = {
        "profile": "< 1KB",
        "articles": f"约 {stats.articles_count * 2}KB" if stats.articles_count > 0 else "< 1KB",
        "comments": f"约 {stats.comments_count * 0.5}KB" if stats.comments_count > 0 else "< 1KB"
    }
    
    return {
        "user_stats": {
            "articles_count": stats.articles_count,
            "comments_count": stats.comments_count,
            "likes_received": stats.likes_received,
            "tools_rated": stats.tools_rated
        },
        "estimated_sizes": estimated_sizes,
        "available_formats": ["json", "csv"],
        "last_export": None,  # TODO: 实现导出历史记录
        "export_limit": {
            "daily": 5,
            "monthly": 30
        }
    }


# 管理员功能
@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 20,
    admin_user: User = Depends(require_admin)
):
    """获取用户列表 (管理员权限)"""
    # TODO: 实现用户列表查询
    return []


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    admin_user: User = Depends(require_admin)
):
    """根据ID获取用户信息 (管理员权限)"""
    # TODO: 实现根据ID查询用户
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.put("/{user_id}/role")
async def update_user_role(
    user_id: str,
    new_role: UserRole,
    super_admin: User = Depends(require_super_admin)
):
    """更新用户角色 (超级管理员权限)"""
    # TODO: 实现用户角色更新
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.put("/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    admin_user: User = Depends(require_admin)
):
    """更新用户状态 (管理员权限)"""
    # TODO: 实现用户状态更新
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


# 团队管理相关路由
@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    创建团队
    
    - **name**: 团队名称
    - **description**: 团队描述（可选）
    - **leader_id**: 团队负责人ID（可选，默认为创建者）
    - **settings**: 团队设置（可选）
    """
    return await auth_service.create_team(team_data, current_user.id)


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: UUID,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """获取团队信息"""
    team = await auth_service.get_team_by_id(team_id)
    
    # 检查访问权限：只有团队成员或管理员可以查看
    if (current_user.team_id != team_id and 
        current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return team


@router.put("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: UUID,
    update_data: TeamUpdate,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    更新团队信息
    
    只有团队负责人或管理员可以更新团队信息
    """
    return await auth_service.update_team(team_id, update_data, current_user.id)


@router.post("/teams/{team_id}/invite", status_code=status.HTTP_200_OK)
async def invite_team_member(
    team_id: UUID,
    invitation: TeamInvitation,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    邀请团队成员
    
    - **email**: 被邀请用户的邮箱
    - **role**: 用户角色
    - **message**: 邀请消息（可选）
    """
    await auth_service.invite_team_member(team_id, invitation, current_user.id)
    return {"message": "邀请发送成功"}


@router.delete("/teams/{team_id}/members/{member_id}", status_code=status.HTTP_200_OK)
async def remove_team_member(
    team_id: UUID,
    member_id: UUID,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """移除团队成员"""
    await auth_service.remove_team_member(team_id, member_id, current_user.id)
    return {"message": "成员移除成功"}


@router.put("/teams/{team_id}/members/{member_id}/role", status_code=status.HTTP_200_OK)
async def update_team_member_role(
    team_id: UUID,
    member_id: UUID,
    role_update: TeamMemberUpdate,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """更新团队成员角色"""
    await auth_service.update_team_member_role(team_id, member_id, role_update, current_user.id)
    return {"message": "角色更新成功"}


@router.get("/teams/{team_id}/stats", response_model=TeamStats)
async def get_team_stats(
    team_id: UUID,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """获取团队统计信息"""
    # 检查访问权限
    if (current_user.team_id != team_id and 
        current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return await auth_service.get_team_stats(team_id)


@router.post("/teams/leave", status_code=status.HTTP_200_OK)
async def leave_team(
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """离开当前团队"""
    await auth_service.leave_team(current_user.id)
    return {"message": "已成功离开团队"}


@router.get("/profile/team", response_model=TeamResponse)
async def get_current_user_team(
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """获取当前用户的团队信息"""
    if not current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未加入任何团队"
        )
    
    return await auth_service.get_team_by_id(current_user.team_id)