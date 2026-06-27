# SaaS Game QA Platform Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the approved Tencent/NetEase-style SaaS and game QA platform baseline across knowledge, tools, news, collaboration, governance, and staged acceptance.

**Architecture:** Keep the current Next.js 14 + FastAPI + PostgreSQL architecture. Extend existing domain modules instead of introducing new services; add business-domain fields, status workflows, APIs, UI pages, tests, and seed data in small vertical slices.

**Tech Stack:** FastAPI, SQLAlchemy 2.0 async, Alembic, PostgreSQL, pytest, Next.js 14 App Router, TypeScript, Ant Design, Zustand, pnpm.

---

### Task 1: Product Taxonomy And Seed Data

**Files:**
- Modify: `qa-knowledge-platform/backend/app/modules/knowledge/models.py`
- Modify: `qa-knowledge-platform/backend/app/modules/tools/models.py`
- Modify: `qa-knowledge-platform/backend/app/modules/news/models.py`
- Modify: `qa-knowledge-platform/backend/scripts/init_db.py`
- Test: `qa-knowledge-platform/backend/tests/test_taxonomy.py`

**Step 1: Write the failing test**

Create tests that assert the platform supports `saas` and `game` business domains, content lifecycle states, and seeded SaaS/game categories.

```python
def test_business_domain_values_exist():
    from app.modules.knowledge.models import BusinessDomain
    assert BusinessDomain.SAAS.value == "saas"
    assert BusinessDomain.GAME.value == "game"
```

**Step 2: Run test to verify it fails**

Run: `cd qa-knowledge-platform/backend && poetry run pytest tests/test_taxonomy.py -v`
Expected: FAIL because `BusinessDomain` does not exist.

**Step 3: Implement minimal model additions**

Add shared enum values to each affected module:

```python
class BusinessDomain(str, enum.Enum):
    SAAS = "saas"
    GAME = "game"
    COMMON = "common"
```

Add `business_domain`, `project_key`, `review_status`, and `visibility` where relevant. Keep existing names backward-compatible.

**Step 4: Seed canonical categories**

Seed SaaS categories such as API compatibility, SLA, gray release, incident review. Seed game categories such as device compatibility, FPS performance, weak network, gameplay, LQA, version submission.

**Step 5: Run tests**

Run: `cd qa-knowledge-platform/backend && poetry run pytest tests/test_taxonomy.py -v`
Expected: PASS.

**Step 6: Commit**

```bash
git add qa-knowledge-platform/backend/app/modules/*/models.py qa-knowledge-platform/backend/scripts/init_db.py qa-knowledge-platform/backend/tests/test_taxonomy.py
git commit -m "feat(platform): add saas and game qa taxonomy"
```

### Task 2: Knowledge API Vertical Slice

**Files:**
- Modify: `qa-knowledge-platform/backend/app/modules/knowledge/api.py`
- Create: `qa-knowledge-platform/backend/app/modules/knowledge/schemas.py`
- Create: `qa-knowledge-platform/backend/app/modules/knowledge/services.py`
- Test: `qa-knowledge-platform/backend/tests/test_knowledge_api.py`

**Step 1: Write failing API tests**

Cover article list, detail, create, update, delete, search, domain filter, and review status filter.

**Step 2: Run failing tests**

Run: `cd qa-knowledge-platform/backend && poetry run pytest tests/test_knowledge_api.py -v`
Expected: FAIL because current routes return "开发中".

**Step 3: Implement schemas and service**

Define request/response schemas for title, summary, content, type, category, tags, business_domain, visibility, review_status, and attachments.

**Step 4: Replace placeholder routes**

Implement:
- `GET /api/v1/knowledge/articles`
- `POST /api/v1/knowledge/articles`
- `GET /api/v1/knowledge/articles/{id}`
- `PUT /api/v1/knowledge/articles/{id}`
- `DELETE /api/v1/knowledge/articles/{id}`
- `GET /api/v1/knowledge/search`
- `GET /api/v1/knowledge/categories`

**Step 5: Run tests**

Run: `cd qa-knowledge-platform/backend && poetry run pytest tests/test_knowledge_api.py -v`
Expected: PASS.

**Step 6: Commit**

```bash
git add qa-knowledge-platform/backend/app/modules/knowledge qa-knowledge-platform/backend/tests/test_knowledge_api.py
git commit -m "feat(knowledge): implement qa article workflow"
```

### Task 3: Tools API Vertical Slice

**Files:**
- Modify: `qa-knowledge-platform/backend/app/modules/tools/api.py`
- Create: `qa-knowledge-platform/backend/app/modules/tools/schemas.py`
- Create: `qa-knowledge-platform/backend/app/modules/tools/services.py`
- Test: `qa-knowledge-platform/backend/tests/test_tools_api.py`

**Step 1: Write failing tests**

Test CRUD, category filter, business-domain filter, rating, pros/cons, favorites, recommended tools, and usage count.

**Step 2: Run failing tests**

Run: `cd qa-knowledge-platform/backend && poetry run pytest tests/test_tools_api.py -v`
Expected: FAIL because current routes return placeholders.

**Step 3: Implement tool schemas and services**

Support SaaS tools, game tools, shared tools, scoring, recommendations, and usage metrics.

**Step 4: Implement routes**

Implement `GET/POST/PUT/DELETE /api/v1/tools`, `GET /api/v1/tools/categories`, `POST /api/v1/tools/{id}/rating`, `POST /api/v1/tools/{id}/favorite`, and `POST /api/v1/tools/{id}/usage`.

**Step 5: Run tests**

Run: `cd qa-knowledge-platform/backend && poetry run pytest tests/test_tools_api.py -v`
Expected: PASS.

**Step 6: Commit**

```bash
git add qa-knowledge-platform/backend/app/modules/tools qa-knowledge-platform/backend/tests/test_tools_api.py
git commit -m "feat(tools): implement qa tool operations"
```

### Task 4: News API And Review Workflow

**Files:**
- Modify: `qa-knowledge-platform/backend/app/modules/news/api.py`
- Modify: `qa-knowledge-platform/backend/app/modules/news/tasks.py`
- Create: `qa-knowledge-platform/backend/app/modules/news/schemas.py`
- Create: `qa-knowledge-platform/backend/app/modules/news/services.py`
- Test: `qa-knowledge-platform/backend/tests/test_news_api.py`

**Step 1: Write failing tests**

Cover source CRUD, active/inactive state, keyword filtering, domain tagging, deduplication by URL, relevance score, and manual publish/reject.

**Step 2: Run failing tests**

Run: `cd qa-knowledge-platform/backend && poetry run pytest tests/test_news_api.py -v`
Expected: FAIL because current routes are placeholders.

**Step 3: Implement source and item services**

Keep crawler logic minimal for MVP; make fetch/import testable with mocked HTML.

**Step 4: Implement routes**

Implement `GET /items`, `POST /items/{id}/publish`, `POST /items/{id}/reject`, `GET/POST/PUT/DELETE /sources`.

**Step 5: Run tests**

Run: `cd qa-knowledge-platform/backend && poetry run pytest tests/test_news_api.py -v`
Expected: PASS.

**Step 6: Commit**

```bash
git add qa-knowledge-platform/backend/app/modules/news qa-knowledge-platform/backend/tests/test_news_api.py
git commit -m "feat(news): implement qa intelligence workflow"
```

### Task 5: Frontend Core Pages

**Files:**
- Modify: `qa-knowledge-platform/frontend/src/app/knowledge/page.tsx`
- Modify: `qa-knowledge-platform/frontend/src/app/tools/page.tsx`
- Modify: `qa-knowledge-platform/frontend/src/app/news/page.tsx`
- Create: `qa-knowledge-platform/frontend/src/lib/api/knowledge.ts`
- Create: `qa-knowledge-platform/frontend/src/lib/api/tools.ts`
- Create: `qa-knowledge-platform/frontend/src/lib/api/news.ts`
- Create: `qa-knowledge-platform/frontend/src/types/platform.types.ts`

**Step 1: Add failing UI checks**

Use Playwright or component tests to assert each page shows domain filters, real tables/cards, create actions, and no "开发中" placeholder.

**Step 2: Run failing checks**

Run: `cd qa-knowledge-platform/frontend && pnpm lint && pnpm type-check`
Expected: type-check may fail until API types exist.

**Step 3: Build API clients and types**

Add typed clients for knowledge, tools, and news using the existing axios client.

**Step 4: Replace placeholder pages**

Use Ant Design tables, filters, tags, drawers/forms, and status badges. Keep screens dense and operational, not marketing-style.

**Step 5: Run verification**

Run: `cd qa-knowledge-platform/frontend && pnpm lint && pnpm type-check && pnpm build`
Expected: PASS.

**Step 6: Commit**

```bash
git add qa-knowledge-platform/frontend/src
git commit -m "feat(frontend): add saas and game qa workspaces"
```

### Task 6: Governance And Acceptance Evidence

**Files:**
- Create: `qa-knowledge-platform/docs/plans/acceptance-matrix-saas-game-qa.md`
- Modify: `qa-knowledge-platform/P1-verification-checklist.md`
- Modify: `qa-knowledge-platform/P2-verification-checklist.md`
- Modify: `qa-knowledge-platform/P3-verification-checklist.md`

**Step 1: Write the acceptance matrix**

Map P0-P3 requirements to modules, API routes, frontend pages, tests, owner, and evidence.

**Step 2: Update verification checklists**

Add SaaS/game examples: API compatibility article, game version report, tool rating, source review, comment, favorite, admin review.

**Step 3: Run full backend tests**

Run: `cd qa-knowledge-platform/backend && poetry run pytest tests/ --cov=app`
Expected: PASS and coverage meets project threshold or explicitly documented gap.

**Step 4: Run full frontend checks**

Run: `cd qa-knowledge-platform/frontend && pnpm lint && pnpm type-check && pnpm build`
Expected: PASS.

**Step 5: Commit**

```bash
git add qa-knowledge-platform/docs/plans qa-knowledge-platform/P*-verification-checklist.md
git commit -m "docs(qa): add saas game acceptance matrix"
```

### Task 7: Final Integration Gate

**Files:**
- Modify as needed based on defects discovered in previous tasks.

**Step 1: Start full stack**

Run: `cd qa-knowledge-platform && ./scripts/project-manager.sh start --env dev`
Expected: frontend on `3000`, backend on `8000`, PostgreSQL on `5432`, Redis on `6379`.

**Step 2: Initialize data**

Run: `cd qa-knowledge-platform && ./scripts/project-manager.sh init-db`
Expected: SaaS/game categories and sample content are present.

**Step 3: Execute acceptance walkthrough**

Verify:
- Create SaaS incident review article.
- Create game version quality report.
- Rate a game performance tool.
- Publish a QA trend news item.
- Search by business domain and tag.
- Review content as Admin.

**Step 4: Record evidence**

Add screenshots or command output references to the acceptance matrix.

**Step 5: Commit final fixes**

```bash
git add qa-knowledge-platform
git commit -m "test(platform): verify saas game qa acceptance flow"
```
