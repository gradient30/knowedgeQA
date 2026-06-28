# QA 知识协作平台

QA 知识协作平台是一个面向 SaaS 与游戏质量工程团队的全栈协作系统，覆盖知识文章、证据文件、测试工具治理、QA 资讯情报、通知、审计日志和管理员工作流。

本项目定位为大厂级互联网 QA 业务的工程化基线示例，不隶属于腾讯、网易或任何第三方公司。

## 当前状态

仓库已通过本地 Docker 验收基线，证据见 [`docs/plans/acceptance-matrix-saas-game-qa.md`](docs/plans/acceptance-matrix-saas-game-qa.md)：

- 后端回归：76 个测试，带覆盖率报告。
- 前端门禁：TypeScript 检查、ESLint、浏览器 UI 验收、真实浏览器 E2E 验收。
- 运行态验收：认证文件证据、通知治理、知识库、工具库、资讯、审计、确定性智能 API。
- 数据库：Alembic 迁移图保持单一发布头。
- 生产镜像：`docker-compose.prod.yml` 的前后端镜像已完成本地构建验证。

## 技术架构

- 前端：Next.js 14 App Router、TypeScript、Ant Design、Tailwind CSS、Zustand。
- 后端：FastAPI、SQLAlchemy 2、Alembic、PostgreSQL、Redis、Celery。
- 运行环境：Docker Compose 支持本地开发和单机生产部署。
- 质量门禁：pytest、覆盖率、`pnpm type-check`、`pnpm lint`、Playwright 验收脚本。

项目结构：

```text
qa-knowledge-platform/
├── frontend/                  # Next.js 前端应用
├── backend/                   # FastAPI 服务与 Alembic 迁移
├── scripts/                   # PowerShell 与 Bash 项目脚本
├── docs/                      # 架构、部署、运维、安全文档
├── docker-compose.dev.yml     # 本地开发栈
└── docker-compose.prod.yml    # 单机生产栈
```

## 快速开始

环境要求：

- Docker Desktop，启用 Docker Compose V2。
- Node.js 18+，用于本地验收脚本。
- Windows PowerShell 5+，或 WSL 2 Bash。

PowerShell：

```powershell
cd qa-knowledge-platform
.\scripts\project-manager.ps1 setup
.\scripts\project-manager.ps1 start -Env dev
.\scripts\project-manager.ps1 test
```

WSL 或 Bash：

```bash
cd qa-knowledge-platform
bash ./scripts/project-manager.sh setup
bash ./scripts/project-manager.sh start --env dev
bash ./scripts/project-manager.sh test
```

本地访问地址：

- 前端：<http://localhost:3000>
- 后端 API：<http://localhost:8000>
- Swagger UI：<http://localhost:8000/docs>
- 健康检查：<http://localhost:8000/health>

## 文档

- [开发环境部署](docs/deployment/dev.md)
- [生产环境部署](docs/deployment/prod.md)
- [系统架构](docs/architecture.md)
- [运维说明](docs/operations.md)
- [安全说明](docs/security.md)
- [技术路线图](docs/technical-roadmap.md)
- [贡献者指南](../AGENTS.md)

## 开发命令

```powershell
.\scripts\project-manager.ps1 status
.\scripts\project-manager.ps1 logs -Service backend -Follow
.\scripts\project-manager.ps1 stop
```

```bash
bash ./scripts/project-manager.sh status
bash ./scripts/project-manager.sh logs --service backend --follow
bash ./scripts/project-manager.sh stop
```

仅后端：

```bash
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
poetry run pytest tests/ --cov=app
```

仅前端：

```bash
cd frontend
pnpm install
pnpm dev
pnpm type-check
pnpm lint
pnpm build
```

## 生产部署

生产部署步骤见 [`docs/deployment/prod.md`](docs/deployment/prod.md)。当前仓库提供单机 Docker Compose 生产部署路径：

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker-compose.prod.yml`
- `.env.prod.example`

复制 `.env.prod.example` 为 `.env.prod`，替换所有密钥、域名和公网地址后，按生产部署文档执行。

## 贡献方式

提交信息遵循 Conventional Commits，例如：

```text
feat(knowledge): add article review workflow
fix(files): enforce private download ownership
docs(deployment): document production rollout
```

提交前应运行与变更相关的最小测试；涉及部署、共享 API、迁移、认证、文件访问或公共文档时，应运行完整项目门禁。

## 许可证

当前仓库尚未声明开源许可证。若需要作为可复用开源项目分发，请先补充 `LICENSE` 文件。
