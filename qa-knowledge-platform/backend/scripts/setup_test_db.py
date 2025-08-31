#!/usr/bin/env python3
"""
测试数据库设置脚本
为测试环境创建独立的数据库和测试数据
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.core.database import Base
from app.core.config import settings
from app.modules.users.models import User, Team, UserRole
from app.modules.knowledge.models import Category, CategoryType, Article, ArticleStatus, ArticleType, Tag, TagCategory
from app.modules.tools.models import ToolCategory, ToolCategoryType, Tool
from app.modules.news.models import NewsSource, NewsCategory
import uuid
import bcrypt


# 测试数据库配置
TEST_DATABASE_URL = settings.DATABASE_URL.replace("qa_platform", "qa_platform_test")


async def create_test_database():
    """创建测试数据库"""
    # 连接到默认数据库来创建测试数据库
    default_db_url = settings.DATABASE_URL.rsplit('/', 1)[0] + '/postgres'
    engine = create_async_engine(default_db_url)
    
    async with engine.begin() as conn:
        # 检查测试数据库是否存在
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'qa_platform_test'")
        )
        if not result.fetchone():
            # 创建测试数据库
            await conn.execute(text("CREATE DATABASE qa_platform_test"))
            print("✅ 测试数据库创建成功")
        else:
            print("ℹ️  测试数据库已存在")
    
    await engine.dispose()


async def setup_test_tables():
    """设置测试数据库表"""
    engine = create_async_engine(TEST_DATABASE_URL)
    
    async with engine.begin() as conn:
        # 导入所有模型
        from app.modules.users.models import User, Team
        from app.modules.knowledge.models import Article, Category, Tag, ArticleTag
        from app.modules.tools.models import Tool, ToolCategory, ToolRating
        from app.modules.news.models import NewsSource, NewsItem
        from app.modules.files.models import UploadedFile
        
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("✅ 测试数据库表创建完成")


async def create_test_data():
    """创建测试数据"""
    engine = create_async_engine(TEST_DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        try:
            # 创建测试团队
            test_team = Team(
                id=uuid.uuid4(),
                name="测试团队",
                description="用于测试的QA团队",
                settings={"test_mode": True}
            )
            session.add(test_team)
            await session.flush()
            
            # 创建测试用户
            users_data = [
                {
                    "username": "test_admin",
                    "email": "admin@test.com",
                    "password": "test123",
                    "nickname": "测试管理员",
                    "role": UserRole.SUPER_ADMIN
                },
                {
                    "username": "test_user1",
                    "email": "user1@test.com", 
                    "password": "test123",
                    "nickname": "测试用户1",
                    "role": UserRole.MEMBER
                },
                {
                    "username": "test_user2",
                    "email": "user2@test.com",
                    "password": "test123", 
                    "nickname": "测试用户2",
                    "role": UserRole.ADMIN
                }
            ]
            
            created_users = []
            for user_data in users_data:
                password_hash = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                user = User(
                    id=uuid.uuid4(),
                    username=user_data["username"],
                    email=user_data["email"],
                    password_hash=password_hash,
                    nickname=user_data["nickname"],
                    role=user_data["role"],
                    team_id=test_team.id,
                    is_active=True,
                    is_verified=True
                )
                session.add(user)
                created_users.append(user)
            
            await session.flush()
            
            # 设置团队负责人
            test_team.leader_id = created_users[0].id
            
            # 创建测试分类
            test_categories = []
            categories_data = [
                {"name": "功能测试", "type": CategoryType.FUNCTIONAL},
                {"name": "性能测试", "type": CategoryType.PERFORMANCE},
                {"name": "自动化测试", "type": CategoryType.AUTOMATION}
            ]
            
            for cat_data in categories_data:
                category = Category(
                    id=uuid.uuid4(),
                    name=cat_data["name"],
                    description=f"测试用{cat_data['name']}分类",
                    type=cat_data["type"],
                    sort_order=1
                )
                session.add(category)
                test_categories.append(category)
            
            await session.flush()
            
            # 创建测试标签
            test_tags = []
            tags_data = [
                {"name": "测试标签1", "category": TagCategory.TECH},
                {"name": "测试标签2", "category": TagCategory.TOOL},
                {"name": "初级", "category": TagCategory.DIFFICULTY}
            ]
            
            for tag_data in tags_data:
                tag = Tag(
                    id=uuid.uuid4(),
                    name=tag_data["name"],
                    category=tag_data["category"],
                    color="#1890ff"
                )
                session.add(tag)
                test_tags.append(tag)
            
            await session.flush()
            
            # 创建测试文章
            articles_data = [
                {
                    "title": "测试文章1 - 功能测试经验",
                    "content": "这是一篇关于功能测试的经验分享文章...",
                    "type": ArticleType.EXPERIENCE,
                    "status": ArticleStatus.PUBLIC
                },
                {
                    "title": "测试文章2 - Bug案例分析",
                    "content": "这是一篇Bug案例分析文章...",
                    "type": ArticleType.BUG_CASE,
                    "status": ArticleStatus.TEAM
                },
                {
                    "title": "测试文章3 - 工具使用教程",
                    "content": "这是一篇工具使用教程...",
                    "type": ArticleType.TOOL_TUTORIAL,
                    "status": ArticleStatus.PRIVATE
                }
            ]
            
            for i, article_data in enumerate(articles_data):
                article = Article(
                    id=uuid.uuid4(),
                    user_id=created_users[i % len(created_users)].id,
                    category_id=test_categories[i % len(test_categories)].id,
                    title=article_data["title"],
                    summary=f"这是{article_data['title']}的摘要",
                    content=article_data["content"],
                    type=article_data["type"],
                    status=article_data["status"],
                    view_count=10 * (i + 1),
                    like_count=5 * (i + 1)
                )
                session.add(article)
            
            # 创建工具分类
            tool_category = ToolCategory(
                id=uuid.uuid4(),
                name="测试工具分类",
                description="用于测试的工具分类",
                type=ToolCategoryType.AUTOMATION,
                sort_order=1
            )
            session.add(tool_category)
            await session.flush()
            
            # 创建测试工具
            test_tool = Tool(
                id=uuid.uuid4(),
                category_id=tool_category.id,
                name="测试工具",
                url="https://example.com/test-tool",
                description="这是一个测试工具",
                features=["功能1", "功能2", "功能3"],
                avg_rating=4.5,
                rating_count=10,
                usage_count=50,
                is_recommended=True
            )
            session.add(test_tool)
            
            # 创建测试资讯源
            news_source = NewsSource(
                id=uuid.uuid4(),
                name="测试资讯源",
                url="https://example.com/test-news",
                category=NewsCategory.SOFTWARE_TESTING,
                keywords=["测试", "质量"],
                frequency_hours=24,
                is_active=True
            )
            session.add(news_source)
            
            await session.commit()
            print("✅ 测试数据创建完成")
            print(f"   - 测试团队: 1个")
            print(f"   - 测试用户: {len(users_data)}个")
            print(f"   - 测试分类: {len(categories_data)}个")
            print(f"   - 测试文章: {len(articles_data)}篇")
            print(f"   - 测试工具: 1个")
            print(f"   - 测试资讯源: 1个")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ 创建测试数据失败: {e}")
            raise
        finally:
            await engine.dispose()


async def cleanup_test_database():
    """清理测试数据库"""
    # 连接到默认数据库来删除测试数据库
    default_db_url = settings.DATABASE_URL.rsplit('/', 1)[0] + '/postgres'
    engine = create_async_engine(default_db_url)
    
    async with engine.begin() as conn:
        # 断开所有连接
        await conn.execute(
            text("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'qa_platform_test'")
        )
        # 删除测试数据库
        await conn.execute(text("DROP DATABASE IF EXISTS qa_platform_test"))
        print("✅ 测试数据库已清理")
    
    await engine.dispose()


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="测试数据库管理")
    parser.add_argument("action", choices=["setup", "cleanup"], help="操作类型")
    args = parser.parse_args()
    
    if args.action == "setup":
        print("🚀 设置测试数据库...")
        await create_test_database()
        await setup_test_tables()
        await create_test_data()
        print(f"\n✅ 测试数据库设置完成!")
        print(f"测试数据库URL: {TEST_DATABASE_URL}")
        print("\n测试用户:")
        print("  - test_admin / test123 (超级管理员)")
        print("  - test_user1 / test123 (普通成员)")
        print("  - test_user2 / test123 (管理员)")
        
    elif args.action == "cleanup":
        print("🧹 清理测试数据库...")
        await cleanup_test_database()
        print("✅ 测试数据库清理完成!")


if __name__ == "__main__":
    asyncio.run(main())