from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.audit.schemas import AuditLogResponse
from app.modules.audit.services import AuditService

router = APIRouter()


def get_audit_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuditService:
    return AuditService(session)


@router.get("/logs", response_model=List[AuditLogResponse])
async def list_audit_logs(
    resource_type: Optional[str] = None,
    resource_id: Optional[UUID] = None,
    action: Optional[str] = None,
    business_domain: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    service: AuditService = Depends(get_audit_service),
):
    """查询关键治理动作审计日志"""
    return await service.list_logs(
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        business_domain=business_domain,
        limit=limit,
    )
