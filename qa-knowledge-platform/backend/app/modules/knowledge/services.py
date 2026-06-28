from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.knowledge.models import (
    Article,
    BusinessDomain,
    Category,
    ReviewStatus,
    Visibility,
)
from app.modules.knowledge.schemas import (
    ArticleCreate,
    ArticleResponse,
    ArticleUpdate,
    CategoryResponse,
)


class KnowledgeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_articles(
        self,
        business_domain: Optional[str] = None,
        review_status: Optional[str] = None,
        visibility: Optional[str] = None,
        project_key: Optional[str] = None,
    ) -> List[ArticleResponse]:
        stmt = select(Article)
        stmt = self._apply_article_filters(
            stmt, business_domain, review_status, visibility, project_key
        )
        result = await self.session.execute(stmt)
        return [self._article_to_response(article) for article in result.scalars()]

    async def create_article(self, payload: ArticleCreate) -> ArticleResponse:
        if payload.user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建知识文章需要提供 user_id 或接入登录态",
            )
        article = Article(
            user_id=payload.user_id,
            category_id=payload.category_id,
            title=payload.title,
            summary=payload.summary,
            content=payload.content,
            type=payload.type,
            business_domain=payload.business_domain,
            visibility=payload.visibility,
            review_status=ReviewStatus.PENDING,
            project_key=payload.project_key,
            extra_data={
                "tags": payload.tags,
                "attachment_file_ids": [
                    str(file_id) for file_id in payload.attachment_file_ids
                ],
            },
        )
        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)
        return self._article_to_response(article)

    async def get_article(self, article_id: UUID) -> ArticleResponse:
        article = await self.session.get(Article, article_id)
        if article is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
        return self._article_to_response(article)

    async def update_article(
        self, article_id: UUID, payload: ArticleUpdate
    ) -> ArticleResponse:
        article = await self.session.get(Article, article_id)
        if article is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")

        updates = payload.model_dump(exclude_unset=True)
        tags = updates.pop("tags", None)
        attachment_file_ids = updates.pop("attachment_file_ids", None)
        for key, value in updates.items():
            setattr(article, key, value)
        if tags is not None or attachment_file_ids is not None:
            extra_data = dict(article.extra_data or {})
            if tags is not None:
                extra_data["tags"] = tags
            if attachment_file_ids is not None:
                extra_data["attachment_file_ids"] = [
                    str(file_id) for file_id in attachment_file_ids
                ]
            article.extra_data = extra_data

        await self.session.commit()
        await self.session.refresh(article)
        return self._article_to_response(article)

    async def delete_article(self, article_id: UUID) -> bool:
        article = await self.session.get(Article, article_id)
        if article is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
        await self.session.delete(article)
        await self.session.commit()
        return True

    async def search_articles(
        self,
        q: str,
        business_domain: Optional[str] = None,
        review_status: Optional[str] = None,
        visibility: Optional[str] = None,
        project_key: Optional[str] = None,
    ) -> List[ArticleResponse]:
        stmt = select(Article).where(
            or_(Article.title.contains(q), Article.summary.contains(q), Article.content.contains(q))
        )
        stmt = self._apply_article_filters(
            stmt, business_domain, review_status, visibility, project_key
        )
        result = await self.session.execute(stmt)
        return [self._article_to_response(article) for article in result.scalars()]

    async def list_categories(
        self, business_domain: Optional[str] = None
    ) -> List[CategoryResponse]:
        stmt = select(Category)
        if business_domain:
            stmt = stmt.where(Category.business_domain == BusinessDomain(business_domain))
        stmt = stmt.order_by(Category.sort_order.asc(), Category.name.asc())
        result = await self.session.execute(stmt)
        return [CategoryResponse.model_validate(category) for category in result.scalars()]

    def _apply_article_filters(
        self,
        stmt,
        business_domain: Optional[str],
        review_status: Optional[str],
        visibility: Optional[str],
        project_key: Optional[str],
    ):
        if business_domain:
            stmt = stmt.where(Article.business_domain == BusinessDomain(business_domain))
        if review_status:
            stmt = stmt.where(Article.review_status == ReviewStatus(review_status))
        if visibility:
            stmt = stmt.where(Article.visibility == Visibility(visibility))
        if project_key:
            stmt = stmt.where(Article.project_key == project_key)
        return stmt.order_by(Article.updated_at.desc().nullslast(), Article.created_at.desc())

    def _article_to_response(self, article: Article) -> ArticleResponse:
        extra_data = article.extra_data or {}
        return ArticleResponse(
            id=article.id,
            title=article.title,
            summary=article.summary,
            content=article.content,
            type=article.type,
            business_domain=article.business_domain,
            visibility=article.visibility,
            review_status=article.review_status,
            project_key=article.project_key,
            tags=extra_data.get("tags", []),
            attachment_file_ids=extra_data.get("attachment_file_ids", []),
        )
