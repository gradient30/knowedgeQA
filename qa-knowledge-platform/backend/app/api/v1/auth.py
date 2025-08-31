from fastapi import APIRouter, Depends, status

from app.modules.users.schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    PasswordReset, PasswordResetConfirm, EmailVerification
)
from app.modules.users.services import AuthService, get_auth_service, get_current_active_user
from app.modules.users.models import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    用户注册
    
    创建新用户账户并发送邮箱验证邮件。
    
    **请求参数:**
    - **username**: 用户名 (3-50字符，唯一)
    - **email**: 邮箱地址 (唯一)
    - **password**: 密码 (最少8字符)
    - **nickname**: 昵称 (可选，默认为用户名)
    - **bio**: 个人简介 (可选)
    - **role**: 用户角色 (默认为member)
    - **team_id**: 团队ID (可选)
    
    **响应:**
    - 返回创建的用户信息
    - 自动发送邮箱验证邮件
    
    **错误码:**
    - 400: 用户名或邮箱已存在
    """
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    用户登录
    
    验证用户凭据并返回访问令牌。
    
    **请求参数:**
    - **email**: 邮箱地址
    - **password**: 密码
    
    **响应:**
    - **access_token**: JWT访问令牌
    - **token_type**: 令牌类型 (bearer)
    - **expires_in**: 令牌过期时间 (秒)
    - **user**: 用户信息
    
    **安全特性:**
    - 登录失败5次后账户锁定15分钟
    - 更新最后登录时间
    
    **错误码:**
    - 401: 邮箱或密码错误、账户被禁用
    - 429: 登录失败次数过多
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
    
    使用邮箱验证令牌激活用户账户。
    
    **请求参数:**
    - **token**: 邮箱验证令牌 (从邮件中获取)
    
    **响应:**
    - 成功消息
    
    **注意:**
    - 验证令牌24小时内有效
    - 验证成功后令牌自动失效
    
    **错误码:**
    - 400: 验证令牌无效或已过期
    - 404: 用户不存在
    """
    success = await auth_service.verify_email(verification_data.token)
    return {"message": "邮箱验证成功", "verified": success}


@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(
    reset_request: PasswordReset,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    请求密码重置
    
    发送密码重置邮件到指定邮箱。
    
    **请求参数:**
    - **email**: 邮箱地址
    
    **响应:**
    - 统一成功消息 (无论邮箱是否存在)
    
    **安全特性:**
    - 即使邮箱不存在也返回成功消息
    - 重置令牌1小时内有效
    
    **注意:**
    - 为了安全考虑，不会透露邮箱是否存在
    """
    await auth_service.request_password_reset(reset_request.email)
    return {"message": "如果邮箱存在，重置链接已发送到您的邮箱"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    重置密码
    
    使用重置令牌设置新密码。
    
    **请求参数:**
    - **token**: 密码重置令牌 (从邮件中获取)
    - **new_password**: 新密码 (最少8字符)
    
    **响应:**
    - 成功消息
    
    **注意:**
    - 重置令牌1小时内有效
    - 重置成功后令牌自动失效
    
    **错误码:**
    - 400: 重置令牌无效或已过期
    - 404: 用户不存在
    """
    success = await auth_service.reset_password(reset_data.token, reset_data.new_password)
    return {"message": "密码重置成功", "reset": success}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """
    用户登出
    
    客户端应删除本地存储的令牌。
    
    **注意:**
    - JWT令牌是无状态的，服务端不需要特殊处理
    - 客户端负责删除本地令牌
    """
    return {"message": "登出成功"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户信息
    
    根据令牌获取当前登录用户的详细信息。
    
    **响应:**
    - 当前用户的完整信息
    
    **错误码:**
    - 401: 令牌无效或已过期
    - 404: 用户不存在
    """
    return UserResponse.model_validate(current_user)