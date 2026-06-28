# Public Repository Documentation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create public GitHub-ready documentation and real dev/prod deployment instructions for the QA knowledge platform.

**Architecture:** The documentation must describe the current Next.js frontend, FastAPI backend, PostgreSQL, Redis, Celery, Docker, and acceptance gates. Production deployment must be backed by committed deployment artifacts instead of referencing nonexistent compose files.

**Tech Stack:** Markdown, Docker Compose, Next.js 14, FastAPI, PostgreSQL 15, Redis 7, Celery, Poetry, pnpm.

---

### Task 1: Public Repository README

**Files:**
- Modify: `README.md`

**Steps:**
1. Replace the legacy README with a concise public repository overview.
2. Include real quick-start commands for PowerShell and WSL.
3. Link to deployment, architecture, security, operations, and roadmap docs.
4. Avoid claiming unsupported staging deployment or undeclared license terms.

### Task 2: Deployable Dev and Prod Artifacts

**Files:**
- Create: `frontend/Dockerfile`
- Create: `backend/Dockerfile`
- Create: `docker-compose.prod.yml`
- Create: `.env.prod.example`

**Steps:**
1. Add production Dockerfiles without hot reload.
2. Add a single-host production Compose file using explicit environment variables.
3. Add an example production env file with placeholders only.
4. Validate Compose syntax with `docker compose --env-file .env.prod.example -f docker-compose.prod.yml config`.

### Task 3: Standard Documentation Set

**Files:**
- Create: `docs/deployment/dev.md`
- Create: `docs/deployment/prod.md`
- Create: `docs/architecture.md`
- Create: `docs/operations.md`
- Create: `docs/security.md`
- Create: `docs/technical-roadmap.md`

**Steps:**
1. Document development deployment from the existing dev Compose and scripts.
2. Document production deployment from the new production artifacts.
3. Describe architecture, module ownership, data flow, operational checks, and security posture.
4. Keep claims aligned with current acceptance matrix and known gaps.

### Task 4: Verification and Commit

**Files:**
- Verify all changed docs and deployment artifacts.

**Steps:**
1. Run documentation gate: `node scripts/verify-acceptance-docs.js`.
2. Run production Compose config validation.
3. Run `git diff --check`.
4. Stage, commit, and push with a docs-scoped Conventional Commit.
