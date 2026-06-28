# SaaS/Game Baseline Acceptance Matrix

This matrix defines the release evidence for the SaaS and game QA baseline. It maps product requirements to implementation surfaces, tests, and owners so QA managers can verify the platform with repeatable evidence.

| Level | Requirement | Modules and routes | Frontend evidence | Automated evidence | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | Business domain taxonomy supports SaaS, game, and common QA assets. | Models: knowledge, tools, news. Seed: `scripts/init_db.py`. | Domain filters on `/knowledge`, `/tools`, `/news`. | `python -m pytest tests/test_taxonomy.py -q` | Tech lead | Passed |
| P0 | Knowledge workflow replaces placeholders with article CRUD and search. | `GET /api/v1/knowledge/articles`, `POST /api/v1/knowledge/articles`, `GET /api/v1/knowledge/search`, `GET /api/v1/knowledge/categories`. | SaaS incident review and game release report rows visible on `/knowledge`. | `python -m pytest tests/test_knowledge_api.py -q` | Backend + QA | Passed |
| P0 | Tool operations support domain filtering, rating, favorite, and usage tracking. | `GET /api/v1/tools`, `POST /api/v1/tools`, `POST /api/v1/tools/{id}/rating`, `POST /api/v1/tools/{id}/favorite`, `POST /api/v1/tools/{id}/usage`. | API contract, automation, FPS, and weak-network tools visible on `/tools`. | `python -m pytest tests/test_tools_api.py -q` | Backend + QA | Passed |
| P1 | QA intelligence news supports source governance and publish/reject review. | `GET /api/v1/news/items`, `POST /api/v1/news/items/{id}/publish`, `POST /api/v1/news/items/{id}/reject`, `/api/v1/news/sources`. | DORA, AI testing, and game testing intelligence visible on `/news`. | `python -m pytest tests/test_news_api.py -q` | Content ops | Passed |
| P1 | Frontend pages are operational workspaces, not "under development" placeholders. | Typed clients in `frontend/src/lib/api/*`. | Tables, filters, metrics, status tags, and create actions on `/knowledge`, `/tools`, `/news`. | `node scripts/verify-core-pages.js`, `pnpm type-check`, `pnpm lint`, `pnpm build` | Frontend + QA | Passed |
| P2 | Collaboration and governance remain compatible with files, notifications, auth, and profile flows. | File upload, notification admin, auth store/API, profile route. | `/files`, `/admin/notifications`, `/profile`, `/login` build successfully. | `pnpm build` | Full stack | Passed with warnings |
| P3 | Intelligent QA features are gated until reviewed content and metrics are available. | Future: reviewed knowledge graph, similar issue retrieval, tool recommendations, news summarization. | Matrix requires source-backed answers and citations before release. | Not in MVP automated gate | Product + QA | Deferred |

## Release Evidence

- Backend focused suite: `python -m pytest tests/test_taxonomy.py tests/test_knowledge_api.py tests/test_tools_api.py tests/test_news_api.py -q` -> 13 passed.
- Backend full regression: `python -m pytest tests/ --cov=app -q` -> 52 passed, 68% coverage.
- Frontend static gate: `node scripts/verify-core-pages.js` -> passed.
- Frontend quality gate: `pnpm type-check`, `pnpm lint`, `pnpm build` -> passed. Lint still reports non-blocking existing `any` and hook dependency warnings.
- Runtime Docker acceptance: `node scripts/verify-runtime-acceptance.js` -> validates backend health, SaaS/Game seed data, file upload, and frontend routes on the integrated stack.
- Documentation gate: `node scripts/verify-acceptance-docs.js` must pass before release handoff.

## Manual Walkthrough

Use a local dev stack with backend on `8000` and frontend on `3000`.

1. Create a SaaS API compatibility or incident review article and verify `business_domain=saas`.
2. Create a game version quality report and verify `business_domain=game`.
3. Rate or favorite a game performance tool from `/tools`.
4. Publish a QA trend item from the news review workflow.
5. Search and filter knowledge, tools, and news by business domain and tag.
6. Confirm admin review, file upload, notification settings, and profile flows still build and route.

## Known Gaps

- Docker Desktop is required locally. The PowerShell and WSL scripts support the user-level Docker install path when Docker is not on `PATH`.
- End-to-end browser screenshots are not attached to this matrix; use `node scripts/verify-runtime-acceptance.js` as the repeatable HTTP smoke gate for release handoff.
- P3 intelligent recommendations require reviewed production content and evaluation datasets before release.

## Final Integration Gate

| Check | Command | Result |
| --- | --- | --- |
| Docker stack status | `.\scripts\project-manager.ps1 status` | Passed: frontend, backend, PostgreSQL, Redis, Celery worker, and Celery beat are running. |
| WSL script compatibility | `bash ./scripts/project-manager.sh status` | Passed using the Windows Docker CLI fallback. |
| Full stack startup | `.\scripts\project-manager.ps1 start -Env dev` | Passed: dev stack starts and initializes. |
| Runtime Docker acceptance | `node scripts/verify-runtime-acceptance.js` | Passed: health, SaaS/Game APIs, file upload, and core frontend routes. |
| Backend focused regression | `python -m pytest tests/test_taxonomy.py tests/test_knowledge_api.py tests/test_tools_api.py tests/test_news_api.py -q` | Passed: 13 tests. |
| Backend full regression | `python -m pytest tests/ --cov=app -q` | Passed: 52 tests, 68% coverage. |
| Frontend release build | `$docker = Join-Path $env:LOCALAPPDATA 'Programs\DockerDesktop\resources\bin\docker.exe'; & $docker compose -f docker-compose.dev.yml run --rm --no-deps -e NODE_ENV=production frontend pnpm build` | Passed: 17 static routes generated. |
| Documentation gate | `node scripts/verify-acceptance-docs.js` | Passed. |
