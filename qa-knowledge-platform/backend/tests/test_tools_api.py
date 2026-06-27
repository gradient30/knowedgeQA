import uuid

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.modules.tools.api import get_tools_service, router


class FakeToolsService:
    def __init__(self):
        self.tool_id = uuid.uuid4()
        self.deleted_ids = []

    async def list_tools(self, **filters):
        assert filters["business_domain"] == "game"
        assert filters["is_recommended"] is True
        return [
            {
                "id": self.tool_id,
                "name": "游戏帧率巡检工具",
                "url": "https://example.com/fps",
                "description": "用于团战场景 FPS 和内存巡检",
                "business_domain": "game",
                "project_key": "moba",
                "category_id": uuid.uuid4(),
                "features": ["FPS", "内存", "弱网"],
                "avg_rating": 4.5,
                "rating_count": 8,
                "usage_count": 20,
                "is_recommended": True,
            }
        ]

    async def create_tool(self, payload):
        return {
            "id": self.tool_id,
            **payload.model_dump(),
            "avg_rating": 0,
            "rating_count": 0,
            "usage_count": 0,
            "is_recommended": False,
        }

    async def get_tool(self, tool_id):
        return {
            "id": tool_id,
            "name": "SaaS接口契约测试工具",
            "url": "https://example.com/api",
            "description": "用于接口兼容性验证",
            "business_domain": "saas",
            "project_key": "crm",
            "category_id": uuid.uuid4(),
            "features": ["契约测试"],
            "avg_rating": 4.2,
            "rating_count": 6,
            "usage_count": 12,
            "is_recommended": True,
        }

    async def update_tool(self, tool_id, payload):
        return {
            "id": tool_id,
            "name": payload.name,
            "url": "https://example.com/api",
            "description": "更新后的工具描述",
            "business_domain": "saas",
            "project_key": "crm",
            "category_id": uuid.uuid4(),
            "features": ["契约测试", "回归"],
            "avg_rating": 4.2,
            "rating_count": 6,
            "usage_count": 12,
            "is_recommended": True,
        }

    async def delete_tool(self, tool_id):
        self.deleted_ids.append(tool_id)
        return True

    async def list_categories(self, business_domain=None):
        assert business_domain == "saas"
        return [
            {
                "id": uuid.uuid4(),
                "name": "SaaS接口测试工具",
                "description": "契约测试和回归验证工具",
                "type": "接口测试",
                "business_domain": "saas",
                "sort_order": 1,
            }
        ]

    async def rate_tool(self, tool_id, payload):
        return {
            "id": uuid.uuid4(),
            "tool_id": tool_id,
            "user_id": payload.user_id,
            "rating": payload.rating,
            "review": payload.review,
            "pros_cons": payload.pros_cons,
        }

    async def favorite_tool(self, tool_id, user_id):
        assert user_id is not None
        return True

    async def record_usage(self, tool_id):
        return {"tool_id": tool_id, "usage_count": 21}


@pytest.fixture()
def app_with_fake_service():
    app = FastAPI()
    service = FakeToolsService()
    app.include_router(router, prefix="/tools")
    app.dependency_overrides[get_tools_service] = lambda: service
    return app, service


@pytest.mark.asyncio
async def test_list_tools_filters_by_game_domain_and_recommended(app_with_fake_service):
    app, _ = app_with_fake_service
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/tools/",
            params={"business_domain": "game", "is_recommended": "true"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data[0]["name"] == "游戏帧率巡检工具"
    assert data[0]["business_domain"] == "game"


@pytest.mark.asyncio
async def test_tool_crud_rating_favorite_and_usage_flow(app_with_fake_service):
    app, service = app_with_fake_service
    category_id = uuid.uuid4()
    user_id = uuid.uuid4()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            "/tools/",
            json={
                "category_id": str(category_id),
                "name": "SaaS接口契约测试工具",
                "url": "https://example.com/api",
                "description": "用于接口兼容性验证",
                "business_domain": "saas",
                "project_key": "crm",
                "features": ["契约测试"],
            },
        )
        tool_id = create_response.json()["id"]
        detail_response = await client.get(f"/tools/{tool_id}")
        update_response = await client.put(
            f"/tools/{tool_id}", json={"name": "SaaS接口契约测试工具-更新"}
        )
        rating_response = await client.post(
            f"/tools/{tool_id}/rating",
            json={
                "user_id": str(user_id),
                "rating": 5,
                "review": "适合灰度前 API 回归",
                "pros_cons": {"pros": ["稳定"], "cons": ["配置复杂"]},
            },
        )
        favorite_response = await client.post(
            f"/tools/{tool_id}/favorite", params={"user_id": str(user_id)}
        )
        usage_response = await client.post(f"/tools/{tool_id}/usage")
        delete_response = await client.delete(f"/tools/{tool_id}")

    assert create_response.status_code == 201
    assert detail_response.status_code == 200
    assert update_response.json()["name"].endswith("更新")
    assert rating_response.status_code == 201
    assert rating_response.json()["rating"] == 5
    assert favorite_response.json()["success"] is True
    assert usage_response.json()["usage_count"] == 21
    assert delete_response.status_code == 200
    assert service.deleted_ids == [uuid.UUID(tool_id)]


@pytest.mark.asyncio
async def test_tool_categories_support_saas_domain(app_with_fake_service):
    app, _ = app_with_fake_service
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/tools/categories", params={"business_domain": "saas"}
        )

    assert response.status_code == 200
    assert response.json()[0]["name"] == "SaaS接口测试工具"
