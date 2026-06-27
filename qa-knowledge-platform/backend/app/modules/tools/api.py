from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.tools.schemas import (
    ToolCategoryResponse,
    ToolCreate,
    ToolRatingCreate,
    ToolRatingResponse,
    ToolResponse,
    ToolUpdate,
)
from app.modules.tools.services import ToolsService

router = APIRouter()


def get_tools_service(session: AsyncSession = Depends(get_async_session)) -> ToolsService:
    return ToolsService(session)


@router.get("/", response_model=List[ToolResponse])
async def get_tools(
    business_domain: Optional[str] = None,
    is_recommended: Optional[bool] = None,
    category_id: Optional[UUID] = None,
    project_key: Optional[str] = None,
    service: ToolsService = Depends(get_tools_service),
):
    """获取工具列表"""
    return await service.list_tools(
        business_domain=business_domain,
        is_recommended=is_recommended,
        category_id=category_id,
        project_key=project_key,
    )


@router.post("/", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_tool(
    payload: ToolCreate,
    service: ToolsService = Depends(get_tools_service),
):
    """添加工具"""
    return await service.create_tool(payload)


@router.get("/categories", response_model=List[ToolCategoryResponse])
async def get_tool_categories(
    business_domain: Optional[str] = None,
    service: ToolsService = Depends(get_tools_service),
):
    """获取工具分类"""
    return await service.list_categories(business_domain=business_domain)


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: UUID,
    service: ToolsService = Depends(get_tools_service),
):
    """获取工具详情"""
    return await service.get_tool(tool_id)


@router.put("/{tool_id}", response_model=ToolResponse)
async def update_tool(
    tool_id: UUID,
    payload: ToolUpdate,
    service: ToolsService = Depends(get_tools_service),
):
    """更新工具"""
    return await service.update_tool(tool_id, payload)


@router.delete("/{tool_id}")
async def delete_tool(
    tool_id: UUID,
    service: ToolsService = Depends(get_tools_service),
):
    """删除工具"""
    await service.delete_tool(tool_id)
    return {"success": True}


@router.post(
    "/{tool_id}/rating",
    response_model=ToolRatingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def rate_tool(
    tool_id: UUID,
    payload: ToolRatingCreate,
    service: ToolsService = Depends(get_tools_service),
):
    """工具评分"""
    return await service.rate_tool(tool_id, payload)


@router.post("/{tool_id}/favorite")
async def favorite_tool(
    tool_id: UUID,
    user_id: UUID,
    service: ToolsService = Depends(get_tools_service),
):
    """收藏工具"""
    await service.favorite_tool(tool_id, user_id)
    return {"success": True}


@router.post("/{tool_id}/usage")
async def record_tool_usage(
    tool_id: UUID,
    service: ToolsService = Depends(get_tools_service),
):
    """记录工具使用次数"""
    return await service.record_usage(tool_id)
