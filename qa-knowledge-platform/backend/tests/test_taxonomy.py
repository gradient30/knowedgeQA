from app.modules.knowledge.models import ArticleStatus
from pathlib import Path


def test_business_domain_values_exist():
    from app.modules.knowledge.models import BusinessDomain
    from app.modules.tools.models import BusinessDomain as ToolBusinessDomain
    from app.modules.news.models import BusinessDomain as NewsBusinessDomain

    assert BusinessDomain.SAAS.value == "saas"
    assert BusinessDomain.GAME.value == "game"
    assert BusinessDomain.COMMON.value == "common"
    assert ToolBusinessDomain.SAAS.value == "saas"
    assert NewsBusinessDomain.GAME.value == "game"


def test_article_lifecycle_separates_visibility_and_review_status():
    from app.modules.knowledge.models import ReviewStatus, Visibility

    assert ArticleStatus.DRAFT.value == "draft"
    assert Visibility.PRIVATE.value == "private"
    assert Visibility.TEAM.value == "team"
    assert Visibility.PUBLIC.value == "public"
    assert ReviewStatus.PENDING.value == "pending"
    assert ReviewStatus.APPROVED.value == "approved"
    assert ReviewStatus.REJECTED.value == "rejected"
    assert ReviewStatus.ARCHIVED.value == "archived"


def test_seed_taxonomy_contains_saas_and_game_categories():
    from scripts.init_db import (
        get_initial_categories_data,
        get_initial_news_sources_data,
        get_initial_tool_categories_data,
    )

    categories = get_initial_categories_data()
    tool_categories = get_initial_tool_categories_data()
    news_sources = get_initial_news_sources_data()

    category_names = {item["name"] for item in categories}
    tool_category_names = {item["name"] for item in tool_categories}
    source_names = {item["name"] for item in news_sources}

    assert "API兼容性测试" in category_names
    assert "SaaS灰度发布复盘" in category_names
    assert "游戏版本质量报告" in category_names
    assert "机型兼容测试" in category_names
    assert "SaaS接口测试工具" in tool_category_names
    assert "游戏性能测试工具" in tool_category_names
    assert "腾讯云游戏行业资讯" in source_names
    assert "网易游戏研发资讯" in source_names


def test_taxonomy_migration_adds_domain_and_review_columns():
    migration = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "20260627_add_saas_game_taxonomy.py"
    )

    assert migration.exists()
    content = migration.read_text(encoding="utf-8")
    assert "business_domain" in content
    assert "review_status" in content
    assert "visibility" in content
    assert "project_key" in content
