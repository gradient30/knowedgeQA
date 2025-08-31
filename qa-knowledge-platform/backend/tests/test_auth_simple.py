"""
简化的认证系统测试（避免Celery依赖）
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch


class TestAuthSimple:
    """简化的认证系统测试类"""
    
    @pytest.mark.asyncio
    @patch('app.modules.users.services.send_verification_email')
    async def test_register_user_simple(self, mock_email, client: AsyncClient):
        """测试用户注册（模拟邮件发送）"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "Test User"
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
        
        # 验证邮件发送被调用
        mock_email.delay.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.modules.users.services.send_verification_email')
    async def test_register_duplicate_user_simple(self, mock_email, client: AsyncClient):
        """测试重复用户注册"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        # 第一次注册
        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        
        # 第二次注册相同用户
        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        data = response.json()
        assert "用户名或邮箱已存在" in data["message"]
    
    @pytest.mark.asyncio
    @patch('app.modules.users.services.send_verification_email')
    async def test_login_success_simple(self, mock_email, client: AsyncClient):
        """测试成功登录"""
        # 先注册用户
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        await client.post("/api/v1/auth/register", json=user_data)
        
        # 登录
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials_simple(self, client: AsyncClient):
        """测试无效凭据登录"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        data = response.json()
        assert "邮箱或密码错误" in data["message"]
    
    @pytest.mark.asyncio
    @patch('app.modules.users.services.send_verification_email')
    async def test_get_current_user_simple(self, mock_email, client: AsyncClient):
        """测试获取当前用户信息"""
        # 先注册并登录
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        await client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
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
    async def test_get_current_user_invalid_token_simple(self, client: AsyncClient):
        """测试无效令牌获取用户信息"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "令牌无效" in data["message"]
    
    @pytest.mark.asyncio
    async def test_logout_simple(self, client: AsyncClient):
        """测试用户登出"""
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "登出成功"