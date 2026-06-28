"""Create core database tables

Revision ID: 001_create_core_tables
Revises: 72a93e43c917
Create Date: 2025-08-30 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_create_core_tables'
down_revision = '72a93e43c917'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    user_role_enum = postgresql.ENUM('member', 'admin', 'super_admin', name='userrole')
    user_role_enum.create(op.get_bind(), checkfirst=True)
    
    article_status_enum = postgresql.ENUM('draft', 'private', 'team', 'public', name='articlestatus')
    article_status_enum.create(op.get_bind(), checkfirst=True)
    
    article_type_enum = postgresql.ENUM('经验分享', 'Bug案例', '工具教程', '最佳实践', name='articletype')
    article_type_enum.create(op.get_bind(), checkfirst=True)
    
    category_type_enum = postgresql.ENUM('功能测试', '性能测试', '自动化测试', '游戏测试', '安全测试', '移动测试', name='categorytype')
    category_type_enum.create(op.get_bind(), checkfirst=True)
    
    tag_category_enum = postgresql.ENUM('技术', '工具', '平台', '难度', '类型', name='tagcategory')
    tag_category_enum.create(op.get_bind(), checkfirst=True)
    
    tool_category_type_enum = postgresql.ENUM('功能测试', '性能测试', '自动化测试', '移动测试', '游戏测试', '管理工具', name='toolcategorytype')
    tool_category_type_enum.create(op.get_bind(), checkfirst=True)
    
    news_category_enum = postgresql.ENUM('软件测试', '游戏测试', 'AI测试', '行业动态', name='newscategory')
    news_category_enum.create(op.get_bind(), checkfirst=True)

    user_role_type = postgresql.ENUM(name='userrole', create_type=False)
    article_status_type = postgresql.ENUM(name='articlestatus', create_type=False)
    article_type = postgresql.ENUM(name='articletype', create_type=False)
    category_type = postgresql.ENUM(name='categorytype', create_type=False)
    tag_category_type = postgresql.ENUM(name='tagcategory', create_type=False)
    tool_category_type = postgresql.ENUM(name='toolcategorytype', create_type=False)
    news_category_type = postgresql.ENUM(name='newscategory', create_type=False)

    # Create teams table first (referenced by users)
    op.create_table('teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('leader_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('settings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('nickname', sa.String(length=100), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('role', user_role_type, nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('skills', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Add foreign key constraint for team leader
    op.create_foreign_key('fk_teams_leader_id', 'teams', 'users', ['leader_id'], ['id'])

    # Create categories table
    op.create_table('categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', category_type, nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create tags table
    op.create_table('tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('category', tag_category_type, nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create articles table
    op.create_table('articles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('cover_image', sa.Text(), nullable=True),
        sa.Column('status', article_status_type, nullable=False),
        sa.Column('type', article_type, nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=True),
        sa.Column('like_count', sa.Integer(), nullable=True),
        sa.Column('comment_count', sa.Integer(), nullable=True),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create article_tags junction table
    op.create_table('article_tags',
        sa.Column('article_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
        sa.PrimaryKeyConstraint('article_id', 'tag_id')
    )

    # Create tool_categories table
    op.create_table('tool_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', tool_category_type, nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create tools table
    op.create_table('tools',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('icon_url', sa.Text(), nullable=True),
        sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('avg_rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('rating_count', sa.Integer(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('is_recommended', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['tool_categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create tool_ratings table
    op.create_table('tool_ratings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tool_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('review', sa.Text(), nullable=True),
        sa.Column('pros_cons', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tool_id'], ['tools.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create news_sources table
    op.create_table('news_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('selector', sa.String(length=200), nullable=True),
        sa.Column('keywords', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('frequency_hours', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('category', news_category_type, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create news_items table
    op.create_table('news_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('rank_position', sa.Integer(), nullable=True),
        sa.Column('relevance_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('scraped_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['news_sources.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )

    # Create indexes for better performance
    op.create_index('idx_articles_status', 'articles', ['status'])
    op.create_index('idx_articles_type', 'articles', ['type'])
    op.create_index('idx_articles_created_at', 'articles', ['created_at'])
    op.create_index('idx_articles_user_id', 'articles', ['user_id'])
    op.create_index('idx_articles_category_id', 'articles', ['category_id'])
    
    op.create_index('idx_tools_category_id', 'tools', ['category_id'])
    op.create_index('idx_tools_is_recommended', 'tools', ['is_recommended'])
    
    op.create_index('idx_news_items_source_id', 'news_items', ['source_id'])
    op.create_index('idx_news_items_published_at', 'news_items', ['published_at'])
    op.create_index('idx_news_items_scraped_at', 'news_items', ['scraped_at'])
    
    op.create_index('idx_tool_ratings_tool_id', 'tool_ratings', ['tool_id'])
    op.create_index('idx_tool_ratings_user_id', 'tool_ratings', ['user_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_tool_ratings_user_id', table_name='tool_ratings')
    op.drop_index('idx_tool_ratings_tool_id', table_name='tool_ratings')
    op.drop_index('idx_news_items_scraped_at', table_name='news_items')
    op.drop_index('idx_news_items_published_at', table_name='news_items')
    op.drop_index('idx_news_items_source_id', table_name='news_items')
    op.drop_index('idx_tools_is_recommended', table_name='tools')
    op.drop_index('idx_tools_category_id', table_name='tools')
    op.drop_index('idx_articles_category_id', table_name='articles')
    op.drop_index('idx_articles_user_id', table_name='articles')
    op.drop_index('idx_articles_created_at', table_name='articles')
    op.drop_index('idx_articles_type', table_name='articles')
    op.drop_index('idx_articles_status', table_name='articles')

    # Drop tables in reverse order
    op.drop_table('news_items')
    op.drop_table('news_sources')
    op.drop_table('tool_ratings')
    op.drop_table('tools')
    op.drop_table('tool_categories')
    op.drop_table('article_tags')
    op.drop_table('articles')
    op.drop_table('tags')
    op.drop_table('categories')
    
    # Drop foreign key constraint first
    op.drop_constraint('fk_teams_leader_id', 'teams', type_='foreignkey')
    op.drop_table('users')
    op.drop_table('teams')

    # Drop enum types
    postgresql.ENUM(name='newscategory').drop(op.get_bind())
    postgresql.ENUM(name='toolcategorytype').drop(op.get_bind())
    postgresql.ENUM(name='tagcategory').drop(op.get_bind())
    postgresql.ENUM(name='categorytype').drop(op.get_bind())
    postgresql.ENUM(name='articletype').drop(op.get_bind())
    postgresql.ENUM(name='articlestatus').drop(op.get_bind())
    postgresql.ENUM(name='userrole').drop(op.get_bind())
