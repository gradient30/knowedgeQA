from typing import Dict, Any
import logging

from app.core.celery_app import celery_app
from app.core.email import email_service

logger = logging.getLogger(__name__)


@celery_app.task
def send_verification_email(user_email: str, username: str, verification_token: str) -> Dict[str, Any]:
    """发送邮箱验证邮件任务"""
    try:
        success = email_service.send_verification_email(user_email, username, verification_token)
        
        return {
            "status": "success" if success else "failed",
            "email": user_email,
            "type": "verification"
        }
    except Exception as e:
        logger.error(f"验证邮件发送任务失败: {str(e)}")
        return {
            "status": "failed",
            "email": user_email,
            "error": str(e),
            "type": "verification"
        }


@celery_app.task
def send_password_reset_email(user_email: str, username: str, reset_token: str) -> Dict[str, Any]:
    """发送密码重置邮件任务"""
    try:
        success = email_service.send_password_reset_email(user_email, username, reset_token)
        
        return {
            "status": "success" if success else "failed",
            "email": user_email,
            "type": "password_reset"
        }
    except Exception as e:
        logger.error(f"密码重置邮件发送任务失败: {str(e)}")
        return {
            "status": "failed",
            "email": user_email,
            "error": str(e),
            "type": "password_reset"
        }


@celery_app.task
def send_welcome_email(user_email: str, username: str) -> Dict[str, Any]:
    """发送欢迎邮件任务"""
    try:
        success = email_service.send_welcome_email(user_email, username)
        
        return {
            "status": "success" if success else "failed",
            "email": user_email,
            "type": "welcome"
        }
    except Exception as e:
        logger.error(f"欢迎邮件发送任务失败: {str(e)}")
        return {
            "status": "failed",
            "email": user_email,
            "error": str(e),
            "type": "welcome"
        }


@celery_app.task
def send_email_change_verification(user_email: str, username: str, verification_token: str) -> Dict[str, Any]:
    """发送邮箱修改验证邮件任务"""
    try:
        success = email_service.send_email_change_verification(user_email, username, verification_token)
        
        return {
            "status": "success" if success else "failed",
            "email": user_email,
            "type": "email_change"
        }
    except Exception as e:
        logger.error(f"邮箱修改验证邮件发送任务失败: {str(e)}")
        return {
            "status": "failed",
            "email": user_email,
            "error": str(e),
            "type": "email_change"
        }


@celery_app.task
def send_notification_email(
    user_email: str, 
    username: str, 
    title: str, 
    content: str,
    action_url: str = None,
    action_text: str = None
) -> Dict[str, Any]:
    """发送通知邮件任务"""
    try:
        success = email_service.send_notification_email(
            user_email, username, title, content, action_url, action_text
        )
        
        return {
            "status": "success" if success else "failed",
            "email": user_email,
            "type": "notification"
        }
    except Exception as e:
        logger.error(f"通知邮件发送任务失败: {str(e)}")
        return {
            "status": "failed",
            "email": user_email,
            "error": str(e),
            "type": "notification"
        }