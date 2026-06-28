"""Add file upload tables

Revision ID: add_file_upload_tables
Revises: 001_create_core_tables
Create Date: 2025-08-30 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_file_upload_tables'
down_revision = '001_create_core_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    file_type_enum = postgresql.ENUM(
        'image', 'document', 'archive', 'other', name='filetype'
    )
    file_status_enum = postgresql.ENUM(
        'uploading', 'processing', 'ready', 'error', name='filestatus'
    )
    file_type_enum.create(op.get_bind(), checkfirst=True)
    file_status_enum.create(op.get_bind(), checkfirst=True)
    file_type = postgresql.ENUM(name='filetype', create_type=False)
    file_status = postgresql.ENUM(name='filestatus', create_type=False)
    
    # Create uploaded_files table
    op.create_table('uploaded_files',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('original_name', sa.String(length=255), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_type', file_type, nullable=False),
        sa.Column('status', file_status, nullable=False),
        sa.Column('thumbnail_path', sa.Text(), nullable=True),
        sa.Column('file_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('download_count', sa.Integer(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_uploaded_files_user_id'), 'uploaded_files', ['user_id'], unique=False)
    op.create_index(op.f('ix_uploaded_files_file_type'), 'uploaded_files', ['file_type'], unique=False)
    op.create_index(op.f('ix_uploaded_files_status'), 'uploaded_files', ['status'], unique=False)
    op.create_index(op.f('ix_uploaded_files_created_at'), 'uploaded_files', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_uploaded_files_created_at'), table_name='uploaded_files')
    op.drop_index(op.f('ix_uploaded_files_status'), table_name='uploaded_files')
    op.drop_index(op.f('ix_uploaded_files_file_type'), table_name='uploaded_files')
    op.drop_index(op.f('ix_uploaded_files_user_id'), table_name='uploaded_files')
    
    # Drop table
    op.drop_table('uploaded_files')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS filestatus")
    op.execute("DROP TYPE IF EXISTS filetype")
