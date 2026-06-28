# 生产环境部署

本文说明如何将当前仓库部署为单机 Docker Compose 生产栈。生产部署由以下已提交文件支撑：

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker-compose.prod.yml`
- `.env.prod.example`

如果部署到托管云平台，可以沿用相同环境变量，并将内置 PostgreSQL、Redis 替换为托管服务。

## 前置条件

- Linux 服务器或虚拟机，安装 Docker Engine 与 Docker Compose V2。
- 能访问 Docker Hub、PyPI、npm registry、Google Fonts，或配置内部镜像源。
- 前端和 API 域名，例如 `qa.example.com` 与 `api.qa.example.com`。
- 通过反向代理或负载均衡器终止 TLS。
- 为 PostgreSQL、Redis、上传文件和日志准备持久化磁盘。
- 如启用邮件，需要可用 SMTP 账号。

## 1. 准备配置

```bash
cd qa-knowledge-platform
cp .env.prod.example .env.prod
```

编辑 `.env.prod` 并替换所有占位值：

- `FRONTEND_ORIGIN`：前端公网来源，例如 `https://qa.example.com`。
- `PUBLIC_API_URL`：后端 API 公网来源，例如 `https://api.qa.example.com`。
- `ALLOWED_HOSTS`：允许访问后端的浏览器来源 JSON 列表。
- `POSTGRES_PASSWORD`、`REDIS_PASSWORD`、`SECRET_KEY`：强随机值。
- `ENABLE_EMAIL_QUEUE=true` 时填写 SMTP 配置。

不要提交 `.env.prod`。

## 2. 校验 Compose 配置

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml config
```

该命令必须能输出最终配置，且没有缺失变量错误。

## 3. 构建镜像

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml build
```

前端镜像会在构建时写入 `NEXT_PUBLIC_API_URL`，因此公网 API 地址变化后必须重新构建前端镜像。

当前生产构建已在本地验证通过。若构建失败，优先检查外部网络访问和镜像源配置。

## 4. 启动数据库和缓存

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d db redis
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

等待 `db` 和 `redis` 状态变为 healthy。

## 5. 执行数据库迁移

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm backend \
  poetry run alembic upgrade head
```

应在承接流量前执行迁移。后端启动时仍会创建表以提升开发容错，但生产发布必须以 Alembic 为准。

## 6. 启动应用服务

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d backend celery-worker celery-beat frontend
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

通过反向代理暴露服务：

- 前端容器：`http://127.0.0.1:3000`
- 后端容器：`http://127.0.0.1:8000`

在代理层启用 HTTPS，并将请求转发到以上本地端口。

## 7. 验证部署

```bash
curl -f http://127.0.0.1:8000/health
curl -f http://127.0.0.1:3000
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail=100 backend
```

再验证公网地址：

```bash
curl -f https://api.qa.example.com/health
curl -f https://qa.example.com
```

## 8. 备份与恢复

创建 PostgreSQL 备份：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec db \
  sh -lc 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > backup.sql
```

需要备份的 Docker 卷：

- `prod_db_data`
- `prod_redis_data`
- `prod_uploads`
- `prod_logs`

正式依赖备份前，必须在非生产环境验证恢复流程。

## 9. 升级流程

```bash
git pull
docker compose --env-file .env.prod -f docker-compose.prod.yml build
docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm backend \
  poetry run alembic upgrade head
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

如果验证失败，回退到上一个 Git 提交并重新构建镜像。执行数据库迁移前必须保留备份。

## 构建故障排查

- 如果提示找不到 `docker-credential-desktop`，请确认 Docker Desktop 的 `resources/bin` 已加入 `PATH`，或重新打开终端。
- 如果拉取 `node:18-alpine`、`python:3.11-slim` 超时，请配置 Docker Hub 镜像源或重试网络。
- 如果访问 Debian、PyPI、npm registry 或 Google Fonts 超时，请使用稳定网络或内部代理/镜像源。
- 后端生产镜像不再安装 `gcc`、`g++`、`curl`，当前依赖均可通过 wheel 安装，避免不必要的 apt 网络依赖。
- 后端生产镜像固定 Poetry 2.2.1，以兼容当前 `pyproject.toml` 的 `[project]` 元数据格式。

## 生产说明

- 当前生产 Compose 文件适合单机部署。Kubernetes、ECS 等平台可按服务和环境变量等价转换。
- 高可用场景建议使用托管 PostgreSQL、托管 Redis 和对象存储。
- 本地上传文件持久化在 `prod_uploads` 卷中。多节点生产部署必须替换为对象存储实现。
