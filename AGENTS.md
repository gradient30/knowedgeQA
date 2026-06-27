# Repository Guidelines

## Project Structure & Module Organization

This repository contains a QA knowledge collaboration platform under `qa-knowledge-platform/`. The frontend is a Next.js 14 app in `frontend/`, with routes in `src/app/`, shared UI in `src/components/`, API clients and stores in `src/lib/`, and types in `src/types/`. The backend is a FastAPI service in `backend/`, with `app/main.py`, shared configuration in `app/core/`, routing in `app/api/`, domain modules in `app/modules/`, Alembic migrations in `alembic/`, and tests in `tests/`. Project scripts and Compose files live in `scripts/` and `docker-compose.*.yml`.

## Build, Test, and Development Commands

From `qa-knowledge-platform/`, use `./scripts/project-manager.sh start --env dev` to start the Docker stack and `./scripts/project-manager.sh test` to run tests. For frontend-only work, run `cd frontend && pnpm install && pnpm dev`; use `pnpm build`, `pnpm lint`, and `pnpm type-check` before submitting changes. For backend-only work, run `cd backend && poetry install`, then `poetry run uvicorn app.main:app --reload`; apply migrations with `poetry run alembic upgrade head` and test with `poetry run pytest tests/ --cov=app`.

## Coding Style & Naming Conventions

Frontend code uses TypeScript, PascalCase React components, camelCase helpers, and 2-space indentation. Prettier requires semicolons, single quotes, ES5 trailing commas, and an 80-column print width. ESLint extends `next/core-web-vitals` and `@typescript-eslint/recommended`; unused variables and `var` are errors. Backend code targets Python 3.11+, uses Black/isort with 88-character lines, and keeps modules under `app/modules/<feature>/`.

## Testing Guidelines

Backend tests use pytest and follow `test_*.py` naming in `backend/tests/`. Keep API, service, and model behavior covered near the affected module. For frontend changes, add tests near the feature when practical and always run lint/type checks. Use Playwright scripts such as `test-p1-file-upload.js` for upload or UI-flow verification.

## Commit & Pull Request Guidelines

The README asks contributors to follow Conventional Commits; use messages such as `feat(auth): add password reset` or `fix(files): validate upload type`. History is minimal, so prefer scopes matching `frontend`, `backend`, or a domain module. Pull requests should include a summary, linked issue when available, tests run, screenshots for UI changes, and notes for migrations or environment changes.

## Security & Configuration Tips

Do not commit secrets. Use `.env.dev` or `backend/.env` for local configuration, and keep database, Redis, JWT, SMTP, and storage settings environment-specific. The full local stack expects PostgreSQL on `5432` and Redis on `6379`.
