from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_session
from app.core.email import email_service
from app.modules.notifications.models import (
    EmailLog,
    EmailLogStatus,
    NotificationSettings,
)
from app.modules.users.models import User
from app.modules.users.services import require_admin

router = APIRouter()

DEFAULT_NOTIFICATIONS = {
    "email_verification": True,
    "password_reset": True,
    "welcome_email": True,
    "article_comments": True,
    "team_invitations": True,
    "system_updates": False,
}

EMAIL_TEMPLATES = [
    {
        "id": "verification",
        "name": "邮箱验证",
        "description": "用户注册后验证邮箱地址。",
        "variables": ["username", "verification_url", "token"],
    },
    {
        "id": "password_reset",
        "name": "密码重置",
        "description": "用户发起密码重置时发送安全链接。",
        "variables": ["username", "reset_url", "token"],
    },
    {
        "id": "welcome",
        "name": "欢迎邮件",
        "description": "用户完成邮箱验证后发送平台入口和功能说明。",
        "variables": ["username", "platform_url"],
    },
    {
        "id": "email_change",
        "name": "邮箱修改",
        "description": "用户修改邮箱时验证新邮箱地址。",
        "variables": ["username", "verification_url", "token"],
    },
    {
        "id": "notification",
        "name": "通知邮件",
        "description": "文章评论、团队邀请、系统更新等运营通知。",
        "variables": ["username", "title", "content", "action_url", "action_text"],
    },
]


async def get_or_create_settings(db: AsyncSession) -> NotificationSettings:
    settings_row = await db.scalar(
        select(NotificationSettings).where(NotificationSettings.scope == "global")
    )
    if settings_row:
        return settings_row

    settings_row = NotificationSettings(
        scope="global", notifications=DEFAULT_NOTIFICATIONS.copy()
    )
    db.add(settings_row)
    await db.commit()
    await db.refresh(settings_row)
    return settings_row


def smtp_payload(notifications: Dict[str, bool]) -> Dict[str, Any]:
    return {
        "smtp_configured": bool(settings.SMTP_USER and settings.SMTP_PASSWORD),
        "smtp_host": settings.SMTP_HOST,
        "smtp_port": settings.SMTP_PORT,
        "smtp_user": settings.SMTP_USER,
        "smtp_tls": settings.SMTP_TLS,
        "notifications": notifications,
    }


def normalize_notifications(payload: Dict[str, Any]) -> Dict[str, bool]:
    notifications = payload.get("notifications")
    if not isinstance(notifications, dict):
        raise HTTPException(status_code=400, detail="notifications 必须是对象")

    normalized = DEFAULT_NOTIFICATIONS.copy()
    for key in DEFAULT_NOTIFICATIONS:
        value = notifications.get(key, normalized[key])
        if not isinstance(value, bool):
            raise HTTPException(status_code=400, detail=f"{key} 必须是布尔值")
        normalized[key] = value
    return normalized


def template_ids() -> set[str]:
    return {template["id"] for template in EMAIL_TEMPLATES}


async def write_email_log(
    db: AsyncSession,
    *,
    to_email: str,
    subject: str,
    template_name: str,
    status: EmailLogStatus,
    sent_by_id,
    error_message: str | None = None,
) -> EmailLog:
    log = EmailLog(
        to_email=to_email,
        subject=subject,
        template_name=template_name,
        status=status.value,
        error_message=error_message,
        sent_by_id=sent_by_id,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


@router.get("/email-settings")
async def get_email_settings(
    db: AsyncSession = Depends(get_async_session),
    admin_user: User = Depends(require_admin),
):
    """获取邮件通知设置"""
    settings_row = await get_or_create_settings(db)
    return smtp_payload(settings_row.notifications)


@router.put("/email-settings")
async def update_email_settings(
    settings_data: dict,
    db: AsyncSession = Depends(get_async_session),
    admin_user: User = Depends(require_admin),
):
    """更新邮件通知设置"""
    notifications = normalize_notifications(settings_data)
    settings_row = await get_or_create_settings(db)
    settings_row.notifications = notifications
    settings_row.updated_by_id = admin_user.id
    await db.commit()
    await db.refresh(settings_row)
    return {
        "success": True,
        "message": "邮件设置已更新",
        "settings": {"notifications": settings_row.notifications},
    }


@router.get("/email-templates")
async def get_email_templates(admin_user: User = Depends(require_admin)):
    """获取邮件模板列表"""
    return {"templates": EMAIL_TEMPLATES}


@router.post("/preview-template")
async def preview_template(
    preview_data: dict,
    admin_user: User = Depends(require_admin),
):
    """预览邮件模板"""
    template_name = preview_data.get("template_name")
    if template_name not in template_ids():
        raise HTTPException(status_code=404, detail="邮件模板不存在")

    html_content = email_service._create_fallback_template(
        template_name,
        username="QA经理",
        title="邮件模板预览",
        content="这是一封用于通知管理验收的模板预览邮件。",
        action_url="http://localhost:3000",
        action_text="访问平台",
        verification_url="http://localhost:3000/verify",
        reset_url="http://localhost:3000/reset-password",
        platform_url="http://localhost:3000",
        token="preview-token",
    )
    return {"html_content": html_content}


@router.post("/test-email")
async def send_test_email(
    test_data: dict,
    db: AsyncSession = Depends(get_async_session),
    admin_user: User = Depends(require_admin),
):
    """发送测试邮件并记录发送日志"""
    to_email = test_data.get("to_email")
    if not to_email:
        raise HTTPException(status_code=400, detail="收件人邮箱不能为空")

    subject = "QA测试知识协作平台 - 邮件服务测试"
    success = email_service.send_notification_email(
        to_email=to_email,
        username=admin_user.nickname or admin_user.username,
        title="邮件服务测试",
        content="这是一封测试邮件，用于验证邮件服务是否正常工作。",
        action_url="http://localhost:3000",
        action_text="访问平台",
    )

    await write_email_log(
        db,
        to_email=to_email,
        subject=subject,
        template_name="notification",
        status=EmailLogStatus.SUCCESS if success else EmailLogStatus.FAILED,
        sent_by_id=admin_user.id,
        error_message=None if success else "测试邮件发送失败",
    )

    if not success:
        raise HTTPException(status_code=500, detail="测试邮件发送失败")
    return {"success": True, "message": "测试邮件发送成功"}


@router.get("/email-logs")
async def get_email_logs(
    db: AsyncSession = Depends(get_async_session),
    admin_user: User = Depends(require_admin),
):
    """获取邮件发送日志"""
    result = await db.execute(
        select(EmailLog).order_by(EmailLog.sent_at.desc()).limit(50)
    )
    logs = result.scalars().all()
    return {
        "logs": [
            {
                "id": str(log.id),
                "to_email": log.to_email,
                "subject": log.subject,
                "template_name": log.template_name,
                "status": log.status,
                "sent_at": log.sent_at,
                "error_message": log.error_message,
            }
            for log in logs
        ]
    }


@router.get("/smtp-status")
async def get_smtp_status(admin_user: User = Depends(require_admin)):
    """获取SMTP服务状态"""
    try:
        smtp_configured = bool(settings.SMTP_USER and settings.SMTP_PASSWORD)
        if not smtp_configured:
            return {
                "status": "not_configured",
                "message": "SMTP服务未配置",
                "details": {
                    "smtp_host": settings.SMTP_HOST or "未设置",
                    "smtp_port": settings.SMTP_PORT or "未设置",
                    "smtp_user": settings.SMTP_USER or "未设置",
                    "smtp_tls": settings.SMTP_TLS,
                },
            }

        return {
            "status": "healthy",
            "message": "SMTP服务正常",
            "details": {
                "smtp_host": settings.SMTP_HOST,
                "smtp_port": settings.SMTP_PORT,
                "smtp_user": settings.SMTP_USER,
                "smtp_tls": settings.SMTP_TLS,
                "last_check": datetime.now().isoformat(),
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"SMTP服务检查失败: {str(e)}",
            "details": {},
        }
