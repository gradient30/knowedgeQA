# QA Knowledge Platform

QA Knowledge Platform is a full-stack collaboration platform for quality engineering teams working across SaaS and game businesses. It provides knowledge articles, evidence files, tool governance, QA news intelligence, notifications, audit logs, and administrator workflows.

The project is built as a practical baseline for large internet-style QA operations. It is not affiliated with Tencent, NetEase, or any other company.

## Current Status

The repository has passed the local Docker acceptance baseline documented in [`docs/plans/acceptance-matrix-saas-game-qa.md`](docs/plans/acceptance-matrix-saas-game-qa.md):

- Backend regression: 76 tests with coverage reporting.
- Frontend gates: TypeScript check, ESLint, browser UI acceptance, and real browser E2E acceptance.
- Runtime acceptance: authenticated file evidence, notification governance, knowledge, tools, news, audit, and deterministic intelligence APIs.
- Database: Alembic migration graph has one release head.

## Architecture

- Frontend: Next.js 14 App Router, TypeScript, Ant Design, Tailwind CSS, Zustand.
- Backend: FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, Redis, Celery.
- Runtime: Docker Compose for local development and single-host production deployment.
- Quality gates: pytest, coverage, pnpm type-check, pnpm lint, Playwright acceptance scripts.

Project layout:

```text
qa-knowledge-platform/
├── frontend/                  # Next.js application
├── backend/                   # FastAPI service and Alembic migrations
├── scripts/                   # PowerShell and Bash project commands
├── docs/                      # Architecture, deployment, operations, security
├── docker-compose.dev.yml     # Local development stack
└── docker-compose.prod.yml    # Single-host production stack
```

## Quick Start

Requirements:

- Docker Desktop with Docker Compose V2
- Node.js 18+ for local script-based acceptance checks
- PowerShell 5+ on Windows, or WSL 2 with Bash

PowerShell:

```powershell
cd qa-knowledge-platform
.\scripts\project-manager.ps1 setup
.\scripts\project-manager.ps1 start -Env dev
.\scripts\project-manager.ps1 test
```

WSL or Bash:

```bash
cd qa-knowledge-platform
bash ./scripts/project-manager.sh setup
bash ./scripts/project-manager.sh start --env dev
bash ./scripts/project-manager.sh test
```

Local URLs:

- Frontend: <http://localhost:3000>
- Backend API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

## Documentation

- [Development deployment](docs/deployment/dev.md)
- [Production deployment](docs/deployment/prod.md)
- [Architecture](docs/architecture.md)
- [Operations](docs/operations.md)
- [Security](docs/security.md)
- [Technical roadmap](docs/technical-roadmap.md)
- [Contributor guide](../AGENTS.md)

## Development Commands

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

Backend-only:

```bash
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
poetry run pytest tests/ --cov=app
```

Frontend-only:

```bash
cd frontend
pnpm install
pnpm dev
pnpm type-check
pnpm lint
pnpm build
```

## Production Deployment

Production deployment is documented in [`docs/deployment/prod.md`](docs/deployment/prod.md). The committed production path is a single-host Docker Compose stack using:

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker-compose.prod.yml`
- `.env.prod.example`

Create a real `.env.prod` from the example, replace all secrets and public URLs, then run the documented commands.

## Contributing

Use Conventional Commits, for example:

```text
feat(knowledge): add article review workflow
fix(files): enforce private download ownership
docs(deployment): document production rollout
```

Before submitting changes, run the narrowest relevant tests and the full project gate when deployment, shared APIs, migrations, authentication, file access, or public documentation changes.

## License

No open-source license file is currently declared in this repository. Add a `LICENSE` file before distributing this project as reusable open-source software.
