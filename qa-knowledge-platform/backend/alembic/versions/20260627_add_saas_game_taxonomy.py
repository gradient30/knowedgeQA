"""Add SaaS and game QA taxonomy fields.

Revision ID: 20260627_add_saas_game_taxonomy
Revises: 001_create_core_tables
Create Date: 2026-06-27 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260627_add_saas_game_taxonomy"
down_revision = "001_create_core_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE categorytype ADD VALUE IF NOT EXISTS 'SaaS接口测试'")
    op.execute("ALTER TYPE categorytype ADD VALUE IF NOT EXISTS 'SaaS发布质量'")
    op.execute("ALTER TYPE categorytype ADD VALUE IF NOT EXISTS '游戏兼容性测试'")
    op.execute("ALTER TYPE categorytype ADD VALUE IF NOT EXISTS '游戏性能测试'")
    op.execute("ALTER TYPE toolcategorytype ADD VALUE IF NOT EXISTS '接口测试'")
    op.execute("ALTER TYPE newscategory ADD VALUE IF NOT EXISTS 'SaaS质量'")

    business_domain_enum = postgresql.ENUM(
        "saas", "game", "common", name="businessdomain"
    )
    review_status_enum = postgresql.ENUM(
        "pending", "approved", "rejected", "archived", name="reviewstatus"
    )
    visibility_enum = postgresql.ENUM("private", "team", "public", name="visibility")

    business_domain_enum.create(op.get_bind(), checkfirst=True)
    review_status_enum.create(op.get_bind(), checkfirst=True)
    visibility_enum.create(op.get_bind(), checkfirst=True)

    business_domain_type = postgresql.ENUM(name="businessdomain", create_type=False)
    review_status_type = postgresql.ENUM(name="reviewstatus", create_type=False)
    visibility_type = postgresql.ENUM(name="visibility", create_type=False)

    op.add_column(
        "categories",
        sa.Column(
            "business_domain",
            business_domain_type,
            nullable=False,
            server_default="common",
        ),
    )
    op.add_column("articles", sa.Column("project_key", sa.String(length=100)))
    op.add_column(
        "articles",
        sa.Column(
            "business_domain",
            business_domain_type,
            nullable=False,
            server_default="common",
        ),
    )
    op.add_column(
        "articles",
        sa.Column(
            "visibility",
            visibility_type,
            nullable=False,
            server_default="team",
        ),
    )
    op.add_column(
        "articles",
        sa.Column(
            "review_status",
            review_status_type,
            nullable=False,
            server_default="pending",
        ),
    )
    op.add_column(
        "tool_categories",
        sa.Column(
            "business_domain",
            business_domain_type,
            nullable=False,
            server_default="common",
        ),
    )
    op.add_column(
        "tools",
        sa.Column(
            "business_domain",
            business_domain_type,
            nullable=False,
            server_default="common",
        ),
    )
    op.add_column("tools", sa.Column("project_key", sa.String(length=100)))
    op.add_column(
        "news_sources",
        sa.Column(
            "business_domain",
            business_domain_type,
            nullable=False,
            server_default="common",
        ),
    )
    op.add_column(
        "news_items",
        sa.Column(
            "business_domain",
            business_domain_type,
            nullable=False,
            server_default="common",
        ),
    )
    op.add_column(
        "news_items",
        sa.Column(
            "review_status",
            review_status_type,
            nullable=False,
            server_default="pending",
        ),
    )


def downgrade() -> None:
    op.drop_column("news_items", "review_status")
    op.drop_column("news_items", "business_domain")
    op.drop_column("news_sources", "business_domain")
    op.drop_column("tools", "project_key")
    op.drop_column("tools", "business_domain")
    op.drop_column("tool_categories", "business_domain")
    op.drop_column("articles", "review_status")
    op.drop_column("articles", "visibility")
    op.drop_column("articles", "business_domain")
    op.drop_column("articles", "project_key")
    op.drop_column("categories", "business_domain")
    op.execute("DROP TYPE IF EXISTS visibility")
    op.execute("DROP TYPE IF EXISTS reviewstatus")
    op.execute("DROP TYPE IF EXISTS businessdomain")
