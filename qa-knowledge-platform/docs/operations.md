# 运维说明

本文定义当前项目的日常检查、发布和回滚操作。

## 健康检查

后端：

```bash
curl -f http://localhost:8000/health
curl -f http://localhost:8000/health/detailed
```

前端：

```bash
curl -f http://localhost:3000
```

Docker：

```bash
docker compose -f docker-compose.dev.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

`/health/detailed` 会检查 PostgreSQL、Redis、Celery 可见性和主机系统信息。

## 日志

开发环境：

```powershell
.\scripts\project-manager.ps1 logs -Service backend -Follow
```

```bash
bash ./scripts/project-manager.sh logs --service backend --follow
```

生产环境：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail=200 backend
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f celery-worker
```

## 发布检查清单

合并或部署共享行为前执行：

```powershell
.\scripts\project-manager.ps1 test
```

或：

```bash
bash ./scripts/project-manager.sh test
```

生产发布步骤：

1. 确认 `git status --short` 为空。
2. 构建生产镜像。
3. 备份 PostgreSQL 和上传文件。
4. 执行 Alembic 迁移。
5. 启动服务。
6. 验证 `/health`、前端页面、日志和关键认证流程。

## 数据库操作

查看当前迁移头：

```bash
docker compose -f docker-compose.dev.yml exec backend poetry run alembic heads
```

执行迁移：

```bash
docker compose -f docker-compose.dev.yml exec backend poetry run alembic upgrade head
```

生产环境：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm backend \
  poetry run alembic upgrade head
```

## 备份对象

生产环境需要备份：

- PostgreSQL 数据库。
- `prod_uploads` 卷。
- 安全保存的 `.env.prod`。
- 反向代理 TLS 配置。
- 存储在 Git 外部的 SMTP 和外部服务凭据。

## 回滚

应用回滚：

1. 切回上一个 Git 提交。
2. 重新构建镜像。
3. 使用 `docker compose up -d` 重启服务。
4. 验证健康检查和日志。

数据库回滚取决于具体迁移。没有经过测试的回滚方案和最新备份时，不要降级生产数据库。

## 故障处理

同时使用审计日志和应用日志定位问题：

- API 与中间件日志用于定位请求失败。
- 审计日志用于定位知识库、资讯、工具和管理操作变更。
- 通知日志用于定位邮件模板和发送尝试。

涉及认证、私有文件、管理员治理或迁移的问题应优先升级处理。
