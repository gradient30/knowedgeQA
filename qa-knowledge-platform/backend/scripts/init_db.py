#!/usr/bin/env python3
"""
数据库初始化脚本
创建数据库表并插入初始数据
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import engine, AsyncSessionLocal, Base
from app.core.config import settings
from app.modules.users.models import User, Team, UserRole
from app.modules.knowledge.models import (
    BusinessDomain as KnowledgeBusinessDomain,
    Category,
    CategoryType,
    Tag,
    TagCategory,
)
from app.modules.tools.models import (
    BusinessDomain as ToolBusinessDomain,
    ToolCategory,
    ToolCategoryType,
)
from app.modules.news.models import (
    BusinessDomain as NewsBusinessDomain,
    NewsCategory,
    NewsSource,
)
import uuid
from datetime import datetime
import bcrypt


def get_initial_categories_data():
    return [
        {
            "name": "功能测试",
            "description": "验证软件功能是否符合需求规格说明书的测试",
            "type": CategoryType.FUNCTIONAL,
            "business_domain": KnowledgeBusinessDomain.COMMON,
        },
        {
            "name": "性能测试",
            "description": "验证系统在特定负载下的性能表现",
            "type": CategoryType.PERFORMANCE,
            "business_domain": KnowledgeBusinessDomain.COMMON,
        },
        {
            "name": "自动化测试",
            "description": "使用自动化工具和脚本进行的测试",
            "type": CategoryType.AUTOMATION,
            "business_domain": KnowledgeBusinessDomain.COMMON,
        },
        {
            "name": "API兼容性测试",
            "description": "SaaS接口版本、调用方和破坏性变更验证",
            "type": CategoryType.SAAS_API,
            "business_domain": KnowledgeBusinessDomain.SAAS,
        },
        {
            "name": "SaaS灰度发布复盘",
            "description": "灰度批次、监控指标、异常决策和回滚复盘",
            "type": CategoryType.SAAS_RELEASE,
            "business_domain": KnowledgeBusinessDomain.SAAS,
        },
        {
            "name": "游戏版本质量报告",
            "description": "游戏版本提审、阻塞缺陷、性能和质量结论",
            "type": CategoryType.GAME,
            "business_domain": KnowledgeBusinessDomain.GAME,
        },
        {
            "name": "机型兼容测试",
            "description": "游戏多端设备、系统、画质档位和崩溃验证",
            "type": CategoryType.GAME_COMPATIBILITY,
            "business_domain": KnowledgeBusinessDomain.GAME,
        },
        {
            "name": "游戏性能测试",
            "description": "帧率、内存、弱网、发热和压测结果沉淀",
            "type": CategoryType.GAME_PERFORMANCE,
            "business_domain": KnowledgeBusinessDomain.GAME,
        },
        {
            "name": "安全测试",
            "description": "验证系统安全性和数据保护的测试",
            "type": CategoryType.SECURITY,
            "business_domain": KnowledgeBusinessDomain.COMMON,
        },
        {
            "name": "移动测试",
            "description": "移动应用和移动端网页的测试",
            "type": CategoryType.MOBILE,
            "business_domain": KnowledgeBusinessDomain.COMMON,
        },
    ]


def get_initial_tool_categories_data():
    return [
        {
            "name": "功能测试工具",
            "description": "用于功能测试的各种工具和平台",
            "type": ToolCategoryType.FUNCTIONAL,
            "business_domain": ToolBusinessDomain.COMMON,
        },
        {
            "name": "SaaS接口测试工具",
            "description": "SaaS API兼容性、契约测试和回归验证工具",
            "type": ToolCategoryType.API,
            "business_domain": ToolBusinessDomain.SAAS,
        },
        {
            "name": "性能测试工具",
            "description": "负载测试、压力测试、性能监控工具",
            "type": ToolCategoryType.PERFORMANCE,
            "business_domain": ToolBusinessDomain.COMMON,
        },
        {
            "name": "自动化测试工具",
            "description": "UI自动化、API自动化、测试框架",
            "type": ToolCategoryType.AUTOMATION,
            "business_domain": ToolBusinessDomain.COMMON,
        },
        {
            "name": "移动测试工具",
            "description": "移动应用测试、设备管理工具",
            "type": ToolCategoryType.MOBILE,
            "business_domain": ToolBusinessDomain.COMMON,
        },
        {
            "name": "游戏性能测试工具",
            "description": "游戏帧率、弱网、压测、兼容性和稳定性工具",
            "type": ToolCategoryType.GAME,
            "business_domain": ToolBusinessDomain.GAME,
        },
        {
            "name": "测试管理工具",
            "description": "测试用例管理、缺陷管理、项目管理",
            "type": ToolCategoryType.MANAGEMENT,
            "business_domain": ToolBusinessDomain.COMMON,
        },
    ]


def get_initial_news_sources_data():
    return [
        {
            "name": "软件测试网",
            "url": "https://www.51testing.com",
            "category": NewsCategory.SOFTWARE_TESTING,
            "business_domain": NewsBusinessDomain.COMMON,
            "keywords": ["软件测试", "质量保证", "测试方法", "测试工具"],
            "frequency_hours": 24,
        },
        {
            "name": "TesterHome",
            "url": "https://testerhome.com",
            "category": NewsCategory.SOFTWARE_TESTING,
            "business_domain": NewsBusinessDomain.COMMON,
            "keywords": ["自动化测试", "移动测试", "性能测试"],
            "frequency_hours": 12,
        },
        {
            "name": "腾讯云游戏行业资讯",
            "url": "https://www.tencentcloud.com/solutions/gaming",
            "category": NewsCategory.GAME_TESTING,
            "business_domain": NewsBusinessDomain.GAME,
            "keywords": ["游戏质量", "游戏开发", "游戏云", "性能"],
            "frequency_hours": 24,
        },
        {
            "name": "网易游戏研发资讯",
            "url": "https://www.neteasegames.com/news/",
            "category": NewsCategory.GAME_TESTING,
            "business_domain": NewsBusinessDomain.GAME,
            "keywords": ["网易游戏", "游戏研发", "AI测试", "自动化测试"],
            "frequency_hours": 24,
        },
        {
            "name": "SaaS质量工程资讯",
            "url": "https://dora.dev/research/",
            "category": NewsCategory.SAAS_QUALITY,
            "business_domain": NewsBusinessDomain.SAAS,
            "keywords": ["SaaS", "DevOps", "质量工程", "交付效能"],
            "frequency_hours": 48,
        },
    ]


async def create_tables():
    """创建所有数据库表"""
    print("正在创建数据库表...")
    async with engine.begin() as conn:
        # 导入所有模型以确保表被创建
        from app.modules.users.models import User, Team
        from app.modules.knowledge.models import Article, Category, Tag, ArticleTag
        from app.modules.tools.models import Tool, ToolCategory, ToolRating
        from app.modules.news.models import NewsSource, NewsItem
        from app.modules.files.models import UploadedFile
        
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表创建完成")


async def create_initial_data():
    """创建初始数据"""
    async with AsyncSessionLocal() as session:
        try:
            # 创建默认团队
            default_team = Team(
                id=uuid.uuid4(),
                name="QA测试团队",
                description="默认的QA测试团队，负责产品质量保证工作",
                settings={
                    "default_article_visibility": "team",
                    "allow_external_sharing": True,
                    "require_article_approval": False
                }
            )
            session.add(default_team)
            await session.flush()  # 获取team_id
            
            # 创建超级管理员用户
            password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin_user = User(
                id=uuid.uuid4(),
                username="admin",
                email="admin@qa-platform.com",
                password_hash=password_hash,
                nickname="系统管理员",
                bio="QA测试知识协作平台系统管理员",
                role=UserRole.SUPER_ADMIN,
                team_id=default_team.id,
                skills={
                    "测试类型": ["功能测试", "性能测试", "自动化测试"],
                    "工具经验": ["Selenium", "JMeter", "Postman"],
                    "编程语言": ["Python", "Java", "JavaScript"]
                },
                is_active=True,
                is_verified=True
            )
            session.add(admin_user)
            await session.flush()
            
            # 设置团队负责人
            default_team.leader_id = admin_user.id
            
            # 创建测试分类
            categories_data = get_initial_categories_data()
            
            for i, cat_data in enumerate(categories_data):
                category = Category(
                    id=uuid.uuid4(),
                    name=cat_data["name"],
                    description=cat_data["description"],
                    type=cat_data["type"],
                    business_domain=cat_data["business_domain"],
                    sort_order=i + 1
                )
                session.add(category)
            
            # 创建常用标签
            tags_data = [
                # 技术标签
                {"name": "Selenium", "category": TagCategory.TECH, "color": "#1890ff"},
                {"name": "JMeter", "category": TagCategory.TECH, "color": "#52c41a"},
                {"name": "Postman", "category": TagCategory.TECH, "color": "#fa8c16"},
                {"name": "Cypress", "category": TagCategory.TECH, "color": "#722ed1"},
                {"name": "Playwright", "category": TagCategory.TECH, "color": "#eb2f96"},
                
                # 工具标签
                {"name": "API测试", "category": TagCategory.TOOL, "color": "#13c2c2"},
                {"name": "UI测试", "category": TagCategory.TOOL, "color": "#faad14"},
                {"name": "数据库测试", "category": TagCategory.TOOL, "color": "#a0d911"},
                
                # 平台标签
                {"name": "Web", "category": TagCategory.PLATFORM, "color": "#1890ff"},
                {"name": "Android", "category": TagCategory.PLATFORM, "color": "#52c41a"},
                {"name": "iOS", "category": TagCategory.PLATFORM, "color": "#faad14"},
                {"name": "微信小程序", "category": TagCategory.PLATFORM, "color": "#722ed1"},
                
                # 难度标签
                {"name": "初级", "category": TagCategory.DIFFICULTY, "color": "#52c41a"},
                {"name": "中级", "category": TagCategory.DIFFICULTY, "color": "#faad14"},
                {"name": "高级", "category": TagCategory.DIFFICULTY, "color": "#f5222d"},
                
                # 类型标签
                {"name": "Bug案例", "category": TagCategory.TYPE, "color": "#f5222d"},
                {"name": "最佳实践", "category": TagCategory.TYPE, "color": "#52c41a"},
                {"name": "工具教程", "category": TagCategory.TYPE, "color": "#1890ff"},
                {"name": "经验分享", "category": TagCategory.TYPE, "color": "#722ed1"}
            ]
            
            for tag_data in tags_data:
                tag = Tag(
                    id=uuid.uuid4(),
                    name=tag_data["name"],
                    category=tag_data["category"],
                    color=tag_data["color"],
                    usage_count=0
                )
                session.add(tag)
            
            # 创建工具分类
            tool_categories_data = get_initial_tool_categories_data()
            
            for i, tool_cat_data in enumerate(tool_categories_data):
                tool_category = ToolCategory(
                    id=uuid.uuid4(),
                    name=tool_cat_data["name"],
                    description=tool_cat_data["description"],
                    type=tool_cat_data["type"],
                    business_domain=tool_cat_data["business_domain"],
                    sort_order=i + 1
                )
                session.add(tool_category)
            
            # 创建默认资讯源
            news_sources_data = get_initial_news_sources_data()
            
            for news_data in news_sources_data:
                news_source = NewsSource(
                    id=uuid.uuid4(),
                    name=news_data["name"],
                    url=news_data["url"],
                    category=news_data["category"],
                    business_domain=news_data["business_domain"],
                    keywords=news_data["keywords"],
                    frequency_hours=news_data["frequency_hours"],
                    is_active=True
                )
                session.add(news_source)
            
            await session.commit()
            print("✅ 初始数据创建完成")
            print(f"   - 默认团队: {default_team.name}")
            print(f"   - 管理员用户: {admin_user.username} (密码: admin123)")
            print(f"   - 测试分类: {len(categories_data)} 个")
            print(f"   - 常用标签: {len(tags_data)} 个")
            print(f"   - 工具分类: {len(tool_categories_data)} 个")
            print(f"   - 资讯源: {len(news_sources_data)} 个")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ 创建初始数据失败: {e}")
            raise


async def check_database_connection():
    """检查数据库连接"""
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ 数据库连接正常")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


async def main():
    """主函数"""
    print("🚀 开始初始化QA测试知识协作平台数据库...")
    print(f"数据库URL: {settings.DATABASE_URL}")
    
    # 检查数据库连接
    if not await check_database_connection():
        print("请确保数据库服务正在运行并且连接配置正确")
        return
    
    try:
        # 创建表
        await create_tables()
        
        # 创建初始数据
        await create_initial_data()
        
        print("\n🎉 数据库初始化完成！")
        print("\n📋 登录信息:")
        print("   用户名: admin")
        print("   密码: admin123")
        print("   邮箱: admin@qa-platform.com")
        print("\n🔗 下一步:")
        print("   1. 启动后端服务: uvicorn app.main:app --reload")
        print("   2. 访问API文档: http://localhost:8000/docs")
        print("   3. 启动前端服务并开始使用平台")
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
