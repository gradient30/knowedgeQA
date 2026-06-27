from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.knowledge.schemas import (
    ArticleCreate,
    ArticleResponse,
    ArticleUpdate,
    CategoryResponse,
)
from app.modules.knowledge.services import KnowledgeService

router = APIRouter()


def get_knowledge_service(
    session: AsyncSession = Depends(get_async_session),
) -> KnowledgeService:
    return KnowledgeService(session)


@router.get("/articles", response_model=List[ArticleResponse])
async def get_articles(
    business_domain: Optional[str] = None,
    review_status: Optional[str] = None,
    visibility: Optional[str] = None,
    project_key: Optional[str] = None,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """获取文章列表"""
    return await service.list_articles(
        business_domain=business_domain,
        review_status=review_status,
        visibility=visibility,
        project_key=project_key,
    )


@router.post(
    "/articles",
    response_model=ArticleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_article(
    payload: ArticleCreate,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """创建文章"""
    return await service.create_article(payload)


@router.get("/search", response_model=List[ArticleResponse])
async def search_articles(
    q: str,
    business_domain: Optional[str] = None,
    review_status: Optional[str] = None,
    visibility: Optional[str] = None,
    project_key: Optional[str] = None,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """搜索文章"""
    return await service.search_articles(
        q=q,
        business_domain=business_domain,
        review_status=review_status,
        visibility=visibility,
        project_key=project_key,
    )


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    business_domain: Optional[str] = None,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """获取分类列表"""
    return await service.list_categories(business_domain=business_domain)


@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: UUID,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """获取文章详情"""
    return await service.get_article(article_id)


@router.put("/articles/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: UUID,
    payload: ArticleUpdate,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """更新文章"""
    return await service.update_article(article_id, payload)


@router.delete("/articles/{article_id}")
async def delete_article(
    article_id: UUID,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """删除文章"""
    await service.delete_article(article_id)
    return {"success": True}
