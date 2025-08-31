"""
用户管理测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User, UserRole, Team


class TestUsers:
    """用户管理测试类"""
    
    async def create_and_login_user(self, client: AsyncClient, username="testuser", email="test@example.com"):
        """创建并登录用户的辅助方法"""
        user_data = {
            "username": username,
            "email": email,
            "password": "testpassword123"
        }
        await client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "email": email,
            "password": "testpassword123"
        }
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        return login_response.json()["access_token"]
    
    @pytest.mark.asyncio
    async def test_user_profile_update(self, client: AsyncClient):
        """测试用户资料更新"""
        token = await self.create_and_login_user(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # 更新用户资料
        update_data = {
            "nickname": "Updated Nickname",
            "bio": "This is my updated bio"
        }
        
        response = await client.put("/api/v1/users/profile", json=update_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["nickname"] == "Updated Nickname"
        assert data["bio"] == "This is my updated bio"
    
    @pytest.mark.asyncio
    async def test_password_change(self, client: AsyncClient):
        """测试密码修改"""
        token = await self.create_and_login_user(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # 修改密码
        password_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }
        
        response = await client.post("/api/v1/users/change-password", json=password_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    @pytest.mark.asyncio
    async def test_password_change_wrong_current(self, client: AsyncClient):
        """测试错误当前密码的密码修改"""
        token = await self.create_and_login_user(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # 使用错误的当前密码
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        
        response = await client.post("/api/v1/users/change-password", json=password_data, headers=headers)
        assert response.status_code == 400
        assert "当前密码错误" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_user_stats(self, client: AsyncClient):
        """测试用户统计信息"""
        token = await self.create_and_login_user(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get("/api/v1/users/stats", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "articles_count" in data
        assert "comments_count" in data
        assert "likes_received" in data
        assert "tools_rated" in data
    
    @pytest.mark.asyncio
    async def test_data_export(self, client: AsyncClient):
        """测试数据导出"""
        token = await self.create_and_login_user(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        export_data = {
            "format": "json",
            "include_profile": True,
            "include_articles": True,
            "include_comments": True
        }
        
        response = await client.post("/api/v1/users/export-data", json=export_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "export_info" in data
        assert "profile" in data
        assert "statistics" in data


class TestTeams:
    """团队管理测试类"""
    
    async def create_and_login_user(self, client: AsyncClient, username="testuser", email="test@example.com"):
        """创建并登录用户的辅助方法"""
        user_data = {
            "username": username,
            "email": email,
            "password": "testpassword123"
        }
        await client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "email": email,
            "password": "testpassword123"
        }
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        return login_response.json()["access_token"]
    
    @pytest.mark.asyncio
    async def test_create_team(self, client: AsyncClient):
        """测试创建团队"""
        token = await self.create_and_login_user(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        team_data = {
            "name": "Test Team",
            "description": "This is a test team"
        }
        
        response = await client.post("/api/v1/teams", json=team_data, headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == "Test Team"
        assert data["description"] == "This is a test team"
        assert data["member_count"] == 1
    
    @pytest.mark.asyncio
    async def test_get_team_info(self, client: AsyncClient):
        """测试获取团队信息"""
        token = await self.create_and_login_user(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建团队
        team_data = {
            "name": "Test Team",
            "description": "This is a test team"
        }
        create_response = await client.post("/api/v1/teams", json=team_data, headers=headers)
        team_id = create_response.json()["id"]
        
        # 获取团队信息
        response = await client.get(f"/api/v1/teams/{team_id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test Team"
        assert data["description"] == "This is a test team"
    
    @pytest.mark.asyncio
    async def test_team_stats(self, client: AsyncClient):
        """测试团队统计信息"""
        token = await self.create_and_login_user(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # 先创建团队
        team_data = {
            "name": "Test Team",
            "description": "This is a test team"
        }
        create_response = await client.post("/api/v1/teams", json=team_data, headers=headers)
        team_id = create_response.json()["id"]
        
        # 获取团队统计
        response = await client.get(f"/api/v1/teams/{team_id}/stats", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_members" in data
        assert "active_members" in data
        assert "total_articles" in data
        assert "total_tools" in data