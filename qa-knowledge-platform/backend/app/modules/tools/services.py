from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tools.models import (
    BusinessDomain,
    Tool,
    ToolCategory,
    ToolRating,
)
from app.modules.tools.schemas import (
    ToolCategoryResponse,
    ToolCreate,
    ToolRatingCreate,
    ToolRatingResponse,
    ToolResponse,
    ToolUpdate,
)


class ToolsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_tools(
        self,
        business_domain: Optional[str] = None,
        is_recommended: Optional[bool] = None,
        category_id: Optional[UUID] = None,
        project_key: Optional[str] = None,
    ):
        stmt = select(Tool)
        if business_domain:
            stmt = stmt.where(Tool.business_domain == BusinessDomain(business_domain))
        if is_recommended is not None:
            stmt = stmt.where(Tool.is_recommended == is_recommended)
        if category_id:
            stmt = stmt.where(Tool.category_id == category_id)
        if project_key:
            stmt = stmt.where(Tool.project_key == project_key)
        result = await self.session.execute(stmt.order_by(Tool.is_recommended.desc(), Tool.name.asc()))
        return [self._tool_to_response(tool) for tool in result.scalars()]

    async def create_tool(self, payload: ToolCreate):
        tool = Tool(
            category_id=payload.category_id,
            name=payload.name,
            url=payload.url,
            description=payload.description,
            business_domain=payload.business_domain,
            project_key=payload.project_key,
            features=payload.features,
        )
        self.session.add(tool)
        await self.session.commit()
        await self.session.refresh(tool)
        return self._tool_to_response(tool)

    async def get_tool(self, tool_id: UUID):
        tool = await self.session.get(Tool, tool_id)
        if tool is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工具不存在")
        return self._tool_to_response(tool)

    async def update_tool(self, tool_id: UUID, payload: ToolUpdate):
        tool = await self.session.get(Tool, tool_id)
        if tool is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工具不存在")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(tool, key, value)
        await self.session.commit()
        await self.session.refresh(tool)
        return self._tool_to_response(tool)

    async def delete_tool(self, tool_id: UUID):
        tool = await self.session.get(Tool, tool_id)
        if tool is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工具不存在")
        await self.session.delete(tool)
        await self.session.commit()
        return True

    async def list_categories(self, business_domain: Optional[str] = None):
        stmt = select(ToolCategory)
        if business_domain:
            stmt = stmt.where(ToolCategory.business_domain == BusinessDomain(business_domain))
        result = await self.session.execute(
            stmt.order_by(ToolCategory.sort_order.asc(), ToolCategory.name.asc())
        )
        return [
            ToolCategoryResponse.model_validate(category)
            for category in result.scalars()
        ]

    async def rate_tool(self, tool_id: UUID, payload: ToolRatingCreate):
        tool = await self.session.get(Tool, tool_id)
        if tool is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工具不存在")
        rating = ToolRating(
            tool_id=tool_id,
            user_id=payload.user_id,
            rating=payload.rating,
            review=payload.review,
            pros_cons=payload.pros_cons,
        )
        self.session.add(rating)
        await self.session.flush()

        avg_stmt = select(func.avg(ToolRating.rating), func.count(ToolRating.id)).where(
            ToolRating.tool_id == tool_id
        )
        avg_rating, rating_count = (await self.session.execute(avg_stmt)).one()
        tool.avg_rating = Decimal(str(round(float(avg_rating or 0), 2)))
        tool.rating_count = rating_count

        await self.session.commit()
        await self.session.refresh(rating)
        return ToolRatingResponse.model_validate(rating)

    async def favorite_tool(self, tool_id: UUID, user_id: UUID):
        tool = await self.session.get(Tool, tool_id)
        if tool is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工具不存在")
        # MVP keeps favorite as an API contract until a dedicated table lands in P2.
        return True

    async def record_usage(self, tool_id: UUID):
        tool = await self.session.get(Tool, tool_id)
        if tool is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工具不存在")
        tool.usage_count = (tool.usage_count or 0) + 1
        await self.session.commit()
        await self.session.refresh(tool)
        return {"tool_id": tool.id, "usage_count": tool.usage_count}

    def _tool_to_response(self, tool: Tool):
        return ToolResponse(
            id=tool.id,
            category_id=tool.category_id,
            name=tool.name,
            url=tool.url,
            description=tool.description,
            business_domain=tool.business_domain,
            project_key=tool.project_key,
            features=tool.features or [],
            avg_rating=tool.avg_rating or Decimal("0"),
            rating_count=tool.rating_count or 0,
            usage_count=tool.usage_count or 0,
            is_recommended=bool(tool.is_recommended),
        )
