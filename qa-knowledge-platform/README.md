# QA测试知识协作平台

专为测试团队打造的知识分享与协作平台，提供测试经验分享、工具管理和行业资讯追踪三大核心功能。

## 🚀 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18+ (本地开发)
- Python 3.11+ (本地开发)

### 一键启动

```bash
# 克隆项目
git clone <repository-url>
cd qa-knowledge-platform

# 初始化项目环境
./scripts/project-manager.sh setup

# 启动开发环境
./scripts/project-manager.sh start

# 初始化数据库
./scripts/project-manager.sh init-db
```

### 访问地址

- 前端应用: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- 数据库: localhost:5432 (qa_user/qa_password)
- Redis: localhost:6379

## 📋 功能特性

### MVP版本 (V1.0)

- ✅ **用户认证系统**: 注册、登录、权限控制
- 🔄 **知识库管理**: 测试经验分享、分类管理、搜索功能
- 🔄 **测试工具库**: 工具推荐、评分、收藏
- 🔄 **行业资讯**: 自动抓取、分类展示
- ✅ **文件上传**: 图片、文档上传和管理
- ✅ **团队协作**: 三级权限控制、内容可见性

### 计划功能 (V2.0)

- 📋 高级协作功能 (评论、@提及、通知)
- 📋 学习路径与技能发展
- 📋 团队效能分析
- 📋 智能推荐系统
- 📋 移动端支持

## 🏗️ 技术架构

### 前端技术栈

- **框架**: Next.js 14 (App Router)
- **UI组件**: Ant Design 5.x + Tailwind CSS
- **状态管理**: Zustand
- **编辑器**: @uiw/react-md-editor
- **语言**: TypeScript 5.x

### 后端技术栈

- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0 + Alembic
- **缓存**: Redis 7+
- **任务队列**: Celery
- **认证**: FastAPI-Users + JWT

### 开发工具

- **容器化**: Docker + Docker Compose
- **代码质量**: ESLint, Prettier, Black, isort
- **测试**: Jest, pytest, Playwright
- **包管理**: pnpm, Poetry

## 📁 项目结构

```
qa-knowledge-platform/
├── frontend/                 # Next.js前端应用
│   ├── src/app/             # App Router页面
│   ├── src/components/      # 可复用组件
│   ├── src/lib/            # 工具函数和API客户端
│   └── src/types/          # TypeScript类型定义
├── backend/                 # FastAPI后端应用
│   ├── app/core/           # 核心配置和工具
│   ├── app/modules/        # 业务模块
│   ├── alembic/            # 数据库迁移
│   └── scripts/            # 工具脚本
├── scripts/                # 项目管理脚本
└── docker-compose.*.yml    # Docker编排文件
```

## 🛠️ 开发指南

### 本地开发

```bash
# 启动开发环境
./scripts/project-manager.sh start --env dev

# 查看服务状态
./scripts/project-manager.sh status

# 查看日志
./scripts/project-manager.sh logs --service backend --follow

# 运行测试
./scripts/project-manager.sh test

# 停止服务
./scripts/project-manager.sh stop
```

### 前端开发

```bash
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 代码检查
pnpm lint

# 运行测试
pnpm test
```

### 后端开发

```bash
cd backend

# 安装依赖
poetry install

# 启动开发服务器
poetry run uvicorn app.main:app --reload

# 数据库迁移
poetry run alembic upgrade head

# 运行测试
poetry run pytest tests/ --cov=app
```

## 🗄️ 数据库管理

### 创建迁移

```bash
cd backend
poetry run alembic revision --autogenerate -m "描述信息"
```

### 执行迁移

```bash
poetry run alembic upgrade head
```

### 初始化数据

```bash
poetry run python scripts/init_db.py
```

## 🧪 测试

### 运行所有测试

```bash
./scripts/project-manager.sh test
```

### 单独运行测试

```bash
# 后端测试
cd backend
poetry run pytest tests/ --cov=app --cov-report=html

# 前端测试
cd frontend
pnpm test --coverage

# E2E测试
pnpm test:e2e
```

## 📦 部署

### 开发环境

```bash
./scripts/project-manager.sh start --env dev
```

### 预发布环境

```bash
./scripts/project-manager.sh build --env staging
./scripts/project-manager.sh start --env staging
```

### 生产环境

```bash
./scripts/project-manager.sh build --env prod
./scripts/project-manager.sh start --env prod
```

## 🔧 配置说明

### 环境变量

主要配置文件: `.env.dev`, `.env.staging`, `.env.prod`

```bash
# 应用配置
APP_NAME=QA测试知识协作平台
DEBUG=true

# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db

# Redis配置
REDIS_URL=redis://host:port/db

# JWT配置
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 文件上传配置
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=[".jpg", ".png", ".pdf"]
```

## 👥 团队协作

### 代码规范

- 使用 ESLint + Prettier (前端)
- 使用 Black + isort (后端)
- 提交信息遵循 Conventional Commits

### 分支策略

- `main`: 生产环境分支
- `develop`: 开发环境分支
- `feature/*`: 功能开发分支
- `hotfix/*`: 紧急修复分支

### 代码审查

所有代码变更需要通过 Pull Request 并经过代码审查。

## 📊 监控和日志

### 查看日志

```bash
# 查看所有服务日志
./scripts/project-manager.sh logs

# 查看特定服务日志
./scripts/project-manager.sh logs --service backend --follow
```

### 健康检查

- 后端健康检查: http://localhost:8000/health
- 前端健康检查: http://localhost:3000/api/health

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如有问题或建议，请通过以下方式联系：

- 创建 Issue
- 发送邮件至: qa-team@company.com
- 项目文档: [链接]

## 🎯 路线图

### 2025 Q1 - MVP版本
- [x] 项目初始化和基础架构
- [x] 用户认证系统
- [ ] 知识库核心功能
- [ ] 工具库管理
- [ ] 资讯聚合系统

### 2025 Q2 - 完整版本
- [ ] 高级协作功能
- [ ] 学习路径系统
- [ ] 团队效能分析
- [ ] 智能推荐
- [ ] 移动端支持

---

**QA测试知识协作平台** - 让测试团队的知识流动起来 🚀