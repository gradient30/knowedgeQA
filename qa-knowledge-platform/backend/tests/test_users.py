"""
用户管理测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.knowledge.models import BusinessDomain as KnowledgeBusinessDomain
from app.modules.knowledge.models import Category, CategoryType
from app.modules.tools.models import BusinessDomain as ToolBusinessDomain
from app.modules.tools.models import ToolCategory, ToolCategoryType
from app.modules.users.models import Team, User, UserRole


class TestUsers:
    """用户管理测试类"""

    async def create_and_login_user(
        self, client: AsyncClient, username="testuser", email="test@example.com"
    ):
        """创建并登录用户的辅助方法"""
        user_data = {
            "username": username,
            "email": email,
            "password": "testpassword123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        login_data = {"email": email, "password": "testpassword123"}
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        return login_response.json()["access_token"]

    @pytest.mark.asyncio
    async def test_user_profile_update(self, client: AsyncClient):
        """测试用户资料更新"""
        token = await self.create_and_login_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        # 更新用户资料
        update_data = {"nickname": "Updated Nickname", "bio": "This is my updated bio"}

        response = await client.put(
            "/api/v1/users/profile", json=update_data, headers=headers
        )
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
            "new_password": "newpassword123",
        }

        response = await client.post(
            "/api/v1/users/change-password", json=password_data, headers=headers
        )
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
            "new_password": "newpassword123",
        }

        response = await client.post(
            "/api/v1/users/change-password", json=password_data, headers=headers
        )
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
    async def test_user_stats_count_real_articles_comments_likes_and_tool_ratings(
        self, client: AsyncClient, async_session: AsyncSession
    ):
        """用户统计应来自真实知识协作和工具评分记录"""
        token = await self.create_and_login_user(
            client, username="statsuser", email="stats@example.com"
        )
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = await client.get("/api/v1/users/profile", headers=headers)
        user_id = profile_response.json()["id"]

        category = Category(
            name="SaaS发布质量",
            description="SaaS release quality",
            type=CategoryType.SAAS_RELEASE,
            business_domain=KnowledgeBusinessDomain.SAAS,
        )
        tool_category = ToolCategory(
            name="质量运营工具",
            description="Quality operation tools",
            type=ToolCategoryType.MANAGEMENT,
            business_domain=ToolBusinessDomain.SAAS,
        )
        async_session.add_all([category, tool_category])
        await async_session.commit()
        await async_session.refresh(category)
        await async_session.refresh(tool_category)

        article_response = await client.post(
            "/api/v1/knowledge/articles",
            json={
                "category_id": str(category.id),
                "user_id": user_id,
                "title": "SaaS灰度发布验收",
                "summary": "发布质量复盘",
                "content": "覆盖灰度、回滚、监控指标。",
                "type": "最佳实践",
                "business_domain": "saas",
                "visibility": "team",
                "tags": ["release", "qa"],
            },
        )
        assert article_response.status_code == 201
        article_id = article_response.json()["id"]

        comment_response = await client.post(
            f"/api/v1/knowledge/articles/{article_id}/comments",
            json={"user_id": user_id, "content": "补充回归准入标准。"},
        )
        assert comment_response.status_code == 201
        like_response = await client.post(
            f"/api/v1/knowledge/articles/{article_id}/like",
            params={"user_id": user_id},
        )
        assert like_response.status_code == 200

        tool_response = await client.post(
            "/api/v1/tools/",
            json={
                "category_id": str(tool_category.id),
                "name": "发布质量看板",
                "url": "https://qa.example.com/release",
                "description": "汇总SaaS发布质量指标。",
                "business_domain": "saas",
                "features": ["release", "metrics"],
            },
        )
        assert tool_response.status_code == 201
        rating_response = await client.post(
            f"/api/v1/tools/{tool_response.json()['id']}/rating",
            json={"user_id": user_id, "rating": 5, "review": "适合发布验收"},
        )
        assert rating_response.status_code == 201

        response = await client.get("/api/v1/users/stats", headers=headers)
        assert response.status_code == 200
        assert response.json() == {
            "articles_count": 1,
            "comments_count": 1,
            "likes_received": 1,
            "tools_rated": 1,
        }

    @pytest.mark.asyncio
    async def test_data_export(self, client: AsyncClient):
        """测试数据导出"""
        token = await self.create_and_login_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        export_data = {
            "format": "json",
            "include_profile": True,
            "include_articles": True,
            "include_comments": True,
        }

        response = await client.post(
            "/api/v1/users/export-data", json=export_data, headers=headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "export_info" in data
        assert "profile" in data
        assert "statistics" in data

    @pytest.mark.asyncio
    async def test_admin_user_management_flow(self, client: AsyncClient):
        """管理员应能查询用户，超级管理员应能调整角色和状态"""
        super_admin_data = {
            "username": "superadmin",
            "email": "superadmin@example.com",
            "password": "testpassword123",
            "role": "super_admin",
        }
        register_response = await client.post(
            "/api/v1/auth/register", json=super_admin_data
        )
        assert register_response.status_code == 201
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "superadmin@example.com", "password": "testpassword123"},
        )
        super_admin_token = login_response.json()["access_token"]
        super_admin_headers = {"Authorization": f"Bearer {super_admin_token}"}
        super_admin_profile = await client.get(
            "/api/v1/users/profile", headers=super_admin_headers
        )
        assert super_admin_profile.status_code == 200
        assert super_admin_profile.json()["role"] == "super_admin"

        target_token = await self.create_and_login_user(
            client,
            username="manageduser",
            email="managed@example.com",
        )
        target_profile = await client.get(
            "/api/v1/users/profile",
            headers={"Authorization": f"Bearer {target_token}"},
        )
        target_user_id = target_profile.json()["id"]

        list_response = await client.get(
            "/api/v1/users/",
            params={"skip": 0, "limit": 10},
            headers=super_admin_headers,
        )
        assert list_response.status_code == 200
        listed_users = list_response.json()
        assert {user["email"] for user in listed_users} >= {
            "superadmin@example.com",
            "managed@example.com",
        }

        get_response = await client.get(
            f"/api/v1/users/{target_user_id}",
            headers=super_admin_headers,
        )
        assert get_response.status_code == 200
        assert get_response.json()["email"] == "managed@example.com"

        promote_response = await client.put(
            f"/api/v1/users/{target_user_id}/role",
            params={"new_role": "admin"},
            headers=super_admin_headers,
        )
        assert promote_response.status_code == 200
        assert promote_response.json()["role"] == "admin"

        status_response = await client.put(
            f"/api/v1/users/{target_user_id}/status",
            params={"is_active": False},
            headers=super_admin_headers,
        )
        assert status_response.status_code == 200
        assert status_response.json()["is_active"] is False

        disabled_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "managed@example.com", "password": "testpassword123"},
        )
        assert disabled_login.status_code == 401
        assert "账户已被禁用" in disabled_login.json()["detail"]

    @pytest.mark.asyncio
    async def test_member_cannot_use_admin_user_management(self, client: AsyncClient):
        """普通成员不能访问管理员用户管理接口"""
        member_token = await self.create_and_login_user(
            client,
            username="plainmember",
            email="plainmember@example.com",
        )
        headers = {"Authorization": f"Bearer {member_token}"}

        response = await client.get("/api/v1/users/", headers=headers)

        assert response.status_code == 403


class TestTeams:
    """团队管理测试类"""

    async def create_and_login_user(
        self, client: AsyncClient, username="testuser", email="test@example.com"
    ):
        """创建并登录用户的辅助方法"""
        user_data = {
            "username": username,
            "email": email,
            "password": "testpassword123",
        }
        await client.post("/api/v1/auth/register", json=user_data)

        login_data = {"email": email, "password": "testpassword123"}
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        return login_response.json()["access_token"]

    @pytest.mark.asyncio
    async def test_create_team(self, client: AsyncClient):
        """测试创建团队"""
        token = await self.create_and_login_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        team_data = {"name": "Test Team", "description": "This is a test team"}

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
        team_data = {"name": "Test Team", "description": "This is a test team"}
        create_response = await client.post(
            "/api/v1/teams", json=team_data, headers=headers
        )
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
        team_data = {"name": "Test Team", "description": "This is a test team"}
        create_response = await client.post(
            "/api/v1/teams", json=team_data, headers=headers
        )
        team_id = create_response.json()["id"]

        # 获取团队统计
        response = await client.get(f"/api/v1/teams/{team_id}/stats", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert "total_members" in data
        assert "active_members" in data
        assert "total_articles" in data
        assert "total_tools" in data

    @pytest.mark.asyncio
    async def test_team_stats_count_member_articles_and_tool_ratings(
        self, client: AsyncClient, async_session: AsyncSession
    ):
        """团队统计应按成员聚合内容沉淀和工具评分"""
        token = await self.create_and_login_user(
            client, username="teamstats", email="teamstats@example.com"
        )
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = await client.get("/api/v1/users/profile", headers=headers)
        user_id = profile_response.json()["id"]

        create_team_response = await client.post(
            "/api/v1/teams",
            json={"name": "QA运营团队", "description": "负责SaaS和游戏验收"},
            headers=headers,
        )
        assert create_team_response.status_code == 201
        team_id = create_team_response.json()["id"]

        category = Category(
            name="游戏兼容性",
            description="Game compatibility",
            type=CategoryType.GAME_COMPATIBILITY,
            business_domain=KnowledgeBusinessDomain.GAME,
        )
        tool_category = ToolCategory(
            name="游戏测试工具",
            description="Game QA tools",
            type=ToolCategoryType.GAME,
            business_domain=ToolBusinessDomain.GAME,
        )
        async_session.add_all([category, tool_category])
        await async_session.commit()
        await async_session.refresh(category)
        await async_session.refresh(tool_category)

        article_response = await client.post(
            "/api/v1/knowledge/articles",
            json={
                "category_id": str(category.id),
                "user_id": user_id,
                "title": "手游兼容性验收清单",
                "summary": "设备矩阵与性能基线",
                "content": "覆盖机型、帧率、崩溃率。",
                "type": "最佳实践",
                "business_domain": "game",
                "visibility": "team",
                "tags": ["game", "compatibility"],
            },
        )
        assert article_response.status_code == 201

        tool_response = await client.post(
            "/api/v1/tools/",
            json={
                "category_id": str(tool_category.id),
                "name": "兼容性设备矩阵",
                "url": "https://qa.example.com/devices",
                "description": "管理游戏兼容性设备覆盖。",
                "business_domain": "game",
                "features": ["devices", "coverage"],
            },
        )
        assert tool_response.status_code == 201
        rating_response = await client.post(
            f"/api/v1/tools/{tool_response.json()['id']}/rating",
            json={"user_id": user_id, "rating": 4, "review": "设备覆盖清晰"},
        )
        assert rating_response.status_code == 201

        response = await client.get(f"/api/v1/teams/{team_id}/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_members"] == 1
        assert data["total_articles"] == 1
        assert data["total_tools"] == 1
        assert data["recent_activity_count"] >= 2
