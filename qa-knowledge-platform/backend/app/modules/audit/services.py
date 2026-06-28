from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditLog
from app.modules.audit.schemas import AuditLogResponse


class AuditService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_logs(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        action: Optional[str] = None,
        business_domain: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditLogResponse]:
        stmt = select(AuditLog)
        if resource_type:
            stmt = stmt.where(AuditLog.resource_type == resource_type)
        if resource_id:
            stmt = stmt.where(AuditLog.resource_id == resource_id)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        if business_domain:
            stmt = stmt.where(AuditLog.business_domain == business_domain)
        stmt = stmt.order_by(AuditLog.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return [self._to_response(log) for log in result.scalars()]

    @staticmethod
    def _to_response(log: AuditLog) -> AuditLogResponse:
        return AuditLogResponse(
            id=log.id,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            actor_id=log.actor_id,
            business_domain=log.business_domain,
            summary=log.summary,
            metadata=log.event_data or {},
            created_at=log.created_at,
        )


def add_audit_log(
    session: AsyncSession,
    *,
    action: str,
    resource_type: str,
    resource_id: UUID,
    actor_id: Optional[UUID] = None,
    business_domain: Optional[str] = None,
    summary: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    log = AuditLog(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        actor_id=actor_id,
        business_domain=business_domain,
        summary=summary,
        event_data=metadata or {},
    )
    session.add(log)
    return log
