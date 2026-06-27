import uuid

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.modules.news.api import get_news_service, router


class FakeNewsService:
    def __init__(self):
        self.item_id = uuid.uuid4()
        self.source_id = uuid.uuid4()
        self.deleted_source_ids = []

    async def list_items(self, **filters):
        assert filters["business_domain"] == "game"
        assert filters["review_status"] == "pending"
        return [
            {
                "id": self.item_id,
                "source_id": self.source_id,
                "title": "网易游戏 AI 测试实践",
                "url": "https://example.com/news/ai-test",
                "summary": "游戏自动化测试和 AI Agent 趋势",
                "business_domain": "game",
                "tags": ["AI测试", "游戏"],
                "relevance_score": 92.5,
                "review_status": "pending",
            }
        ]

    async def publish_item(self, item_id):
        return {
            "id": item_id,
            "source_id": self.source_id,
            "title": "已发布资讯",
            "url": "https://example.com/news/published",
            "summary": "发布后的摘要",
            "business_domain": "saas",
            "tags": ["SaaS"],
            "relevance_score": 88,
            "review_status": "approved",
        }

    async def reject_item(self, item_id):
        return {
            "id": item_id,
            "source_id": self.source_id,
            "title": "已驳回资讯",
            "url": "https://example.com/news/rejected",
            "summary": "驳回后的摘要",
            "business_domain": "game",
            "tags": ["低相关"],
            "relevance_score": 10,
            "review_status": "rejected",
        }

    async def list_sources(self, business_domain=None):
        assert business_domain == "game"
        return [
            {
                "id": self.source_id,
                "name": "腾讯云游戏行业资讯",
                "url": "https://www.tencentcloud.com/solutions/gaming",
                "category": "游戏测试",
                "business_domain": "game",
                "keywords": ["游戏质量", "性能"],
                "frequency_hours": 24,
                "is_active": True,
            }
        ]

    async def create_source(self, payload):
        return {"id": self.source_id, **payload.model_dump()}

    async def update_source(self, source_id, payload):
        return {
            "id": source_id,
            "name": payload.name,
            "url": "https://www.neteasegames.com/news/",
            "category": "游戏测试",
            "business_domain": "game",
            "keywords": ["AI测试"],
            "frequency_hours": 12,
            "is_active": True,
        }

    async def delete_source(self, source_id):
        self.deleted_source_ids.append(source_id)
        return True


@pytest.fixture()
def app_with_fake_service():
    app = FastAPI()
    service = FakeNewsService()
    app.include_router(router, prefix="/news")
    app.dependency_overrides[get_news_service] = lambda: service
    return app, service


@pytest.mark.asyncio
async def test_list_news_items_filters_by_game_domain_and_review_status(app_with_fake_service):
    app, _ = app_with_fake_service
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/news/items",
            params={"business_domain": "game", "review_status": "pending"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data[0]["title"] == "网易游戏 AI 测试实践"
    assert data[0]["review_status"] == "pending"


@pytest.mark.asyncio
async def test_publish_and_reject_news_items(app_with_fake_service):
    app, service = app_with_fake_service
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        publish_response = await client.post(f"/news/items/{service.item_id}/publish")
        reject_response = await client.post(f"/news/items/{service.item_id}/reject")

    assert publish_response.status_code == 200
    assert publish_response.json()["review_status"] == "approved"
    assert reject_response.status_code == 200
    assert reject_response.json()["review_status"] == "rejected"


@pytest.mark.asyncio
async def test_news_source_crud_supports_business_domain(app_with_fake_service):
    app, service = app_with_fake_service
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        list_response = await client.get(
            "/news/sources", params={"business_domain": "game"}
        )
        create_response = await client.post(
            "/news/sources",
            json={
                "name": "网易游戏研发资讯",
                "url": "https://www.neteasegames.com/news/",
                "category": "游戏测试",
                "business_domain": "game",
                "keywords": ["AI测试"],
                "frequency_hours": 12,
                "is_active": True,
            },
        )
        source_id = create_response.json()["id"]
        update_response = await client.put(
            f"/news/sources/{source_id}",
            json={"name": "网易游戏研发资讯-更新"},
        )
        delete_response = await client.delete(f"/news/sources/{source_id}")

    assert list_response.status_code == 200
    assert list_response.json()[0]["name"] == "腾讯云游戏行业资讯"
    assert create_response.status_code == 201
    assert create_response.json()["business_domain"] == "game"
    assert update_response.json()["name"].endswith("更新")
    assert delete_response.json()["success"] is True
    assert service.deleted_source_ids == [uuid.UUID(source_id)]
