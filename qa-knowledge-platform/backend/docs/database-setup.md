# QA测试知识协作平台 - 数据库设计文档

## 概述

本文档描述了QA测试知识协作平台的数据库设计，包括表结构、关系、索引和初始化流程。

## 核心表结构

### 用户相关表

#### users (用户表)
存储用户基本信息和认证数据

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | UUID | 用户唯一标识 | 主键 |
| username | VARCHAR(50) | 用户名 | 唯一，非空 |
| email | VARCHAR(100) | 邮箱地址 | 唯一，非空 |
| password_hash | VARCHAR(255) | 密码哈希 | 非空 |
| nickname | VARCHAR(100) | 昵称 | 可空 |
| avatar_url | TEXT | 头像URL | 可空 |
| bio | TEXT | 个人简介 | 可空 |
| role | ENUM | 用户角色 | member/admin/super_admin |
| team_id | UUID | 所属团队ID | 外键 |
| skills | JSON | 技能标签 | 可空 |
| is_active | BOOLEAN | 是否激活 | 默认true |
| is_verified | BOOLEAN | 邮箱是否验证 | 默认false |
| last_login | TIMESTAMP | 最后登录时间 | 可空 |
| created_at | TIMESTAMP | 创建时间 | 自动生成 |
| updated_at | TIMESTAMP | 更新时间 | 自动更新 |

#### teams (团队表)
存储团队信息和配置

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | UUID | 团队唯一标识 | 主键 |
| name | VARCHAR(100) | 团队名称 | 非空 |
| description | TEXT | 团队描述 | 可空 |
| leader_id | UUID | 团队负责人ID | 外键 |
| settings | JSON | 团队配置 | 可空 |
| created_at | TIMESTAMP | 创建时间 | 自动生成 |
| updated_at | TIMESTAMP | 更新时间 | 自动更新 |

### 知识库相关表

#### categories (分类表)
存储测试分类信息

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | UUID | 分类唯一标识 | 主键 |
| name | VARCHAR(100) | 分类名称 | 非空 |
| description | TEXT | 分类描述 | 可空 |
| type | ENUM | 分类类型 | 功能测试/性能测试/自动化测试等 |
| parent_id | UUID | 父分类ID | 外键，可空 |
| sort_order | INTEGER | 排序序号 | 默认0 |
| created_at | TIMESTAMP | 创建时间 | 自动生成 |

#### articles (文章表)
存储测试经验文章

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | UUID | 文章唯一标识 | 主键 |
| user_id | UUID | 作者ID | 外键，非空 |
| category_id | UUID | 分类ID | 外键，非空 |
| project_id | UUID | 项目ID | 可空(V2.0功能) |
| title | VARCHAR(200) | 文章标题 | 非空 |
| summary | TEXT | 文章摘要 | 可空 |
| content | TEXT | 文章内容 | 非空 |
| cover_image | TEXT | 封面图片URL | 可空 |
| status | ENUM | 发布状态 | draft/private/team/public |
| type | ENUM | 文章类型 | 经验分享/Bug案例/工具教程/最佳实践 |
| view_count | INTEGER | 浏览次数 | 默认0 |
| like_count | INTEGER | 点赞次数 | 默认0 |
| comment_count | INTEGER | 评论次数 | 默认0 |
| extra_data | JSON | 扩展数据 | 可空 |
| created_at | TIMESTAMP | 创建时间 | 自动生成 |
| updated_at | TIMESTAMP | 更新时间 | 自动更新 |
| published_at | TIMESTAMP | 发布时间 | 可空 |

#### tags (标签表)
存储文章标签

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | UUID | 标签唯一标识 | 主键 |
| name | VARCHAR(50) | 标签名称 | 唯一，非空 |
| color | VARCHAR(7) | 标签颜色 | 十六进制颜色值 |
| category | ENUM | 标签分类 | 技术/工具/平台/难度/类型 |
| usage_count | INTEGER | 使用次数 | 默认0 |
| created_at | TIMESTAMP | 创建时间 | 自动生成 |

#### article_tags (文章标签关联表)
多对多关系表

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| article_id | UUID | 文章ID | 外键，主键 |
| tag_id | UUID | 标签ID | 外键，主键 |

### 工具库相关表

#### tool_categories (工具分类表)
存储测试工具分类

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | UUID | 分类唯一标识 | 主键 |
| name | VARCHAR(100) | 分类名称 | 非空 |
| description | TEXT | 分类描述 | 可空 |
| type | ENUM | 分类类型 | 功能测试/性能测试/自动化测试等 |
| sort_order | INTEGER | 排序序号 | 默认0 |
| created_at | TIMESTAMP | 创建时间 | 自动生成 |

#### tools (工具表)
存储测试工具信息

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | UUID | 工具唯一标识 | 主键 |
| category_id | UUID | 分类ID | 外键，非空 |
| name | VARCHAR(100) | 工具名称 | 非空 |
| url | VARCHAR(500) | 工具链接 | 非空 |
| description | TEXT | 工具描述 | 非空 |
| icon_url | TEXT | 图标URL | 可空 |
| features | JSON | 功能特性列表 | 可空 |
| avg_rating | DECIMAL(3,2) | 平均评分 | 默认0.0 |
| rating_count | INTEGER | 评分次数 | 默认0 |
| usage_count | INTEGER | 使用次数 | 默认0 |
| is_recommended | BOOLEAN | 是否推荐 | 默认false |
| created_at | TIMESTAMP | 创建时间 | 自动生成 |
| updated_at | TIMESTAMP | 更新时间 | 自动更新 |

#### tool_ratings (工具评分表)
存储用户对工具的评分

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | UUID | 评分唯一标识 | 主键 |
| tool_id | UUID | 工具ID | 外键，非空 |
| user_id | UUID | 用户ID | 外键，非空 |
| rating | INTEGER | 评分 | 1-5分 |
| review | TEXT | 评价内容 | 可空 |
| pros_cons | JSON | 优缺点 | {"pros": [], "cons": []} |
| created_at | TIMESTAMP | 创建时间 | 自动生成 |
| updated_at | TIMESTAMP | 更新时间 | 自动更新 |

### 资讯相关表

#### news_sources (资讯源表)
存储资讯来源配置

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | UUID | 资讯源唯一标识 | 主键 |
| name | VARCHAR(100) | 资讯源名称 | 非空 |
| url | VARCHAR(500) | 资讯源URL | 非空 |
| selector | VARCHAR(200) | CSS选择器 | 可空 |
| keywords | JSON | 关键词列表 | 可空 |
| frequency_hours | INTEGER | 抓取频率(小时) | 默认24 |
| is_active | BOOLEAN | 是否启用 | 默认true |
| category | ENUM | 资讯分类 | 软件测试/游戏测试/AI测试/行业动态 |
| created_at | TIMESTAMP | 创建时间 | 自动生成 |
| updated_at | TIMESTAMP | 更新时间 | 自动更新 |

#### news_items (资讯条目表)
存储抓取的资讯内容

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | UUID | 资讯唯一标识 | 主键 |
| source_id | UUID | 资讯源ID | 外键，非空 |
| title | VARCHAR(300) | 资讯标题 | 非空 |
| url | VARCHAR(500) | 资讯链接 | 唯一，非空 |
| summary | TEXT | 资讯摘要 | 可空 |
| content | TEXT | 资讯内容 | 可空 |
| tags | JSON | 标签列表 | 可空 |
| rank_position | INTEGER | 排序位置 | 可空 |
| relevance_score | DECIMAL(5,2) | 相关性评分 | 默认0.0 |
| scraped_at | TIMESTAMP | 抓取时间 | 自动生成 |
| published_at | TIMESTAMP | 发布时间 | 可空 |
| created_at | TIMESTAMP | 创建时间 | 自动生成 |

## 索引设计

### 性能优化索引

```sql
-- 用户表索引
CREATE INDEX ix_users_username ON users(username);
CREATE INDEX ix_users_email ON users(email);

-- 文章表索引
CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_type ON articles(type);
CREATE INDEX idx_articles_created_at ON articles(created_at);
CREATE INDEX idx_articles_user_id ON articles(user_id);
CREATE INDEX idx_articles_category_id ON articles(category_id);

-- 工具表索引
CREATE INDEX idx_tools_category_id ON tools(category_id);
CREATE INDEX idx_tools_is_recommended ON tools(is_recommended);

-- 资讯表索引
CREATE INDEX idx_news_items_source_id ON news_items(source_id);
CREATE INDEX idx_news_items_published_at ON news_items(published_at);
CREATE INDEX idx_news_items_scraped_at ON news_items(scraped_at);

-- 评分表索引
CREATE INDEX idx_tool_ratings_tool_id ON tool_ratings(tool_id);
CREATE INDEX idx_tool_ratings_user_id ON tool_ratings(user_id);
```

## 数据库初始化

### 1. 运行迁移

```bash
# 在backend目录下执行
poetry run alembic upgrade head
```

### 2. 初始化数据

```bash
# 创建基础数据和管理员用户
python scripts/init_db.py

# 或者单独创建管理员用户
python scripts/create_admin.py
```

### 3. 测试环境设置

```bash
# 设置测试数据库
python scripts/setup_test_db.py setup

# 清理测试数据库
python scripts/setup_test_db.py cleanup
```

### 4. 验证数据库设计

```bash
# 验证表结构和约束
python scripts/validate_database_design.py
```

## 环境配置

### 开发环境
```env
DATABASE_URL=postgresql+asyncpg://qa_user:qa_password@localhost:5432/qa_platform_dev
```

### 测试环境
```env
DATABASE_URL=postgresql+asyncpg://qa_user:qa_password@localhost:5432/qa_platform_test
```

### 生产环境
```env
DATABASE_URL=postgresql+asyncpg://qa_user:qa_password@db:5432/qa_platform
```

## 数据迁移

### 创建新迁移

```bash
# 自动生成迁移文件
poetry run alembic revision --autogenerate -m "描述变更内容"

# 手动创建迁移文件
poetry run alembic revision -m "描述变更内容"
```

### 执行迁移

```bash
# 升级到最新版本
poetry run alembic upgrade head

# 升级到指定版本
poetry run alembic upgrade <revision_id>

# 降级到指定版本
poetry run alembic downgrade <revision_id>
```

### 查看迁移历史

```bash
# 查看当前版本
poetry run alembic current

# 查看迁移历史
poetry run alembic history

# 查看迁移详情
poetry run alembic show <revision_id>
```

## 备份与恢复

### 数据备份

```bash
# 备份整个数据库
pg_dump -h localhost -U qa_user -d qa_platform > backup.sql

# 备份特定表
pg_dump -h localhost -U qa_user -d qa_platform -t users -t articles > partial_backup.sql
```

### 数据恢复

```bash
# 恢复数据库
psql -h localhost -U qa_user -d qa_platform < backup.sql

# 恢复特定表
psql -h localhost -U qa_user -d qa_platform < partial_backup.sql
```

## 性能监控

### 查询性能分析

```sql
-- 查看慢查询
SELECT query, mean_time, calls, total_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- 查看表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 查看索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## 安全考虑

### 1. 数据加密
- 密码使用bcrypt哈希存储
- 敏感数据字段考虑加密存储
- 数据库连接使用SSL

### 2. 访问控制
- 数据库用户权限最小化
- 应用层实现细粒度权限控制
- 定期审计数据库访问日志

### 3. 数据完整性
- 外键约束保证引用完整性
- 检查约束验证数据有效性
- 定期备份和恢复测试

## 故障排除

### 常见问题

1. **连接超时**
   - 检查数据库服务状态
   - 验证连接字符串配置
   - 检查网络连通性

2. **迁移失败**
   - 检查数据库权限
   - 验证迁移文件语法
   - 查看详细错误日志

3. **性能问题**
   - 分析慢查询日志
   - 检查索引使用情况
   - 优化查询语句

4. **数据不一致**
   - 检查外键约束
   - 验证业务逻辑
   - 运行数据完整性检查

### 日志分析

```bash
# 查看PostgreSQL日志
tail -f /var/log/postgresql/postgresql-15-main.log

# 查看应用日志
tail -f logs/app.log
```

## 扩展计划

### V2.0 功能扩展

1. **项目管理表**
   - projects (项目表)
   - project_members (项目成员表)
   - project_permissions (项目权限表)

2. **学习路径表**
   - learning_paths (学习路径表)
   - learning_steps (学习步骤表)
   - learning_progress (学习进度表)

3. **协作功能表**
   - comments (评论表)
   - likes (点赞表)
   - notifications (通知表)
   - follows (关注表)

4. **分析统计表**
   - user_activities (用户活动表)
   - content_analytics (内容分析表)
   - system_metrics (系统指标表)

### 性能优化计划

1. **分区表设计**
   - 按时间分区articles表
   - 按类型分区news_items表

2. **读写分离**
   - 主从数据库配置
   - 读操作路由到从库

3. **缓存策略**
   - Redis缓存热点数据
   - 应用层缓存优化

4. **全文搜索**
   - PostgreSQL全文搜索优化
   - 考虑引入Elasticsearch