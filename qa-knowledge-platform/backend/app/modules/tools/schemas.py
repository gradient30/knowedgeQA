from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.tools.models import BusinessDomain, ToolCategoryType


class ToolCategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    type: ToolCategoryType
    business_domain: BusinessDomain
    sort_order: int = 0

    class Config:
        from_attributes = True


class ToolBase(BaseModel):
    category_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    business_domain: BusinessDomain = BusinessDomain.COMMON
    project_key: Optional[str] = Field(None, max_length=100)
    features: List[str] = Field(default_factory=list)


class ToolCreate(ToolBase):
    pass


class ToolUpdate(BaseModel):
    category_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=1)
    business_domain: Optional[BusinessDomain] = None
    project_key: Optional[str] = Field(None, max_length=100)
    features: Optional[List[str]] = None
    is_recommended: Optional[bool] = None


class ToolResponse(ToolBase):
    id: UUID
    avg_rating: Decimal = Decimal("0")
    rating_count: int = 0
    usage_count: int = 0
    is_recommended: bool = False

    class Config:
        from_attributes = True


class ToolRatingCreate(BaseModel):
    user_id: UUID
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = None
    pros_cons: Dict[str, List[str]] = Field(default_factory=dict)


class ToolRatingResponse(BaseModel):
    id: UUID
    tool_id: UUID
    user_id: UUID
    rating: int
    review: Optional[str] = None
    pros_cons: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True
