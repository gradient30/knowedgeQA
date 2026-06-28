# Operations

This document defines routine checks and release operations for the current project.

## Health Checks

Backend:

```bash
curl -f http://localhost:8000/health
curl -f http://localhost:8000/health/detailed
```

Frontend:

```bash
curl -f http://localhost:3000
```

Docker:

```bash
docker compose -f docker-compose.dev.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

`/health/detailed` checks PostgreSQL, Redis, Celery visibility, and host system information.

## Logs

Development:

```powershell
.\scripts\project-manager.ps1 logs -Service backend -Follow
```

```bash
bash ./scripts/project-manager.sh logs --service backend --follow
```

Production:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail=200 backend
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f celery-worker
```

## Release Checklist

Before merging or deploying shared behavior:

```powershell
.\scripts\project-manager.ps1 test
```

or:

```bash
bash ./scripts/project-manager.sh test
```

For production release:

1. Confirm `git status --short` is clean.
2. Build production images.
3. Back up PostgreSQL and uploads.
4. Run Alembic migrations.
5. Start services.
6. Verify `/health`, frontend page load, logs, and key authenticated flows.

## Database Operations

Current migration head:

```bash
docker compose -f docker-compose.dev.yml exec backend poetry run alembic heads
```

Apply migrations:

```bash
docker compose -f docker-compose.dev.yml exec backend poetry run alembic upgrade head
```

Production:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm backend \
  poetry run alembic upgrade head
```

## Backup Targets

Back up these production assets:

- PostgreSQL database.
- `prod_uploads` volume.
- `.env.prod` in a secure secret manager.
- Reverse proxy TLS configuration.
- SMTP and external service credentials stored outside Git.

## Rollback

Application rollback:

1. Check out the previous Git commit.
2. Rebuild images.
3. Restart services with `docker compose up -d`.
4. Verify health and logs.

Database rollback is migration-specific. Do not downgrade a production database without a tested rollback plan and a fresh backup.

## Incident Triage

Use audit logs and application logs together:

- API and middleware logs identify request failures.
- Audit logs identify domain changes for knowledge, news, tools, and administration.
- Notification logs identify email template and delivery attempts.

Escalate production issues when authentication, private files, admin governance, or migrations are affected.
