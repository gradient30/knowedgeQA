# 公共仓库文档实施计划

> **给 Claude：** 必须使用 superpowers:executing-plans 按任务执行本计划。

**目标：** 为 QA 知识协作平台补齐适合 GitHub 公共仓库的 README、部署、架构、运维、安全和技术路线文档。

**架构：** 文档必须描述当前真实的 Next.js 前端、FastAPI 后端、PostgreSQL、Redis、Celery、Docker 和验收门禁。生产部署必须由仓库内已提交的部署文件支撑，不能引用不存在的 Compose 文件或未实现能力。

**技术栈：** Markdown、Docker Compose、Next.js 14、FastAPI、PostgreSQL 15、Redis 7、Celery、Poetry、pnpm。

---

### 任务 1：公共仓库 README

**文件：**
- 修改：`README.md`

**步骤：**
1. 用清晰的公共仓库说明替换旧 README。
2. 写明 PowerShell 与 WSL 的真实快速启动命令。
3. 链接部署、架构、安全、运维和路线图文档。
4. 不声明仓库中不存在的 staging 部署或许可证。

### 任务 2：可部署的开发与生产文件

**文件：**
- 创建：`frontend/Dockerfile`
- 创建：`backend/Dockerfile`
- 创建：`docker-compose.prod.yml`
- 创建：`.env.prod.example`

**步骤：**
1. 增加无热重载的生产 Dockerfile。
2. 增加单机生产 Compose 文件，显式使用环境变量。
3. 增加只含占位值的生产环境变量示例。
4. 使用 `docker compose --env-file .env.prod.example -f docker-compose.prod.yml config` 校验配置。
5. 使用 `docker compose --env-file .env.prod.example -f docker-compose.prod.yml build` 校验生产镜像构建。

### 任务 3：标准文档集

**文件：**
- 创建：`docs/deployment/dev.md`
- 创建：`docs/deployment/prod.md`
- 创建：`docs/architecture.md`
- 创建：`docs/operations.md`
- 创建：`docs/security.md`
- 创建：`docs/technical-roadmap.md`

**步骤：**
1. 基于现有 dev Compose 和脚本说明开发环境部署。
2. 基于生产 Dockerfile、Compose 和 env 示例说明生产部署。
3. 描述架构、模块边界、数据流、运维检查和安全基线。
4. 内容必须与当前验收矩阵和已知缺口一致。
5. 将相关 Markdown 文档统一汉化。

### 任务 4：验证与提交

**文件：**
- 验证全部文档和部署文件。

**步骤：**
1. 运行文档门禁：`node scripts/verify-acceptance-docs.js`。
2. 运行生产 Compose 配置校验。
3. 运行生产镜像构建。
4. 运行 `git diff --check`。
5. 暂存、提交并推送文档和部署修复。
