import pytest
from httpx import AsyncClient


async def create_and_login_user(
    client: AsyncClient,
    username: str,
    email: str,
    role: str = "member",
) -> dict:
    user_data = {
        "username": username,
        "email": email,
        "password": "testpassword123",
        "role": role,
    }
    register_response = await client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "testpassword123"},
    )
    assert login_response.status_code == 200
    return {"Authorization": f"Bearer {login_response.json()['access_token']}"}


@pytest.mark.asyncio
async def test_notification_admin_requires_admin(client: AsyncClient):
    """邮件通知管理只允许管理员访问"""
    member_headers = await create_and_login_user(
        client,
        username="notificationmember",
        email="notificationmember@example.com",
    )

    anonymous_response = await client.get("/api/v1/notifications/email-settings")
    member_response = await client.get(
        "/api/v1/notifications/email-settings", headers=member_headers
    )

    assert anonymous_response.status_code == 403
    assert member_response.status_code == 403


@pytest.mark.asyncio
async def test_admin_email_settings_are_persisted(client: AsyncClient):
    """管理员修改邮件通知开关后应能读回同一份设置"""
    admin_headers = await create_and_login_user(
        client,
        username="notificationadmin",
        email="notificationadmin@example.com",
        role="admin",
    )
    settings_payload = {
        "notifications": {
            "email_verification": False,
            "password_reset": True,
            "welcome_email": False,
            "article_comments": True,
            "team_invitations": False,
            "system_updates": True,
        }
    }

    update_response = await client.put(
        "/api/v1/notifications/email-settings",
        json=settings_payload,
        headers=admin_headers,
    )
    read_response = await client.get(
        "/api/v1/notifications/email-settings", headers=admin_headers
    )

    assert update_response.status_code == 200
    assert (
        update_response.json()["settings"]["notifications"]
        == settings_payload["notifications"]
    )
    assert read_response.status_code == 200
    assert read_response.json()["notifications"] == settings_payload["notifications"]


@pytest.mark.asyncio
async def test_admin_templates_preview_test_email_and_logs(client: AsyncClient):
    """通知管理页需要模板、预览、测试邮件和发送日志闭环"""
    admin_headers = await create_and_login_user(
        client,
        username="notificationops",
        email="notificationops@example.com",
        role="admin",
    )

    templates_response = await client.get(
        "/api/v1/notifications/email-templates", headers=admin_headers
    )
    assert templates_response.status_code == 200
    templates = templates_response.json()["templates"]
    assert {template["id"] for template in templates} >= {"welcome", "notification"}

    preview_response = await client.post(
        "/api/v1/notifications/preview-template",
        json={"template_name": "notification"},
        headers=admin_headers,
    )
    assert preview_response.status_code == 200
    assert "QA测试知识协作平台" in preview_response.json()["html_content"]

    test_email_response = await client.post(
        "/api/v1/notifications/test-email",
        json={"to_email": "qa-manager@example.com"},
        headers=admin_headers,
    )
    assert test_email_response.status_code == 200
    assert test_email_response.json()["success"] is True

    logs_response = await client.get(
        "/api/v1/notifications/email-logs", headers=admin_headers
    )
    assert logs_response.status_code == 200
    logs = logs_response.json()["logs"]
    assert logs[0]["to_email"] == "qa-manager@example.com"
    assert logs[0]["template_name"] == "notification"
    assert logs[0]["status"] == "success"
