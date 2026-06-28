from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.knowledge.models import (
    ArticleType,
    BusinessDomain,
    CategoryType,
    ReviewStatus,
    Visibility,
)


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    type: CategoryType
    business_domain: BusinessDomain
    sort_order: int = 0


class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    summary: Optional[str] = None
    content: str = Field(..., min_length=1)
    type: ArticleType
    business_domain: BusinessDomain = BusinessDomain.COMMON
    visibility: Visibility = Visibility.TEAM
    project_key: Optional[str] = Field(None, max_length=100)
    tags: List[str] = Field(default_factory=list)
    attachment_file_ids: List[UUID] = Field(default_factory=list)


class ArticleCreate(ArticleBase):
    category_id: UUID
    user_id: Optional[UUID] = None


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    summary: Optional[str] = None
    content: Optional[str] = Field(None, min_length=1)
    type: Optional[ArticleType] = None
    category_id: Optional[UUID] = None
    business_domain: Optional[BusinessDomain] = None
    visibility: Optional[Visibility] = None
    review_status: Optional[ReviewStatus] = None
    project_key: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    attachment_file_ids: Optional[List[UUID]] = None


class ArticleResponse(ArticleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    review_status: ReviewStatus


class CommentCreate(BaseModel):
    user_id: UUID
    content: str = Field(..., min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    id: UUID
    article_id: UUID
    user_id: UUID
    content: str
    like_count: int = 0


class ArticleEngagementResponse(BaseModel):
    article_id: UUID
    like_count: int = 0
    comment_count: int = 0
    favorite_count: int = 0
    liked: bool = False
    favorited: bool = False


class KnowledgeMetricsResponse(BaseModel):
    business_domain: Optional[str] = None
    article_count: int = 0
    approved_article_count: int = 0
    pending_article_count: int = 0
    comment_count: int = 0
    like_count: int = 0
    favorite_count: int = 0
