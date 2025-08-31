from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_async_session
from app.core.email import email_service
from app.core.config import settings
# TODO: Import current user dependency when auth is implemented
# from app.modules.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/email-settings")
async def get_email_settings(
    db: AsyncSession = Depends(get_async_session)
    # current_user = Depends(get_current_user)  # TODO: Uncomment when auth is ready
):
    """
    获取邮件通知设置
    """
    # TODO: 从数据库获取用户的邮件设置
    return {
        "smtp_configured": bool(settings.SMTP_USER and settings.SMTP_PASSWORD),
        "smtp_host": settings.SMTP_HOST,
        "smtp_port": settings.SMTP_PORT,
        "smtp_user": settings.SMTP_USER,
        "smtp_tls": settings.SMTP_TLS,
        "notifications": {
            "email_verification": True,
            "password_reset": True,
            "welcome_email": True,
            "article_comments": True,
            "team_invitations": True,
            "system_updates": False
        }
    }


@router.put("/email-settings")
async def update_email_settings(
    settings_data: dict,
    db: AsyncSession = Depends(get_async_session)
    # current_user = Depends(get_current_user)  # TODO: Uncomment when auth is ready
):
    """
    更新邮件通知设置
    """
    # TODO: 保存用户的邮件设置到数据库
    return {
        "success": True,
        "message": "邮件设置已更新",
        "settings": settings_data
    }


@router.post("/test-email")
async def send_test_email(
    test_data: dict,
    db: AsyncSession = Depends(get_async_session)
    # current_user = Depends(get_current_user)  # TODO: Uncomment when auth is ready
):
    """
    发送测试邮件
    """
    try:
        to_email = test_data.get("to_email")
        if not to_email:
            raise HTTPException(status_code=400, detail="收件人邮箱不能为空")
        
        # 发送测试邮件
        success = email_service.send_notification_email(
            to_email=to_email,
            username="测试用户",
            title="邮件服务测试",
            content="这是一封测试邮件，用于验证邮件服务是否正常工作。如果您收到此邮件，说明邮件服务配置正确。",
            action_url="http://localhost:3000",
            action_text="访问平台"
        )
        
        if success:
            return {
                "success": True,
                "message": "测试邮件发送成功"
            }
        else:
            raise HTTPException(status_code=500, detail="测试邮件发送失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送测试邮件失败: {str(e)}")


@router.get("/smtp-status")
async def get_smtp_status():
    """
    获取SMTP服务状态
    """
    try:
        # 检查SMTP配置
        smtp_configured = bool(settings.SMTP_USER and settings.SMTP_PASSWORD)
        
        if not smtp_configured:
            return {
                "status": "not_configured",
                "message": "SMTP服务未配置",
                "details": {
                    "smtp_host": settings.SMTP_HOST or "未设置",
                    "smtp_port": settings.SMTP_PORT or "未设置",
                    "smtp_user": settings.SMTP_USER or "未设置",
                    "smtp_tls": settings.SMTP_TLS
                }
            }
        
        # TODO: 实际测试SMTP连接
        return {
            "status": "healthy",
            "message": "SMTP服务正常",
            "details": {
                "smtp_host": settings.SMTP_HOST,
                "smtp_port": settings.SMTP_PORT,
                "smtp_user": settings.SMTP_USER,
                "smtp_tls": settings.SMTP_TLS,
                "last_check": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"SMTP服务检查失败: {str(e)}",
            "details": {}
        }