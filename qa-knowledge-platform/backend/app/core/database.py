from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# 创建异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """数据库模型基类"""

    pass


async def get_async_session() -> AsyncSession:
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """创建数据库表"""
    async with engine.begin() as conn:
        # 导入所有模型以确保表被创建
        from app.modules.audit.models import AuditLog
        from app.modules.files.models import UploadedFile
        from app.modules.knowledge.models import Article, ArticleTag, Category, Tag
        from app.modules.news.models import NewsItem, NewsSource
        from app.modules.notifications.models import EmailLog, NotificationSettings
        from app.modules.tools.models import Tool, ToolCategory, ToolRating
        from app.modules.users.models import Team, User

        await conn.run_sync(Base.metadata.create_all)
