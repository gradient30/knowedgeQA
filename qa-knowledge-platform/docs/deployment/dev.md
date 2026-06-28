# Development Deployment

This guide starts the local development stack for QA Knowledge Platform. It uses `docker-compose.dev.yml` and the committed project manager scripts.

## Prerequisites

- Docker Desktop with Docker Compose V2.
- Node.js 18+ on the host for acceptance scripts.
- PowerShell on Windows, or WSL 2 with Bash.
- Ports `3000`, `8000`, `5432`, and `6379` available.

The scripts can locate Docker Desktop from the standard user install path when `docker` is not on `PATH`.

## Start With PowerShell

```powershell
cd D:\workDir\githubwork\sblog\qa-knowledge-platform
.\scripts\project-manager.ps1 setup
.\scripts\project-manager.ps1 start -Env dev
.\scripts\project-manager.ps1 status
```

Open:

- Frontend: <http://localhost:3000>
- Backend API: <http://localhost:8000>
- API docs: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>

## Start With WSL

```bash
cd /mnt/d/workDir/githubwork/sblog/qa-knowledge-platform
bash ./scripts/project-manager.sh setup
bash ./scripts/project-manager.sh start --env dev
bash ./scripts/project-manager.sh status
```

Use forward slashes in WSL. Avoid commands such as `bash .\scripts\project-manager.sh`, because backslashes are not path separators in Bash.

## Run Verification

PowerShell:

```powershell
.\scripts\project-manager.ps1 test
```

WSL:

```bash
bash ./scripts/project-manager.sh test
```

The full gate runs backend tests, Alembic migration checks, frontend type-check, frontend lint, runtime acceptance, browser UI acceptance, real browser E2E acceptance, and documentation gates.

## Useful Commands

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

`clean` removes containers, volumes, and unused Docker resources. Use it only when local data can be discarded.

## Local Data and Configuration

The development stack uses:

- PostgreSQL database `qa_platform_dev`.
- PostgreSQL credentials `qa_user` / `qa_password`.
- Redis without password.
- Backend uploads under `backend/uploads/`.
- `.env.dev` as the local configuration template.

`setup` copies `.env.dev` to `.env` when `.env` does not exist.

## Troubleshooting

- If Docker was just installed, reopen PowerShell or WSL before running scripts.
- If ports are busy, stop the conflicting service or change the port mapping in `docker-compose.dev.yml`.
- If frontend UI acceptance fails after a production build, rerun `.\scripts\project-manager.ps1 test`; the script recreates the frontend dev server before browser checks.
- If WSL cannot find Node.js, install Node in WSL or ensure Windows Node is available from the standard install path.
