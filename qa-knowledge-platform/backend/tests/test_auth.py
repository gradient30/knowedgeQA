"""
认证系统测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import Mock

from app.modules.users.models import User, UserRole
from app.modules.users import services as user_services


class TestAuth:
    """认证系统测试类"""

    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient):
        """测试用户注册"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "Test User",
        }

        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201

        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["nickname"] == "Test User"
        assert data["role"] == "member"
        assert data["is_active"] is True
        assert data["is_verified"] is False

    @pytest.mark.asyncio
    async def test_register_duplicate_user(self, client: AsyncClient):
        """测试重复用户注册"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
        }

        # 第一次注册
        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201

        # 第二次注册相同用户
        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "用户名或邮箱已存在" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_success(
        self, client: AsyncClient, async_session: AsyncSession
    ):
        """测试成功登录"""
        # 先注册用户
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        # 登录
        login_data = {"email": "test@example.com", "password": "testpassword123"}

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """测试无效凭据登录"""
        login_data = {"email": "nonexistent@example.com", "password": "wrongpassword"}

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "邮箱或密码错误" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient):
        """测试获取当前用户信息"""
        # 先注册并登录
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        login_data = {"email": "test@example.com", "password": "testpassword123"}
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]

        # 获取当前用户信息
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """测试无效令牌获取用户信息"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 401
        assert "令牌无效" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_logout(self, client: AsyncClient):
        """测试用户登出"""
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "登出成功"

    @pytest.mark.asyncio
    async def test_password_reset_request(self, client: AsyncClient):
        """测试密码重置请求"""
        # 先注册用户
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        # 请求密码重置
        reset_data = {"email": "test@example.com"}
        response = await client.post(
            "/api/v1/auth/request-password-reset", json=reset_data
        )

        assert response.status_code == 200
        assert "重置链接已发送" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_password_reset_nonexistent_email(self, client: AsyncClient):
        """测试不存在邮箱的密码重置请求"""
        reset_data = {"email": "nonexistent@example.com"}
        response = await client.post(
            "/api/v1/auth/request-password-reset", json=reset_data
        )

        # 为了安全，即使邮箱不存在也返回成功
        assert response.status_code == 200
        assert "重置链接已发送" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_email_verification_requires_valid_token(
        self, client: AsyncClient, monkeypatch
    ):
        """邮箱验证必须使用注册时生成的有效令牌"""
        sent_tokens = []
        verification_task = Mock()
        verification_task.delay.side_effect = (
            lambda email, username, token: sent_tokens.append(token)
        )
        monkeypatch.setattr(user_services, "send_verification_email", verification_task)

        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "verifyuser",
                "email": "verify@example.com",
                "password": "testpassword123",
            },
        )
        assert response.status_code == 201
        assert response.json()["is_verified"] is False
        assert sent_tokens

        invalid_response = await client.post(
            "/api/v1/auth/verify-email", json={"token": "invalid-token"}
        )
        assert invalid_response.status_code == 400

        verify_response = await client.post(
            "/api/v1/auth/verify-email", json={"token": sent_tokens[0]}
        )
        assert verify_response.status_code == 200

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "verify@example.com", "password": "testpassword123"},
        )
        assert login_response.status_code == 200
        assert login_response.json()["user"]["is_verified"] is True

    @pytest.mark.asyncio
    async def test_password_reset_token_changes_password_once(
        self, client: AsyncClient, monkeypatch
    ):
        """密码重置令牌应能修改密码且不可复用"""
        sent_tokens = []
        reset_task = Mock()
        reset_task.delay.side_effect = (
            lambda email, username, token: sent_tokens.append(token)
        )
        monkeypatch.setattr(user_services, "send_password_reset_email", reset_task)

        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "resetuser",
                "email": "reset@example.com",
                "password": "oldpassword123",
            },
        )

        request_response = await client.post(
            "/api/v1/auth/request-password-reset",
            json={"email": "reset@example.com"},
        )
        assert request_response.status_code == 200
        assert sent_tokens

        invalid_response = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": "invalid-token", "new_password": "newpassword123"},
        )
        assert invalid_response.status_code == 400

        reset_response = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": sent_tokens[0], "new_password": "newpassword123"},
        )
        assert reset_response.status_code == 200

        old_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "reset@example.com", "password": "oldpassword123"},
        )
        new_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "reset@example.com", "password": "newpassword123"},
        )
        reused_response = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": sent_tokens[0], "new_password": "reusedpassword123"},
        )

        assert old_login.status_code == 401
        assert new_login.status_code == 200
        assert reused_response.status_code == 400
