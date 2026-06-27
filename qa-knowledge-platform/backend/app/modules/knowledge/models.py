from sqlalchemy import Column, String, Text, Integer, DateTime, Enum, ForeignKey, Boolean
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


class Visibility(str, enum.Enum):
    PRIVATE = "private"
    TEAM = "team"
    PUBLIC = "public"


class ArticleStatus(str, enum.Enum):
    DRAFT = "draft"
    PRIVATE = "private"
    TEAM = "team"
    PUBLIC = "public"


class ArticleType(str, enum.Enum):
    EXPERIENCE = "经验分享"
    BUG_CASE = "Bug案例"
    TOOL_TUTORIAL = "工具教程"
    BEST_PRACTICE = "最佳实践"


class CategoryType(str, enum.Enum):
    FUNCTIONAL = "功能测试"
    PERFORMANCE = "性能测试"
    AUTOMATION = "自动化测试"
    SAAS_API = "SaaS接口测试"
    SAAS_RELEASE = "SaaS发布质量"
    GAME = "游戏测试"
    GAME_COMPATIBILITY = "游戏兼容性测试"
    GAME_PERFORMANCE = "游戏性能测试"
    SECURITY = "安全测试"
    MOBILE = "移动测试"


class TagCategory(str, enum.Enum):
    TECH = "技术"
    TOOL = "工具"
    PLATFORM = "平台"
    DIFFICULTY = "难度"
    TYPE = "类型"


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(Enum(CategoryType), nullable=False)
    business_domain = Column(
        Enum(BusinessDomain), default=BusinessDomain.COMMON, nullable=False
    )
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    articles = relationship("Article", back_populates="category")
    parent = relationship("Category", remote_side=[id])


class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True))  # 项目ID，V2.0功能
    project_key = Column(String(100))
    business_domain = Column(
        Enum(BusinessDomain), default=BusinessDomain.COMMON, nullable=False
    )
    title = Column(String(200), nullable=False)
    summary = Column(Text)
    content = Column(Text, nullable=False)
    cover_image = Column(Text)
    status = Column(Enum(ArticleStatus), default=ArticleStatus.DRAFT, nullable=False)
    visibility = Column(Enum(Visibility), default=Visibility.TEAM, nullable=False)
    review_status = Column(
        Enum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False
    )
    type = Column(Enum(ArticleType), nullable=False)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    extra_data = Column(JSON)  # 重命名避免与SQLAlchemy metadata冲突
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))

    # 关系
    author = relationship("User", back_populates="articles")
    category = relationship("Category", back_populates="articles")
    tags = relationship("Tag", secondary="article_tags", back_populates="articles")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(7))  # 十六进制颜色值
    category = Column(Enum(TagCategory), nullable=False)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    articles = relationship("Article", secondary="article_tags", back_populates="tags")


class ArticleTag(Base):
    __tablename__ = "article_tags"

    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True)
