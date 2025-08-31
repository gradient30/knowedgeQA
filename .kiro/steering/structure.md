# 项目组织结构与开发规范

## QA测试知识协作平台 - 项目结构 (当前主项目)

### 标准目录结构 (严格遵循)
```
qa-knowledge-platform/
├── frontend/                    # Next.js 14 前端应用
│   ├── app/                    # App Router 页面 (Next.js 14)
│   │   ├── (auth)/            # 认证页面组 - 登录、注册、个人设置
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   └── profile/page.tsx
│   │   ├── knowledge/         # 知识库模块 - 核心功能
│   │   │   ├── articles/      # 文章管理
│   │   │   ├── categories/    # 分类管理
│   │   │   └── search/        # 搜索功能
│   │   ├── tools/             # 工具库模块
│   │   │   ├── categories/    # 工具分类
│   │   │   ├── reviews/       # 工具评价
│   │   │   └── favorites/     # 收藏管理
│   │   ├── news/              # 资讯模块
│   │   │   ├── feeds/         # 资讯订阅
│   │   │   └── sources/       # 信息源管理 (管理员)
│   │   ├── collaboration/     # 协作模块 (V2.0)
│   │   │   ├── teams/         # 团队管理
│   │   │   └── discussions/   # 讨论区
│   │   └── admin/             # 管理后台
│   │       ├── users/         # 用户管理
│   │       ├── permissions/   # 权限管理
│   │       └── system/        # 系统配置
│   ├── components/            # 可复用UI组件
│   │   ├── common/           # 通用组件
│   │   │   ├── Layout/       # 布局组件 (Header, Sidebar, Footer)
│   │   │   ├── Forms/        # 表单组件 (基于Ant Design)
│   │   │   └── UI/           # 基础UI组件
│   │   ├── qa/               # QA专用组件 (重要)
│   │   │   ├── TestCaseEditor/ # 测试用例编辑器
│   │   │   ├── BugReporter/   # Bug报告组件
│   │   │   ├── ToolRating/    # 工具评分组件
│   │   │   └── CategoryTree/  # 测试分类树
│   │   ├── knowledge/        # 知识模块组件
│   │   │   ├── ArticleEditor/ # Markdown文章编辑器
│   │   │   ├── ArticleList/   # 文章列表
│   │   │   └── SearchBox/     # 搜索组件
│   │   └── tools/            # 工具模块组件
│   │       ├── ToolGrid/     # 工具网格展示
│   │       └── ToolCard/     # 工具卡片
│   ├── lib/                  # 工具函数和客户端
│   │   ├── api/              # API客户端 (axios配置)
│   │   ├── hooks/            # 自定义React Hooks
│   │   ├── utils/            # 通用工具函数
│   │   └── qa-utils/         # QA专用工具函数
│   ├── types/                # TypeScript类型定义
│   │   ├── auth.types.ts     # 认证相关类型
│   │   ├── knowledge.types.ts # 知识库类型
│   │   ├── tools.types.ts    # 工具库类型
│   │   └── qa.types.ts       # QA专用类型
│   └── styles/               # 样式文件
│       ├── globals.css       # 全局样式
│       └── components.css    # 组件样式
├── backend/                   # FastAPI 后端应用
│   ├── app/
│   │   ├── core/             # 核心系统模块
│   │   │   ├── auth/         # 认证系统
│   │   │   │   ├── jwt.py    # JWT处理
│   │   │   │   ├── permissions.py # 权限控制
│   │   │   │   └── roles.py  # 角色管理
│   │   │   ├── database/     # 数据库配置
│   │   │   │   ├── connection.py
│   │   │   │   └── session.py
│   │   │   ├── config/       # 配置管理
│   │   │   │   ├── settings.py
│   │   │   │   └── environment.py
│   │   │   └── security/     # 安全模块
│   │   ├── modules/          # 业务模块 (按功能组织)
│   │   │   ├── users/        # 用户管理模块
│   │   │   │   ├── api/      # API路由
│   │   │   │   ├── models/   # SQLAlchemy数据模型
│   │   │   │   ├── services/ # 业务逻辑服务
│   │   │   │   └── schemas/  # Pydantic请求/响应模型
│   │   │   ├── knowledge/    # 知识管理模块 (核心)
│   │   │   │   ├── api/
│   │   │   │   ├── models/
│   │   │   │   ├── services/
│   │   │   │   ├── tasks/    # Celery异步任务
│   │   │   │   └── templates/ # 内容模板
│   │   │   ├── tools/        # 工具库模块
│   │   │   │   ├── api/
│   │   │   │   ├── models/
│   │   │   │   ├── services/
│   │   │   │   └── ratings/  # 评分系统
│   │   │   ├── news/         # 资讯模块
│   │   │   │   ├── api/
│   │   │   │   ├── models/
│   │   │   │   ├── services/
│   │   │   │   ├── tasks/    # 爬虫任务
│   │   │   │   └── crawlers/ # 爬虫实现
│   │   │   └── collaboration/ # 协作模块 (V2.0)
│   │   │       ├── api/
│   │   │       ├── models/
│   │   │       ├── services/
│   │   │       └── notifications/ # 通知系统
│   │   ├── shared/           # 共享组件
│   │   │   ├── schemas/      # 通用Pydantic模型
│   │   │   ├── utils/        # 工具函数
│   │   │   ├── exceptions/   # 异常定义
│   │   │   └── constants/    # 常量定义
│   │   └── main.py           # FastAPI应用入口
│   ├── alembic/              # 数据库迁移
│   │   ├── versions/         # 迁移版本文件
│   │   └── alembic.ini       # 迁移配置
│   ├── tests/                # 测试套件
│   │   ├── unit/            # 单元测试
│   │   ├── integration/     # 集成测试
│   │   ├── fixtures/        # 测试数据
│   │   └── conftest.py      # pytest配置
│   └── scripts/              # 部署和工具脚本
│       ├── init_db.py       # 数据库初始化
│       ├── create_admin.py  # 创建管理员用户
│       └── migrate_data.py  # 数据迁移工具
├── docs/                     # 项目文档
│   ├── api/                 # API文档 (自动生成)
│   ├── user-guide/          # 用户使用指南
│   ├── development/         # 开发文档
│   └── deployment/          # 部署文档
├── configs/                  # 配置文件
│   ├── docker/              # Docker配置
│   │   ├── Dockerfile.frontend
│   │   ├── Dockerfile.backend
│   │   └── nginx.conf
│   └── environments/        # 环境配置
│       ├── .env.dev
│       ├── .env.staging
│       └── .env.prod
├── scripts/                  # 项目管理脚本
│   ├── project-manager.sh   # 主管理脚本
│   ├── monitor.sh          # 监控脚本
│   └── backup.sh           # 备份脚本
├── docker-compose.dev.yml   # 开发环境
├── docker-compose.staging.yml # 预发布环境
├── docker-compose.prod.yml  # 生产环境
└── README.md                # 项目说明
```

### 核心模块职责划分

#### 前端模块职责
- **认证模块**: 用户注册、登录、个人资料管理
- **知识模块**: 文章CRUD、分类管理、搜索、Markdown编辑
- **工具模块**: 工具库展示、评分、收藏、分类筛选
- **资讯模块**: 资讯展示、收藏、分享、源管理(管理员)
- **管理模块**: 用户管理、权限控制、系统配置

#### 后端模块职责
- **用户模块**: 认证、权限、个人信息、团队管理
- **知识模块**: 文章管理、分类、标签、搜索、权限控制
- **工具模块**: 工具CRUD、评分系统、统计分析
- **资讯模块**: 爬虫调度、内容过滤、推送通知
- **协作模块**: 评论、点赞、通知、团队协作(V2.0)

### API路由结构 (RESTful设计)

```
/api/v1/
├── auth/                    # 认证相关
│   ├── register            # POST - 用户注册
│   ├── login               # POST - 用户登录
│   ├── logout              # POST - 用户登出
│   ├── verify-email        # POST - 邮箱验证
│   └── reset-password      # POST - 密码重置
├── users/                   # 用户管理
│   ├── profile             # GET/PUT - 个人资料
│   ├── avatar              # POST - 头像上传
│   └── export-data         # GET - 数据导出
├── knowledge/               # 知识库 (核心API)
│   ├── articles/           # 文章管理
│   │   ├── {id}           # GET/PUT/DELETE - 文章详情
│   │   ├── search         # GET - 文章搜索
│   │   └── categories     # GET - 按分类获取
│   ├── categories/         # 分类管理
│   │   ├── {id}           # GET/PUT/DELETE
│   │   └── tree           # GET - 分类树
│   └── tags/               # 标签管理
│       └── popular        # GET - 热门标签
├── tools/                   # 工具库
│   ├── {id}                # GET/PUT/DELETE - 工具详情
│   ├── categories          # GET - 工具分类
│   ├── ratings/{tool_id}   # POST - 工具评分
│   └── favorites           # GET/POST/DELETE - 收藏
├── news/                    # 资讯
│   ├── items               # GET - 资讯列表
│   ├── sources             # GET/POST - 信息源 (管理员)
│   └── favorites           # GET/POST/DELETE - 收藏
└── admin/                   # 管理功能
    ├── users               # GET/PUT/DELETE - 用户管理
    ├── permissions         # GET/PUT - 权限管理
    └── system/stats        # GET - 系统统计
```

## 文件命名规范 (严格执行)

### 前端文件命名 (Next.js + TypeScript)
- **页面文件**: `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`
- **组件文件**: `PascalCase.tsx` (如: `UserProfile.tsx`, `ArticleEditor.tsx`)
- **Hook文件**: `use + PascalCase.ts` (如: `useAuth.ts`, `useArticles.ts`)
- **工具函数**: `camelCase.ts` (如: `apiClient.ts`, `formatDate.ts`)
- **类型定义**: `PascalCase.types.ts` (如: `User.types.ts`)
- **样式文件**: `kebab-case.module.css` (如: `article-editor.module.css`)

### 后端文件命名 (FastAPI + Python)
- **模块目录**: `snake_case` (如: `user_management`, `knowledge_base`)
- **Python文件**: `snake_case.py` (如: `user_service.py`, `article_model.py`)
- **类名**: `PascalCase` (如: `UserService`, `ArticleModel`)
- **函数名**: `snake_case` (如: `get_user_by_id`, `create_article`)
- **常量**: `UPPER_SNAKE_CASE` (如: `MAX_FILE_SIZE`, `DEFAULT_PAGE_SIZE`)
- **测试文件**: `test_*.py` (如: `test_user_service.py`)

### 配置文件命名
- **环境配置**: `.env.{environment}` (如: `.env.dev`, `.env.prod`)
- **Docker配置**: `docker-compose.{env}.yml`
- **脚本文件**: `kebab-case.sh` (如: `project-manager.sh`)

## 代码组织原则 (核心规范)

### 关注点分离
- **前端**: 严格按照页面-组件-服务-工具的层次组织
- **后端**: API-服务-模型-数据库的分层架构
- **数据库**: 规范化设计，合理索引，支持全文搜索
- **配置**: 环境变量外部化，敏感信息加密

### 模块边界控制
- **单一职责**: 每个模块只负责一个业务领域
- **最小依赖**: 跨模块依赖通过明确接口
- **共享组件**: 放在shared/common目录
- **业务隔离**: 避免业务逻辑泄露到其他模块

### 测试结构组织
- **单元测试**: 与源码同目录或tests/unit/
- **集成测试**: tests/integration/，按模块组织
- **E2E测试**: tests/e2e/，按用户流程组织
- **测试数据**: tests/fixtures/，结构化测试数据

## QA测试领域特定规范

### 测试相关组件命名
- **测试用例**: `TestCase`, `TestSuite`, `TestExecution`
- **Bug报告**: `BugReport`, `BugCategory`, `BugSeverity`
- **工具评价**: `ToolRating`, `ToolReview`, `ToolUsage`
- **测试分类**: `TestCategory`, `TestType`, `TestLevel`

### 测试数据结构
- **测试步骤**: JSON格式存储，支持步骤化编辑
- **预期结果**: 结构化存储，支持多种验证方式
- **测试数据**: 支持参数化，环境隔离
- **执行记录**: 完整的执行历史，支持回溯分析

### 权限控制结构
- **角色层级**: Member < Admin < SuperAdmin
- **内容可见性**: Private < Team < Public
- **操作权限**: 基于角色和资源的细粒度控制
- **审核流程**: 内容发布前的审核机制

## 文档和注释规范

### 代码文档要求
- **公共API**: 必须有完整的JSDoc/docstring注释
- **复杂逻辑**: 关键算法和业务逻辑必须有注释
- **类型定义**: TypeScript接口必须有描述注释
- **配置文件**: 重要配置项必须有说明注释

### 项目文档结构
- **README.md**: 项目概述、快速开始、开发指南
- **API文档**: 自动生成的API文档 (FastAPI Swagger)
- **用户指南**: 面向最终用户的使用说明
- **开发文档**: 架构设计、开发规范、部署指南

### 变更记录管理
- **Git提交**: 使用Conventional Commits规范
- **版本管理**: 语义化版本控制 (SemVer)
- **变更日志**: CHANGELOG.md记录重要变更
- **架构决策**: ADR (Architecture Decision Records) 记录重要技术决策