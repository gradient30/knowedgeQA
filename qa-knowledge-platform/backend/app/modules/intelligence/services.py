from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.knowledge.models import (
    Article,
    BusinessDomain as KnowledgeBusinessDomain,
    ReviewStatus as KnowledgeReviewStatus,
)
from app.modules.news.models import (
    BusinessDomain as NewsBusinessDomain,
    NewsItem,
    ReviewStatus as NewsReviewStatus,
)
from app.modules.tools.models import BusinessDomain as ToolBusinessDomain, Tool


class IntelligenceService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def similar_articles(
        self, business_domain: str, q: str, limit: int = 5
    ) -> List[dict]:
        stmt = (
            select(Article)
            .where(Article.business_domain == KnowledgeBusinessDomain(business_domain))
            .where(Article.review_status == KnowledgeReviewStatus.APPROVED)
            .order_by(Article.updated_at.desc().nullslast(), Article.created_at.desc())
            .limit(max(limit * 3, limit))
        )
        articles = (await self.session.execute(stmt)).scalars().all()
        return [
            {
                "id": str(article.id),
                "title": article.title,
                "business_domain": article.business_domain.value,
                "summary": article.summary,
                "source_links": [f"/api/v1/knowledge/articles/{article.id}"],
                "match_reasons": self._match_reasons(q, article.title, article.summary, article.content),
            }
            for article in self._rank_by_keyword(articles, q)[:limit]
        ]

    async def tool_recommendations(
        self, business_domain: str, q: str, limit: int = 5
    ) -> List[dict]:
        stmt = (
            select(Tool)
            .where(Tool.business_domain == ToolBusinessDomain(business_domain))
            .where(Tool.is_recommended.is_(True))
            .order_by(Tool.avg_rating.desc(), Tool.usage_count.desc(), Tool.name.asc())
            .limit(max(limit * 3, limit))
        )
        tools = (await self.session.execute(stmt)).scalars().all()
        return [
            {
                "id": str(tool.id),
                "name": tool.name,
                "business_domain": tool.business_domain.value,
                "description": tool.description,
                "source_links": [f"/api/v1/tools/{tool.id}"],
                "match_reasons": self._match_reasons(
                    q, tool.name, tool.description, " ".join(tool.features or [])
                ),
            }
            for tool in self._rank_by_keyword(tools, q)[:limit]
        ]

    async def news_summary(self, business_domain: str, limit: int = 3) -> dict:
        stmt = (
            select(NewsItem)
            .where(NewsItem.business_domain == NewsBusinessDomain(business_domain))
            .where(NewsItem.review_status == NewsReviewStatus.APPROVED)
            .order_by(NewsItem.relevance_score.desc(), NewsItem.created_at.desc())
            .limit(limit)
        )
        items = (await self.session.execute(stmt)).scalars().all()
        summaries = [item.summary or item.title for item in items]
        if summaries:
            summary = "；".join(summaries)
        else:
            summary = "暂无已审核资讯可用于摘要。"
        return {
            "business_domain": business_domain,
            "summary": summary,
            "source_links": [f"/api/v1/news/items/{item.id}" for item in items],
            "item_count": len(items),
        }

    def _rank_by_keyword(self, items, q: str):
        keyword = q.lower().strip()

        def score(item):
            haystack = " ".join(
                str(value or "")
                for value in [
                    getattr(item, "title", ""),
                    getattr(item, "name", ""),
                    getattr(item, "summary", ""),
                    getattr(item, "description", ""),
                    getattr(item, "content", ""),
                    " ".join(getattr(item, "features", []) or []),
                ]
            ).lower()
            return (keyword in haystack, haystack.count(keyword))

        return sorted(items, key=score, reverse=True)

    def _match_reasons(self, q: str, *values) -> List[str]:
        reasons = ["仅使用已审核或已推荐内容", "结果包含来源链接"]
        keyword = q.strip()
        if keyword:
            haystack = " ".join(str(value or "") for value in values).lower()
            if keyword.lower() in haystack:
                reasons.append(f"关键词命中: {keyword}")
            else:
                reasons.append(f"同业务域候选: {keyword}")
        return reasons
