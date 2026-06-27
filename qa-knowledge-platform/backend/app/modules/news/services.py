from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.news.models import (
    BusinessDomain,
    NewsItem,
    NewsSource,
    ReviewStatus,
)
from app.modules.news.schemas import (
    NewsItemResponse,
    NewsSourceCreate,
    NewsSourceResponse,
    NewsSourceUpdate,
)


class NewsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_items(
        self,
        business_domain: Optional[str] = None,
        review_status: Optional[str] = None,
        q: Optional[str] = None,
    ):
        stmt = select(NewsItem)
        if business_domain:
            stmt = stmt.where(NewsItem.business_domain == BusinessDomain(business_domain))
        if review_status:
            stmt = stmt.where(NewsItem.review_status == ReviewStatus(review_status))
        if q:
            stmt = stmt.where(
                or_(NewsItem.title.contains(q), NewsItem.summary.contains(q))
            )
        result = await self.session.execute(
            stmt.order_by(NewsItem.relevance_score.desc(), NewsItem.created_at.desc())
        )
        return [self._item_to_response(item) for item in result.scalars()]

    async def publish_item(self, item_id: UUID):
        item = await self.session.get(NewsItem, item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资讯不存在")
        item.review_status = ReviewStatus.APPROVED
        item.published_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(item)
        return self._item_to_response(item)

    async def reject_item(self, item_id: UUID):
        item = await self.session.get(NewsItem, item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资讯不存在")
        item.review_status = ReviewStatus.REJECTED
        await self.session.commit()
        await self.session.refresh(item)
        return self._item_to_response(item)

    async def list_sources(self, business_domain: Optional[str] = None):
        stmt = select(NewsSource)
        if business_domain:
            stmt = stmt.where(NewsSource.business_domain == BusinessDomain(business_domain))
        result = await self.session.execute(stmt.order_by(NewsSource.name.asc()))
        return [
            NewsSourceResponse.model_validate(source)
            for source in result.scalars()
        ]

    async def create_source(self, payload: NewsSourceCreate):
        source = NewsSource(**payload.model_dump())
        self.session.add(source)
        await self.session.commit()
        await self.session.refresh(source)
        return NewsSourceResponse.model_validate(source)

    async def update_source(self, source_id: UUID, payload: NewsSourceUpdate):
        source = await self.session.get(NewsSource, source_id)
        if source is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资讯源不存在")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(source, key, value)
        await self.session.commit()
        await self.session.refresh(source)
        return NewsSourceResponse.model_validate(source)

    async def delete_source(self, source_id: UUID):
        source = await self.session.get(NewsSource, source_id)
        if source is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资讯源不存在")
        await self.session.delete(source)
        await self.session.commit()
        return True

    def _item_to_response(self, item: NewsItem):
        return NewsItemResponse(
            id=item.id,
            source_id=item.source_id,
            title=item.title,
            url=item.url,
            summary=item.summary,
            business_domain=item.business_domain,
            tags=item.tags or [],
            relevance_score=item.relevance_score or Decimal("0"),
            review_status=item.review_status,
        )
