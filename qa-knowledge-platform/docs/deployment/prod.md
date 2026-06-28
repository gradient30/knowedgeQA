# Production Deployment

This guide deploys the current repository as a single-host Docker Compose production stack. It uses the committed production artifacts:

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker-compose.prod.yml`
- `.env.prod.example`

For managed cloud deployment, keep the same environment variables and replace the bundled PostgreSQL and Redis services with managed equivalents.

## Prerequisites

- Linux server or VM with Docker Engine and Docker Compose V2.
- Network access to pull base images from Docker Hub or an internal registry mirror.
- DNS names for frontend and API, for example `qa.example.com` and `api.qa.example.com`.
- TLS termination through a reverse proxy or platform load balancer.
- Persistent disk for PostgreSQL, Redis, uploads, and logs.
- SMTP account if email delivery is enabled.

## 1. Prepare Configuration

```bash
cd qa-knowledge-platform
cp .env.prod.example .env.prod
```

Edit `.env.prod` and replace every placeholder:

- `FRONTEND_ORIGIN`: public frontend origin, for example `https://qa.example.com`.
- `PUBLIC_API_URL`: public backend API origin, for example `https://api.qa.example.com`.
- `ALLOWED_HOSTS`: JSON list containing allowed browser origins.
- `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `SECRET_KEY`: strong random values.
- SMTP values when `ENABLE_EMAIL_QUEUE=true`.

Do not commit `.env.prod`.

## 2. Validate Compose Configuration

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml config
```

This command must render the final configuration without missing-variable errors.

## 3. Build Images

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml build
```

The frontend image embeds `NEXT_PUBLIC_API_URL` at build time, so rebuild the frontend image whenever the public API URL changes.

## 4. Start Database and Cache

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d db redis
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

Wait until both services report healthy.

## 5. Run Database Migrations

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm backend \
  poetry run alembic upgrade head
```

Run migrations before starting application traffic. The backend can create tables at startup, but Alembic remains the release-grade migration path.

## 6. Start Application Services

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d backend celery-worker celery-beat frontend
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

Expose the services through a reverse proxy:

- Frontend container: `http://127.0.0.1:3000`
- Backend container: `http://127.0.0.1:8000`

Terminate HTTPS at the proxy and forward requests to these local ports.

## 7. Verify Deployment

```bash
curl -f http://127.0.0.1:8000/health
curl -f http://127.0.0.1:3000
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail=100 backend
```

Then verify public URLs:

```bash
curl -f https://api.qa.example.com/health
curl -f https://qa.example.com
```

## 8. Backup and Restore

Create a PostgreSQL backup:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec db \
  sh -lc 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > backup.sql
```

Back up Docker volumes:

- `prod_db_data`
- `prod_redis_data`
- `prod_uploads`
- `prod_logs`

Test restore procedures in a non-production environment before relying on backups.

## 9. Upgrade Procedure

```bash
git pull
docker compose --env-file .env.prod -f docker-compose.prod.yml build
docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm backend \
  poetry run alembic upgrade head
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

If verification fails, roll back to the previous Git commit and rebuild images. Preserve database backups before migrations.

## Production Notes

- The production Compose file is suitable for a single host. For Kubernetes, ECS, or other platforms, translate services and environment variables directly.
- Use managed PostgreSQL, managed Redis, and object storage for higher availability.
- Local file uploads are persisted in the `prod_uploads` volume. For multi-node production, replace local storage with an object storage implementation.
