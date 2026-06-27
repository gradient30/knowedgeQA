from sqlalchemy import Column, String, Text, Integer, DateTime, Enum, ForeignKey, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class BusinessDomain(str, enum.Enum):
    SAAS = "saas"
    GAME = "game"
    COMMON = "common"


class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class NewsCategory(str, enum.Enum):
    SOFTWARE_TESTING = "软件测试"
    SAAS_QUALITY = "SaaS质量"
    GAME_TESTING = "游戏测试"
    AI_TESTING = "AI测试"
    INDUSTRY_NEWS = "行业动态"


class NewsSource(Base):
    __tablename__ = "news_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    selector = Column(String(200))  # CSS选择器
    keywords = Column(JSON)  # 关键词列表
    business_domain = Column(
        Enum(BusinessDomain), default=BusinessDomain.COMMON, nullable=False
    )
    frequency_hours = Column(Integer, default=24)  # 抓取频率（小时）
    is_active = Column(Boolean, default=True)
    category = Column(Enum(NewsCategory), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    news_items = relationship("NewsItem", back_populates="source")


class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("news_sources.id"), nullable=False)
    business_domain = Column(
        Enum(BusinessDomain), default=BusinessDomain.COMMON, nullable=False
    )
    title = Column(String(300), nullable=False)
    url = Column(String(500), nullable=False, unique=True)
    summary = Column(Text)
    content = Column(Text)
    tags = Column(JSON)  # 标签列表
    rank_position = Column(Integer)  # 排序位置
    relevance_score = Column(Numeric(5, 2), default=0.0)  # 相关性评分
    review_status = Column(
        Enum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False
    )
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    source = relationship("NewsSource", back_populates="news_items")
