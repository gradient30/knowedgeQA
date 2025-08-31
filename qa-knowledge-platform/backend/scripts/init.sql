-- QA测试知识协作平台数据库初始化脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建全文搜索配置 (中文支持)
CREATE TEXT SEARCH CONFIGURATION chinese (COPY = simple);

-- 设置数据库编码
SET client_encoding = 'UTF8';
SET timezone = 'Asia/Shanghai';

-- 创建基础表结构将由Alembic管理
-- 这里只做基础配置