from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.intelligence.schemas import NewsSummaryResponse, SourceBackedItem
from app.modules.intelligence.services import IntelligenceService

router = APIRouter()


def get_intelligence_service(
    session: AsyncSession = Depends(get_async_session),
) -> IntelligenceService:
    return IntelligenceService(session)


@router.get("/similar-articles", response_model=List[SourceBackedItem])
async def similar_articles(
    business_domain: str,
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
    service: IntelligenceService = Depends(get_intelligence_service),
):
    return await service.similar_articles(business_domain, q, limit)


@router.get("/tool-recommendations", response_model=List[SourceBackedItem])
async def tool_recommendations(
    business_domain: str,
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
    service: IntelligenceService = Depends(get_intelligence_service),
):
    return await service.tool_recommendations(business_domain, q, limit)


@router.get("/news-summary", response_model=NewsSummaryResponse)
async def news_summary(
    business_domain: str,
    limit: int = Query(3, ge=1, le=20),
    service: IntelligenceService = Depends(get_intelligence_service),
):
    return await service.news_summary(business_domain, limit)
