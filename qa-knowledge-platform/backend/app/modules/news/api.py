from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.news.schemas import (
    NewsItemResponse,
    NewsSourceCreate,
    NewsSourceResponse,
    NewsSourceUpdate,
)
from app.modules.news.services import NewsService

router = APIRouter()


def get_news_service(session: AsyncSession = Depends(get_async_session)) -> NewsService:
    return NewsService(session)


@router.get("/items", response_model=List[NewsItemResponse])
async def get_news_items(
    business_domain: Optional[str] = None,
    review_status: Optional[str] = None,
    q: Optional[str] = None,
    service: NewsService = Depends(get_news_service),
):
    """获取资讯列表"""
    return await service.list_items(
        business_domain=business_domain,
        review_status=review_status,
        q=q,
    )


@router.post("/items/{item_id}/publish", response_model=NewsItemResponse)
async def publish_news_item(
    item_id: UUID,
    service: NewsService = Depends(get_news_service),
):
    """发布资讯"""
    return await service.publish_item(item_id)


@router.post("/items/{item_id}/reject", response_model=NewsItemResponse)
async def reject_news_item(
    item_id: UUID,
    service: NewsService = Depends(get_news_service),
):
    """驳回资讯"""
    return await service.reject_item(item_id)


@router.get("/sources", response_model=List[NewsSourceResponse])
async def get_news_sources(
    business_domain: Optional[str] = None,
    service: NewsService = Depends(get_news_service),
):
    """获取资讯源列表"""
    return await service.list_sources(business_domain=business_domain)


@router.post(
    "/sources",
    response_model=NewsSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_news_source(
    payload: NewsSourceCreate,
    service: NewsService = Depends(get_news_service),
):
    """创建资讯源"""
    return await service.create_source(payload)


@router.put("/sources/{source_id}", response_model=NewsSourceResponse)
async def update_news_source(
    source_id: UUID,
    payload: NewsSourceUpdate,
    service: NewsService = Depends(get_news_service),
):
    """更新资讯源"""
    return await service.update_source(source_id, payload)


@router.delete("/sources/{source_id}")
async def delete_news_source(
    source_id: UUID,
    service: NewsService = Depends(get_news_service),
):
    """删除资讯源"""
    await service.delete_source(source_id)
    return {"success": True}
