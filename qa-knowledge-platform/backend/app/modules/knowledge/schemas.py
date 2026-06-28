from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.knowledge.models import (
    ArticleType,
    BusinessDomain,
    CategoryType,
    ReviewStatus,
    Visibility,
)


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    type: CategoryType
    business_domain: BusinessDomain
    sort_order: int = 0

    class Config:
        from_attributes = True


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
    id: UUID
    review_status: ReviewStatus

    class Config:
        from_attributes = True
