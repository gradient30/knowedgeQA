from sqlalchemy import Column, String, Text, Integer, DateTime, Enum, ForeignKey, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class ToolCategoryType(str, enum.Enum):
    FUNCTIONAL = "功能测试"
    PERFORMANCE = "性能测试"
    AUTOMATION = "自动化测试"
    MOBILE = "移动测试"
    GAME = "游戏测试"
    MANAGEMENT = "管理工具"


class ToolCategory(Base):
    __tablename__ = "tool_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(Enum(ToolCategoryType), nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    tools = relationship("Tool", back_populates="category")


class Tool(Base):
    __tablename__ = "tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("tool_categories.id"), nullable=False)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    icon_url = Column(Text)
    features = Column(JSON)  # 功能特性列表
    avg_rating = Column(Numeric(3, 2), default=0.0)  # 平均评分
    rating_count = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)
    is_recommended = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    category = relationship("ToolCategory", back_populates="tools")
    ratings = relationship("ToolRating", back_populates="tool")


class ToolRating(Base):
    __tablename__ = "tool_ratings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("tools.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5分
    review = Column(Text)
    pros_cons = Column(JSON)  # 优缺点 {"pros": [], "cons": []}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    tool = relationship("Tool", back_populates="ratings")
    user = relationship("User")