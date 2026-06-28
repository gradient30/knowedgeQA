import uuid

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.modules.intelligence.api import get_intelligence_service, router


class FakeIntelligenceService:
    async def similar_articles(self, business_domain: str, q: str, limit: int):
        assert business_domain == "game"
        assert q == "弱网"
        assert limit == 5
        article_id = uuid.uuid4()
        return [
            {
                "id": str(article_id),
                "title": "游戏弱网测试经验",
                "business_domain": "game",
                "summary": "弱网场景、延迟和重连验收指标",
                "source_links": [f"/api/v1/knowledge/articles/{article_id}"],
                "match_reasons": ["业务域匹配", "关键词命中: 弱网"],
            }
        ]

    async def tool_recommendations(self, business_domain: str, q: str, limit: int):
        assert business_domain == "saas"
        assert q == "API"
        assert limit == 5
        tool_id = uuid.uuid4()
        return [
            {
                "id": str(tool_id),
                "name": "SaaS接口契约测试工具",
                "business_domain": "saas",
                "description": "接口兼容性与灰度前回归验证",
                "source_links": [f"/api/v1/tools/{tool_id}"],
                "match_reasons": ["推荐工具", "关键词命中: API"],
            }
        ]

    async def news_summary(self, business_domain: str, limit: int):
        assert business_domain == "game"
        assert limit == 3
        news_id = uuid.uuid4()
        return {
            "business_domain": "game",
            "summary": "游戏 QA 近期关注 AI 测试与自动化探索。",
            "source_links": [f"/api/v1/news/items/{news_id}"],
            "item_count": 1,
        }


@pytest.fixture()
def app_with_fake_service():
    app = FastAPI()
    service = FakeIntelligenceService()
    app.include_router(router, prefix="/intelligence")
    app.dependency_overrides[get_intelligence_service] = lambda: service
    return app


@pytest.mark.asyncio
async def test_similar_articles_are_source_backed(app_with_fake_service):
    async with AsyncClient(
        transport=ASGITransport(app=app_with_fake_service), base_url="http://test"
    ) as client:
        response = await client.get(
            "/intelligence/similar-articles",
            params={"business_domain": "game", "q": "弱网"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data[0]["business_domain"] == "game"
    assert data[0]["source_links"][0].startswith("/api/v1/knowledge/articles/")


@pytest.mark.asyncio
async def test_tool_recommendations_are_source_backed(app_with_fake_service):
    async with AsyncClient(
        transport=ASGITransport(app=app_with_fake_service), base_url="http://test"
    ) as client:
        response = await client.get(
            "/intelligence/tool-recommendations",
            params={"business_domain": "saas", "q": "API"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data[0]["business_domain"] == "saas"
    assert data[0]["source_links"][0].startswith("/api/v1/tools/")


@pytest.mark.asyncio
async def test_news_summary_is_source_backed(app_with_fake_service):
    async with AsyncClient(
        transport=ASGITransport(app=app_with_fake_service), base_url="http://test"
    ) as client:
        response = await client.get(
            "/intelligence/news-summary",
            params={"business_domain": "game", "limit": 3},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["item_count"] == 1
    assert data["source_links"][0].startswith("/api/v1/news/items/")
