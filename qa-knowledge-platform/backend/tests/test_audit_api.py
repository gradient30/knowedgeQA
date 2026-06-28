import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.knowledge.models import BusinessDomain, Category, CategoryType
from app.modules.news.models import BusinessDomain as NewsBusinessDomain
from app.modules.news.models import NewsCategory, NewsItem, NewsSource
from app.modules.news.models import ReviewStatus as NewsReviewStatus


@pytest.mark.asyncio
async def test_knowledge_lifecycle_writes_queryable_audit_logs(
    client: AsyncClient, async_session: AsyncSession
):
    category = Category(
        name="SaaS审计验收",
        description="Audit acceptance category",
        type=CategoryType.SAAS_RELEASE,
        business_domain=BusinessDomain.SAAS,
    )
    async_session.add(category)
    await async_session.commit()
    await async_session.refresh(category)

    user_id = str(uuid.uuid4())
    create_response = await client.post(
        "/api/v1/knowledge/articles",
        json={
            "category_id": str(category.id),
            "user_id": user_id,
            "title": "SaaS审计日志验收",
            "summary": "验证创建、审核、删除可追溯",
            "content": "审计日志需要记录关键治理动作。",
            "type": "最佳实践",
            "business_domain": "saas",
            "visibility": "team",
            "tags": ["audit", "governance"],
        },
    )
    assert create_response.status_code == 201
    article_id = create_response.json()["id"]

    update_response = await client.put(
        f"/api/v1/knowledge/articles/{article_id}",
        json={"review_status": "approved", "title": "SaaS审计日志验收-已审核"},
    )
    assert update_response.status_code == 200
    delete_response = await client.delete(f"/api/v1/knowledge/articles/{article_id}")
    assert delete_response.status_code == 200

    logs_response = await client.get(
        "/api/v1/audit/logs",
        params={
            "resource_type": "knowledge_article",
            "resource_id": article_id,
            "business_domain": "saas",
        },
    )

    assert logs_response.status_code == 200
    logs = logs_response.json()
    actions = [log["action"] for log in logs]
    assert actions == ["delete", "review", "create"]
    assert {log["resource_id"] for log in logs} == {article_id}
    assert logs[0]["resource_type"] == "knowledge_article"
    assert logs[0]["business_domain"] == "saas"
    assert logs[1]["metadata"]["review_status"] == "approved"


@pytest.mark.asyncio
async def test_news_review_and_source_changes_writes_audit_logs(
    client: AsyncClient, async_session: AsyncSession
):
    source = NewsSource(
        name="SaaS治理资讯源",
        url="https://qa.example.com/source",
        category=NewsCategory.SAAS_QUALITY,
        business_domain=NewsBusinessDomain.SAAS,
        keywords=["SaaS", "审计"],
        frequency_hours=24,
        is_active=True,
    )
    async_session.add(source)
    await async_session.commit()
    await async_session.refresh(source)

    item = NewsItem(
        source_id=source.id,
        title="SaaS发布治理资讯",
        url="https://qa.example.com/news/audit",
        summary="发布审核与治理",
        business_domain=NewsBusinessDomain.SAAS,
        tags=["audit"],
        relevance_score=90,
        review_status=NewsReviewStatus.PENDING,
    )
    async_session.add(item)
    await async_session.commit()
    await async_session.refresh(item)

    publish_response = await client.post(f"/api/v1/news/items/{item.id}/publish")
    reject_response = await client.post(f"/api/v1/news/items/{item.id}/reject")
    create_source_response = await client.post(
        "/api/v1/news/sources",
        json={
            "name": "游戏治理资讯源",
            "url": "https://qa.example.com/game-source",
            "category": "游戏测试",
            "business_domain": "game",
            "keywords": ["游戏", "审计"],
            "frequency_hours": 12,
            "is_active": True,
        },
    )
    created_source_id = create_source_response.json()["id"]
    update_source_response = await client.put(
        f"/api/v1/news/sources/{created_source_id}",
        json={"name": "游戏治理资讯源-更新", "is_active": False},
    )
    delete_source_response = await client.delete(
        f"/api/v1/news/sources/{created_source_id}"
    )

    assert publish_response.status_code == 200
    assert reject_response.status_code == 200
    assert create_source_response.status_code == 201
    assert update_source_response.status_code == 200
    assert delete_source_response.status_code == 200

    review_logs_response = await client.get(
        "/api/v1/audit/logs",
        params={
            "resource_type": "news_item",
            "resource_id": str(item.id),
            "action": "review",
        },
    )
    source_logs_response = await client.get(
        "/api/v1/audit/logs",
        params={
            "resource_type": "news_source",
            "resource_id": created_source_id,
            "business_domain": "game",
        },
    )

    assert review_logs_response.status_code == 200
    review_logs = review_logs_response.json()
    assert [log["metadata"]["review_status"] for log in review_logs] == [
        "rejected",
        "approved",
    ]

    assert source_logs_response.status_code == 200
    source_logs = source_logs_response.json()
    assert [log["action"] for log in source_logs] == ["delete", "update", "create"]
    assert {log["resource_id"] for log in source_logs} == {created_source_id}
