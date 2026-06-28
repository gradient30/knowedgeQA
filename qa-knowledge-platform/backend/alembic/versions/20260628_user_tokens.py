"""Add user auth token table

Revision ID: 20260628_user_tokens
Revises: 20260628_notification_governance
Create Date: 2026-06-28 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260628_user_tokens"
down_revision = "20260628_notification_governance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("token_type", sa.String(length=50), nullable=False),
        sa.Column("extra_data", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_tokens_token_hash", "user_tokens", ["token_hash"], unique=True
    )
    op.create_index("ix_user_tokens_token_type", "user_tokens", ["token_type"])


def downgrade() -> None:
    op.drop_index("ix_user_tokens_token_type", table_name="user_tokens")
    op.drop_index("ix_user_tokens_token_hash", table_name="user_tokens")
    op.drop_table("user_tokens")
