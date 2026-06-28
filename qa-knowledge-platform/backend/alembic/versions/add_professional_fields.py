"""Add professional role and experience fields.

Revision ID: add_professional_fields
Revises:
Create Date: 2024-12-31 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "add_professional_fields"
down_revision = "add_file_upload_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    professional_role_enum = postgresql.ENUM(
        "test_engineer",
        "senior_test_engineer",
        "test_lead",
        "test_manager",
        "qa_engineer",
        "automation_engineer",
        "performance_engineer",
        "security_tester",
        "game_tester",
        "mobile_tester",
        "test_architect",
        "qa_director",
        "developer",
        "product_manager",
        "student",
        "other",
        name="professionalrole",
    )
    professional_role_enum.create(op.get_bind(), checkfirst=True)

    experience_level_enum = postgresql.ENUM(
        "0-1",
        "1-3",
        "3-5",
        "5-8",
        "8+",
        name="experiencelevel",
    )
    experience_level_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "professional_role",
            professional_role_enum,
            server_default="test_engineer",
        ),
    )
    op.add_column(
        "users",
        sa.Column("experience_level", experience_level_enum, server_default="1-3"),
    )
    op.add_column("users", sa.Column("specialties", postgresql.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "specialties")
    op.drop_column("users", "experience_level")
    op.drop_column("users", "professional_role")
    op.execute("DROP TYPE IF EXISTS experiencelevel")
    op.execute("DROP TYPE IF EXISTS professionalrole")
