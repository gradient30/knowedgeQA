# SaaS/Game Baseline Acceptance Matrix

This matrix defines the release evidence for the SaaS and game QA baseline. It maps product requirements to implementation surfaces, tests, and owners so QA managers can verify the platform with repeatable evidence.

| Level | Requirement | Modules and routes | Frontend evidence | Automated evidence | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | Business domain taxonomy supports SaaS, game, and common QA assets. | Models: knowledge, tools, news. Seed: `scripts/init_db.py`. | Domain filters on `/knowledge`, `/tools`, `/news`. | `python -m pytest tests/test_taxonomy.py -q` | Tech lead | Passed |
| P0 | Knowledge workflow replaces placeholders with article CRUD and search. | `GET /api/v1/knowledge/articles`, `POST /api/v1/knowledge/articles`, `GET /api/v1/knowledge/search`, `GET /api/v1/knowledge/categories`. | SaaS incident review and game release report rows visible on `/knowledge`. | `python -m pytest tests/test_knowledge_api.py -q` | Backend + QA | Passed |
| P0 | Tool operations support domain filtering, rating, favorite, and usage tracking. | `GET /api/v1/tools`, `POST /api/v1/tools`, `POST /api/v1/tools/{id}/rating`, `POST /api/v1/tools/{id}/favorite`, `POST /api/v1/tools/{id}/usage`. | API contract, automation, FPS, and weak-network tools visible on `/tools`. | `python -m pytest tests/test_tools_api.py -q` | Backend + QA | Passed |
| P1 | QA intelligence news supports source governance and publish/reject review. | `GET /api/v1/news/items`, `POST /api/v1/news/items/{id}/publish`, `POST /api/v1/news/items/{id}/reject`, `/api/v1/news/sources`. | DORA, AI testing, and game testing intelligence visible on `/news`. | `python -m pytest tests/test_news_api.py -q` | Content ops | Passed |
| P1 | Frontend pages are operational workspaces, not "under development" placeholders. | Typed clients in `frontend/src/lib/api/*`. | Tables, filters, metrics, status tags, and create actions on `/knowledge`, `/tools`, `/news`. | `node scripts/verify-core-pages.js`, `pnpm type-check`, `pnpm lint`, `pnpm build` | Frontend + QA | Passed |
| P2 | Collaboration and governance support files, comments, likes, favorites, notifications, auth, profile, audit logs, real metrics, and administrator user governance. | File upload, `POST /api/v1/knowledge/articles/{id}/comments`, `POST /api/v1/knowledge/articles/{id}/like`, `POST /api/v1/knowledge/articles/{id}/favorite`, `GET /api/v1/knowledge/metrics`, `GET /api/v1/users/stats`, `GET /api/v1/teams/{id}/stats`, `GET /api/v1/audit/logs`, notification admin, auth/profile routes, `GET /api/v1/users/`, `GET /api/v1/users/{id}`, `PUT /api/v1/users/{id}/role`, `PUT /api/v1/users/{id}/status`. | `/files`, `/admin/notifications`, `/profile`, `/login` build successfully; runtime gate verifies comment, like, favorite, metrics, and audit flow. | `python -m pytest tests/test_users.py tests/test_audit_api.py tests/test_no_placeholder_api.py -q`, `node scripts/verify-runtime-acceptance.js`, `pnpm build` | Full stack | Passed |
| P3 | Intelligent QA features only use reviewed content and source links. | `GET /api/v1/intelligence/similar-articles`, `GET /api/v1/intelligence/tool-recommendations`, `GET /api/v1/intelligence/news-summary`. | Source-backed similar articles, recommended tools, and news summaries are exposed through API contracts. | `python -m pytest tests/test_intelligence_api.py -q`, `node scripts/verify-runtime-acceptance.js` | Product + QA | Passed as deterministic MVP |

## Release Evidence

- Backend focused suite: `python -m pytest tests/test_taxonomy.py tests/test_knowledge_api.py tests/test_tools_api.py tests/test_news_api.py tests/test_intelligence_api.py -q` -> 17 passed.
- Backend full regression: `python -m pytest tests/ --cov=app -q` -> 66 passed, 71% coverage, warning-free.
- Database migration graph: `poetry run alembic heads` -> single Alembic release head `20260628_add_audit_logs`; fresh empty database upgrade with `DATABASE_URL=postgresql+asyncpg://... poetry run alembic upgrade head` -> passed.
- Frontend static gate: `node scripts/verify-core-pages.js` -> passed.
- Frontend quality gate: `pnpm type-check`, `pnpm lint`, `pnpm build` -> passed with zero ESLint warnings.
- Runtime Docker acceptance: `node scripts/verify-runtime-acceptance.js` -> validates backend health, SaaS/Game seed data, file upload, knowledge write flow with linked evidence file, comment, like, favorite, metrics, audit flow, tool rating/favorite/usage flow, news source governance, source-backed intelligence flow, source-backed news summary, and frontend routes on the integrated stack.
- UI acceptance: `npx --yes --package playwright node scripts/verify-ui-acceptance.js` -> validates `/knowledge`, `/tools`, and `/news` render live API data, filter by SaaS/Game, and open create/configuration forms in a browser.
- UI screenshot evidence: `output/acceptance/ui-knowledge.png`, `output/acceptance/ui-tools.png`, `output/acceptance/ui-news.png`.
- Project manager script resilience: `node scripts/verify-project-manager-scripts.js` -> verifies PowerShell and WSL test entrypoints restore the frontend dev server before UI acceptance, preventing production `.next` cleanup from corrupting browser checks.
- Placeholder API gate: `python -m pytest tests/test_no_placeholder_api.py -q` -> verifies backend API modules no longer expose "开发中" placeholder responses.
- Documentation gate: `node scripts/verify-acceptance-docs.js` must pass before release handoff.

## Manual Walkthrough

Use a local dev stack with backend on `8000` and frontend on `3000`.

1. Create a SaaS API compatibility or incident review article and verify `business_domain=saas`.
2. Create a game version quality report and verify `business_domain=game`.
3. Rate or favorite a game performance tool from `/tools`.
4. Publish a QA trend item from the news review workflow.
5. Search and filter knowledge, tools, and news by business domain and tag.
6. Confirm admin review, file upload, notification settings, audit flow, profile flows, and user/team stats still build and route.

## Known Gaps

- Docker Desktop is required locally. The PowerShell and WSL scripts support the user-level Docker install path when Docker is not on `PATH`.
- P3 is implemented as a deterministic, source-backed MVP. External LLM/Agent answers remain out of V1.0 scope until reviewed production datasets and evaluation metrics are approved.

## Final Integration Gate

| Check | Command | Result |
| --- | --- | --- |
| Docker stack status | `.\scripts\project-manager.ps1 status` | Passed: frontend, backend, PostgreSQL, Redis, Celery worker, and Celery beat are running. |
| WSL script compatibility | `wsl bash ./scripts/project-manager.sh test` | Passed using Windows Docker and Node fallbacks. |
| Full stack startup | `.\scripts\project-manager.ps1 start -Env dev` | Passed: dev stack starts and initializes. |
| Runtime Docker acceptance | `node scripts/verify-runtime-acceptance.js` | Passed: health, SaaS/Game APIs, file upload, knowledge create with evidence file/approve/comment/like/favorite/metrics/update/search/delete, audit flow for knowledge/news/source changes, tool create/delete/rate/favorite/usage, news source CRUD, news publish/reject, intelligence flow, and core frontend routes. |
| UI acceptance | `npx --yes --package playwright node scripts/verify-ui-acceptance.js` | Passed: live API data rendered, SaaS/Game filters worked, and create/configuration forms opened on knowledge, tools, and news pages. |
| Project manager script resilience | `node scripts/verify-project-manager-scripts.js` | Passed: PowerShell and WSL test entrypoints restore the frontend dev server before browser UI acceptance. |
| Backend focused regression | `python -m pytest tests/test_taxonomy.py tests/test_knowledge_api.py tests/test_tools_api.py tests/test_news_api.py tests/test_intelligence_api.py -q` | Passed: 17 tests. |
| Backend full regression | `python -m pytest tests/ --cov=app -q` | Passed: 66 tests, 71% coverage, warning-free. |
| Database migration graph | `poetry run alembic heads`; run `poetry run alembic upgrade head` against a fresh empty database. | Passed: single Alembic release head `20260628_add_audit_logs`; fresh empty database upgrade passed. |
| Frontend release build | Stop `frontend`, run `$docker compose -f docker-compose.dev.yml run --rm --no-deps -e NODE_ENV=production -e NEXT_TELEMETRY_DISABLED=1 frontend sh -lc "rm -rf .next && pnpm build"`, then start `frontend`. | Passed: 17 static routes generated without `.next` contention. |
| Documentation gate | `node scripts/verify-acceptance-docs.js` | Passed. |
