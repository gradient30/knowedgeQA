from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.news.models import BusinessDomain, NewsCategory, ReviewStatus


class NewsSourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., min_length=1, max_length=500)
    category: NewsCategory
    business_domain: BusinessDomain = BusinessDomain.COMMON
    keywords: List[str] = Field(default_factory=list)
    frequency_hours: int = Field(24, ge=1)
    is_active: bool = True


class NewsSourceCreate(NewsSourceBase):
    selector: Optional[str] = Field(None, max_length=200)


class NewsSourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = Field(None, min_length=1, max_length=500)
    selector: Optional[str] = Field(None, max_length=200)
    category: Optional[NewsCategory] = None
    business_domain: Optional[BusinessDomain] = None
    keywords: Optional[List[str]] = None
    frequency_hours: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class NewsSourceResponse(NewsSourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    selector: Optional[str] = None


class NewsItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID
    title: str
    url: str
    summary: Optional[str] = None
    business_domain: BusinessDomain
    tags: List[str] = Field(default_factory=list)
    relevance_score: Decimal = Decimal("0")
    review_status: ReviewStatus
