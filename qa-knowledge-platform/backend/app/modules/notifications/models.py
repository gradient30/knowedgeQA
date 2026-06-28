import enum
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func

from app.core.database import Base


class EmailLogStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class NotificationSettings(Base):
    __tablename__ = "notification_settings"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scope = Column(String(50), nullable=False, unique=True, default="global")
    notifications = Column(JSON, nullable=False)
    updated_by_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    to_email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    template_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    error_message = Column(Text, nullable=True)
    sent_by_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    sent_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
