import uuid

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.modules.knowledge.api import get_knowledge_service, router


class FakeKnowledgeService:
    def __init__(self):
        self.article_id = uuid.uuid4()
        self.file_id = uuid.uuid4()
        self.user_id = uuid.uuid4()
        self.deleted_ids = []

    async def list_articles(self, **filters):
        assert filters["business_domain"] == "saas"
        assert filters["review_status"] == "approved"
        return [
            {
                "id": self.article_id,
                "title": "SaaS灰度发布复盘",
                "summary": "灰度异常、回滚和测试漏检点复盘",
                "content": "复盘内容",
                "type": "最佳实践",
                "business_domain": "saas",
                "visibility": "team",
                "review_status": "approved",
                "project_key": "crm-saas",
                "tags": ["灰度", "SLA"],
                "attachment_file_ids": [self.file_id],
            }
        ]

    async def create_article(self, payload):
        return {
            "id": self.article_id,
            **payload.model_dump(),
            "review_status": "pending",
        }

    async def get_article(self, article_id):
        return {
            "id": article_id,
            "title": "游戏版本质量报告",
            "summary": "版本提审质量结论",
            "content": "报告内容",
            "type": "Bug案例",
            "business_domain": "game",
            "visibility": "team",
            "review_status": "approved",
            "project_key": "moba-1.2.0",
            "tags": ["提审", "兼容"],
            "attachment_file_ids": [self.file_id],
        }

    async def update_article(self, article_id, payload):
        return {
            "id": article_id,
            "title": payload.title,
            "summary": "更新后的摘要",
            "content": "更新后的内容",
            "type": "经验分享",
            "business_domain": "game",
            "visibility": "public",
            "review_status": "pending",
            "project_key": "moba-1.2.1",
            "tags": ["性能"],
            "attachment_file_ids": payload.attachment_file_ids or [],
        }

    async def delete_article(self, article_id):
        self.deleted_ids.append(article_id)
        return True

    async def add_comment(self, article_id, payload):
        return {
            "id": uuid.uuid4(),
            "article_id": article_id,
            "user_id": payload.user_id,
            "content": payload.content,
            "like_count": 0,
        }

    async def list_comments(self, article_id):
        return [
            {
                "id": uuid.uuid4(),
                "article_id": article_id,
                "user_id": self.user_id,
                "content": "QA经理验收评论",
                "like_count": 0,
            }
        ]

    async def like_article(self, article_id, user_id):
        return {
            "article_id": article_id,
            "like_count": 1,
            "comment_count": 1,
            "favorite_count": 0,
            "liked": True,
            "favorited": False,
        }

    async def favorite_article(self, article_id, user_id):
        return {
            "article_id": article_id,
            "like_count": 1,
            "comment_count": 1,
            "favorite_count": 1,
            "liked": True,
            "favorited": True,
        }

    async def get_metrics(self, business_domain=None):
        assert business_domain == "saas"
        return {
            "business_domain": "saas",
            "article_count": 2,
            "approved_article_count": 1,
            "pending_article_count": 1,
            "comment_count": 3,
            "like_count": 5,
            "favorite_count": 4,
        }

    async def search_articles(self, **filters):
        assert filters["q"] == "弱网"
        return [
            {
                "id": self.article_id,
                "title": "游戏弱网测试经验",
                "summary": "弱网场景和验收指标",
                "content": "弱网测试内容",
                "type": "经验分享",
                "business_domain": "game",
                "visibility": "team",
                "review_status": "approved",
                "project_key": "moba-network",
                "tags": ["弱网"],
                "attachment_file_ids": [],
            }
        ]

    async def list_categories(self, business_domain=None):
        assert business_domain == "game"
        return [
            {
                "id": uuid.uuid4(),
                "name": "机型兼容测试",
                "description": "设备、系统、画质和崩溃验证",
                "type": "游戏兼容性测试",
                "business_domain": "game",
                "sort_order": 1,
            }
        ]


@pytest.fixture()
def app_with_fake_service():
    app = FastAPI()
    service = FakeKnowledgeService()
    app.include_router(router, prefix="/knowledge")
    app.dependency_overrides[get_knowledge_service] = lambda: service
    return app, service


@pytest.mark.asyncio
async def test_list_articles_filters_by_business_domain_and_review_status(app_with_fake_service):
    app, _ = app_with_fake_service
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/knowledge/articles",
            params={"business_domain": "saas", "review_status": "approved"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data[0]["title"] == "SaaS灰度发布复盘"
    assert data[0]["business_domain"] == "saas"


@pytest.mark.asyncio
async def test_create_detail_update_delete_article_flow(app_with_fake_service):
    app, service = app_with_fake_service
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            "/knowledge/articles",
            json={
                "title": "游戏性能压测记录",
                "summary": "团战场景帧率和内存记录",
                "content": "压测详情",
                "type": "经验分享",
                "category_id": str(uuid.uuid4()),
                "business_domain": "game",
                "visibility": "team",
                "project_key": "moba-1.2.1",
                "tags": ["性能", "帧率"],
                "attachment_file_ids": [str(service.file_id)],
            },
        )
        article_id = create_response.json()["id"]
        detail_response = await client.get(f"/knowledge/articles/{article_id}")
        update_response = await client.put(
            f"/knowledge/articles/{article_id}",
            json={
                "title": "游戏性能压测记录-更新",
                "visibility": "public",
                "attachment_file_ids": [],
            },
        )
        delete_response = await client.delete(f"/knowledge/articles/{article_id}")

    assert create_response.status_code == 201
    assert create_response.json()["review_status"] == "pending"
    assert create_response.json()["attachment_file_ids"] == [str(service.file_id)]
    assert detail_response.status_code == 200
    assert detail_response.json()["business_domain"] == "game"
    assert detail_response.json()["attachment_file_ids"] == [str(service.file_id)]
    assert update_response.status_code == 200
    assert update_response.json()["visibility"] == "public"
    assert update_response.json()["attachment_file_ids"] == []
    assert delete_response.status_code == 200
    assert service.deleted_ids == [uuid.UUID(article_id)]


@pytest.mark.asyncio
async def test_search_and_categories_support_game_domain(app_with_fake_service):
    app, _ = app_with_fake_service
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        search_response = await client.get(
            "/knowledge/search", params={"q": "弱网", "business_domain": "game"}
        )
        categories_response = await client.get(
            "/knowledge/categories", params={"business_domain": "game"}
        )

    assert search_response.status_code == 200
    assert search_response.json()[0]["title"] == "游戏弱网测试经验"
    assert categories_response.status_code == 200
    assert categories_response.json()[0]["name"] == "机型兼容测试"


@pytest.mark.asyncio
async def test_article_comment_like_favorite_and_metrics_flow(app_with_fake_service):
    app, service = app_with_fake_service
    article_id = service.article_id
    user_id = service.user_id

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        comment_response = await client.post(
            f"/knowledge/articles/{article_id}/comments",
            json={"user_id": str(user_id), "content": "QA经理验收评论"},
        )
        comments_response = await client.get(f"/knowledge/articles/{article_id}/comments")
        like_response = await client.post(
            f"/knowledge/articles/{article_id}/like",
            params={"user_id": str(user_id)},
        )
        favorite_response = await client.post(
            f"/knowledge/articles/{article_id}/favorite",
            params={"user_id": str(user_id)},
        )
        metrics_response = await client.get(
            "/knowledge/metrics", params={"business_domain": "saas"}
        )

    assert comment_response.status_code == 201
    assert comment_response.json()["content"] == "QA经理验收评论"
    assert comments_response.status_code == 200
    assert comments_response.json()[0]["article_id"] == str(article_id)
    assert like_response.status_code == 200
    assert like_response.json()["liked"] is True
    assert favorite_response.status_code == 200
    assert favorite_response.json()["favorited"] is True
    assert metrics_response.status_code == 200
    assert metrics_response.json()["comment_count"] == 3
