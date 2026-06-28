# 开发环境部署

本文说明如何启动 QA 知识协作平台的本地开发栈。开发环境使用 `docker-compose.dev.yml` 和仓库内的项目管理脚本。

## 前置条件

- Docker Desktop，并启用 Docker Compose V2。
- Node.js 18+，用于运行验收脚本。
- Windows PowerShell，或 WSL 2 Bash。
- 本机端口 `3000`、`8000`、`5432`、`6379` 未被占用。

当 `docker` 未加入 `PATH` 时，项目脚本会尝试从 Docker Desktop 的标准安装路径定位 Docker。

## PowerShell 启动

```powershell
cd D:\workDir\githubwork\sblog\qa-knowledge-platform
.\scripts\project-manager.ps1 setup
.\scripts\project-manager.ps1 start -Env dev
.\scripts\project-manager.ps1 status
```

访问地址：

- 前端：<http://localhost:3000>
- 后端 API：<http://localhost:8000>
- API 文档：<http://localhost:8000/docs>
- 健康检查：<http://localhost:8000/health>

## WSL 启动

```bash
cd /mnt/d/workDir/githubwork/sblog/qa-knowledge-platform
bash ./scripts/project-manager.sh setup
bash ./scripts/project-manager.sh start --env dev
bash ./scripts/project-manager.sh status
```

在 WSL 中请使用正斜杠路径。不要使用 `bash .\scripts\project-manager.sh`，因为反斜杠不是 Bash 路径分隔符。

## 运行验收

PowerShell：

```powershell
.\scripts\project-manager.ps1 test
```

WSL：

```bash
bash ./scripts/project-manager.sh test
```

完整门禁会执行后端测试、Alembic 迁移检查、前端类型检查、前端 lint、运行态验收、浏览器 UI 验收、真实浏览器 E2E 验收和文档门禁。

## 常用命令

```powershell
.\scripts\project-manager.ps1 logs -Service backend -Follow
.\scripts\project-manager.ps1 restart -Env dev
.\scripts\project-manager.ps1 stop
.\scripts\project-manager.ps1 clean
```

```bash
bash ./scripts/project-manager.sh logs --service backend --follow
bash ./scripts/project-manager.sh restart --env dev
bash ./scripts/project-manager.sh stop
bash ./scripts/project-manager.sh clean
```

`clean` 会删除容器、卷和未使用的 Docker 资源。只有在可以丢弃本地数据时才使用。

## 本地数据与配置

开发栈使用：

- PostgreSQL 数据库：`qa_platform_dev`。
- PostgreSQL 账号：`qa_user` / `qa_password`。
- Redis：无密码。
- 后端上传目录：`backend/uploads/`。
- 本地配置模板：`.env.dev`。

`setup` 会在 `.env` 不存在时从 `.env.dev` 复制一份。

## 故障排查

- Docker 刚安装完成后，请重新打开 PowerShell 或 WSL。
- 如果端口被占用，请停止冲突服务，或调整 `docker-compose.dev.yml` 的端口映射。
- 如果生产构建后 UI 验收失败，重新运行 `.\scripts\project-manager.ps1 test`；脚本会在浏览器检查前重建前端 dev server。
- 如果 WSL 找不到 Node.js，请在 WSL 内安装 Node，或确保 Windows Node 位于标准安装路径。
