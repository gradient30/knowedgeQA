import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
import os

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_tls = settings.SMTP_TLS
        
        # 设置模板环境
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        if template_dir.exists():
            self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
        else:
            self.jinja_env = None
            logger.warning(f"Email template directory not found: {template_dir}")
    
    def _get_template(self, template_name: str) -> Optional[Template]:
        """获取邮件模板"""
        if not self.jinja_env:
            return None
        
        try:
            return self.jinja_env.get_template(f"{template_name}.html")
        except Exception as e:
            logger.error(f"Failed to load email template {template_name}: {e}")
            return None
    
    def _create_fallback_template(self, template_type: str, **kwargs) -> str:
        """创建备用邮件模板"""
        base_style = """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #1890ff; margin: 0;">QA测试知识协作平台</h1>
                <p style="color: #666; margin: 5px 0 0 0;">专为测试团队打造的知识分享与协作平台</p>
            </div>
            {content}
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <div style="text-align: center;">
                <p style="color: #999; font-size: 12px; margin: 0;">
                    此邮件由QA测试知识协作平台自动发送，请勿回复。
                </p>
            </div>
        </div>
        """
        
        templates = {
            "verification": f"""
            <h2 style="color: #1890ff;">欢迎加入我们！</h2>
            <p>亲爱的 {kwargs.get('username', '用户')}，</p>
            <p>感谢您注册QA测试知识协作平台。请点击下面的按钮验证您的邮箱地址：</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{kwargs.get('verification_url', '#')}" 
                   style="background-color: #1890ff; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 4px; display: inline-block;">
                    验证邮箱
                </a>
            </div>
            <p>如果按钮无法点击，请复制以下链接到浏览器：</p>
            <p style="word-break: break-all; color: #666; background: #f5f5f5; padding: 10px; border-radius: 4px;">
                {kwargs.get('verification_url', '#')}
            </p>
            <p style="color: #999; font-size: 12px;">
                此链接将在24小时后失效。如果您没有注册账户，请忽略此邮件。
            </p>
            """,
            
            "password_reset": f"""
            <h2 style="color: #ff4d4f;">密码重置请求</h2>
            <p>亲爱的 {kwargs.get('username', '用户')}，</p>
            <p>我们收到了您的密码重置请求。请点击下面的按钮重置您的密码：</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{kwargs.get('reset_url', '#')}" 
                   style="background-color: #ff4d4f; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 4px; display: inline-block;">
                    重置密码
                </a>
            </div>
            <p>如果按钮无法点击，请复制以下链接到浏览器：</p>
            <p style="word-break: break-all; color: #666; background: #f5f5f5; padding: 10px; border-radius: 4px;">
                {kwargs.get('reset_url', '#')}
            </p>
            <p style="color: #ff4d4f; font-weight: bold;">
                如果您没有请求密码重置，请立即联系管理员。
            </p>
            <p style="color: #999; font-size: 12px;">
                此链接将在1小时后失效。
            </p>
            """,
            
            "welcome": f"""
            <h2 style="color: #52c41a;">欢迎加入QA测试知识协作平台！</h2>
            <p>亲爱的 {kwargs.get('username', '用户')}，</p>
            <p>您的邮箱已成功验证，现在可以开始使用平台的所有功能了！</p>
            <div style="background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 4px; padding: 16px; margin: 20px 0;">
                <h3 style="color: #389e0d; margin-top: 0;">您可以开始：</h3>
                <ul style="color: #52c41a; margin: 0;">
                    <li>分享测试经验和最佳实践</li>
                    <li>浏览和收藏测试工具</li>
                    <li>关注行业前沿资讯</li>
                    <li>与团队成员协作交流</li>
                </ul>
            </div>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{kwargs.get('platform_url', 'http://localhost:3000')}" 
                   style="background-color: #52c41a; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 4px; display: inline-block;">
                    开始使用平台
                </a>
            </div>
            """,
            
            "email_change": f"""
            <h2 style="color: #fa8c16;">邮箱修改验证</h2>
            <p>亲爱的 {kwargs.get('username', '用户')}，</p>
            <p>我们收到了您的邮箱修改请求。请点击下面的按钮验证您的新邮箱地址：</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{kwargs.get('verification_url', '#')}" 
                   style="background-color: #fa8c16; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 4px; display: inline-block;">
                    验证新邮箱
                </a>
            </div>
            <p>如果按钮无法点击，请复制以下链接到浏览器：</p>
            <p style="word-break: break-all; color: #666; background: #f5f5f5; padding: 10px; border-radius: 4px;">
                {kwargs.get('verification_url', '#')}
            </p>
            <p style="color: #fa8c16; font-weight: bold;">
                如果您没有请求修改邮箱，请立即联系管理员。
            </p>
            <p style="color: #999; font-size: 12px;">
                此链接将在1小时后失效。验证成功后，您的邮箱地址将被更新。
            </p>
            """,
            
            "notification": f"""
            <h2 style="color: #1890ff;">{kwargs.get('title', '新通知')}</h2>
            <p>亲爱的 {kwargs.get('username', '用户')}，</p>
            <div style="background: #f0f9ff; border: 1px solid #91d5ff; border-radius: 4px; padding: 16px; margin: 20px 0;">
                {kwargs.get('content', '您有新的通知消息。')}
            </div>
            {f'''
            <div style="text-align: center; margin: 30px 0;">
                <a href="{kwargs.get('action_url')}" 
                   style="background-color: #1890ff; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 4px; display: inline-block;">
                    {kwargs.get('action_text', '查看详情')}
                </a>
            </div>
            ''' if kwargs.get('action_url') else ''}
            """
        }
        
        content = templates.get(template_type, f"<p>{kwargs.get('content', '邮件内容')}</p>")
        return base_style.format(content=content)
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        html_content: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        发送邮件
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            template_name: 模板名称
            template_data: 模板数据
            html_content: 直接的HTML内容
            cc: 抄送列表
            bcc: 密送列表
        """
        try:
            # 如果没有配置SMTP，则只记录日志
            if not self.smtp_user or not self.smtp_password:
                logger.info(f"邮件发送模拟 - 收件人: {to_email}, 主题: {subject}")
                if template_name and template_data:
                    logger.info(f"模板: {template_name}, 数据: {template_data}")
                return True
            
            # 生成邮件内容
            if html_content:
                email_html = html_content
            elif template_name:
                template = self._get_template(template_name)
                if template and template_data:
                    email_html = template.render(**template_data)
                else:
                    # 使用备用模板
                    email_html = self._create_fallback_template(template_name, **(template_data or {}))
            else:
                raise ValueError("必须提供 html_content 或 template_name")
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            
            # 添加HTML内容
            html_part = MIMEText(email_html, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                
                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)
                
                server.send_message(msg, to_addrs=recipients)
            
            logger.info(f"邮件发送成功 - 收件人: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败 - 收件人: {to_email}, 错误: {str(e)}")
            return False
    
    def send_verification_email(self, to_email: str, username: str, token: str) -> bool:
        """发送邮箱验证邮件"""
        verification_url = f"http://localhost:3000/auth/verify-email?token={token}"
        
        return self.send_email(
            to_email=to_email,
            subject="QA测试知识协作平台 - 邮箱验证",
            template_name="verification",
            template_data={
                "username": username,
                "verification_url": verification_url,
                "token": token
            }
        )
    
    def send_password_reset_email(self, to_email: str, username: str, token: str) -> bool:
        """发送密码重置邮件"""
        reset_url = f"http://localhost:3000/auth/reset-password?token={token}"
        
        return self.send_email(
            to_email=to_email,
            subject="QA测试知识协作平台 - 密码重置",
            template_name="password_reset",
            template_data={
                "username": username,
                "reset_url": reset_url,
                "token": token
            }
        )
    
    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """发送欢迎邮件"""
        return self.send_email(
            to_email=to_email,
            subject="欢迎加入QA测试知识协作平台！",
            template_name="welcome",
            template_data={
                "username": username,
                "platform_url": "http://localhost:3000"
            }
        )
    
    def send_email_change_verification(self, to_email: str, username: str, token: str) -> bool:
        """发送邮箱修改验证邮件"""
        verification_url = f"http://localhost:3000/auth/confirm-email-change?token={token}"
        
        return self.send_email(
            to_email=to_email,
            subject="QA测试知识协作平台 - 邮箱修改验证",
            template_name="email_change",
            template_data={
                "username": username,
                "verification_url": verification_url,
                "token": token
            }
        )
    
    def send_notification_email(
        self,
        to_email: str,
        username: str,
        title: str,
        content: str,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None
    ) -> bool:
        """发送通知邮件"""
        return self.send_email(
            to_email=to_email,
            subject=f"QA测试知识协作平台 - {title}",
            template_name="notification",
            template_data={
                "username": username,
                "title": title,
                "content": content,
                "action_url": action_url,
                "action_text": action_text
            }
        )


# 全局邮件服务实例
email_service = EmailService()