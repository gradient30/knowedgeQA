# Security

This repository is public-ready only when secrets stay outside Git and deployments use environment-specific configuration.

## Secrets

Never commit:

- `.env`
- `.env.prod`
- SMTP passwords
- JWT `SECRET_KEY`
- Database or Redis production passwords
- Cloud storage credentials
- TLS private keys

Use `.env.prod.example` only as a placeholder template.

## Authentication

The backend uses JWT authentication and role-aware API flows. Email verification, password reset, and email change flows use persisted one-time tokens. Invalid or reused tokens are rejected by backend tests and runtime acceptance.

Required production settings:

- Set a strong `SECRET_KEY`.
- Keep `ACCESS_TOKEN_EXPIRE_MINUTES` aligned with business risk.
- Restrict `ALLOWED_HOSTS` to trusted frontend origins.
- Serve frontend and API through HTTPS.

## Authorization

Sensitive flows require authenticated users and role checks:

- Private file download and deletion.
- Admin user governance.
- Notification administration.
- Review and publication actions.
- Audit log access.

When adding APIs, place authorization checks near the route or service entrypoint and add tests for forbidden access.

## File Uploads

Current upload controls include file size limits, allowed file extensions, authenticated upload/list/download/delete, and private owner/admin access. Production deployments should add:

- Antivirus or malware scanning for uploaded files.
- Object storage for multi-node deployments.
- CDN rules that do not bypass backend authorization for private files.

## Network and Runtime

Recommended production baseline:

- HTTPS only at the reverse proxy or load balancer.
- PostgreSQL and Redis not exposed to the public internet.
- Redis password enabled.
- Docker volumes backed up.
- Logs retained with access controls.
- Admin accounts reviewed regularly.

## Dependency and Code Checks

Run the standard gate before release:

```bash
bash ./scripts/project-manager.sh test
```

or:

```powershell
.\scripts\project-manager.ps1 test
```

For targeted backend checks:

```bash
cd backend
poetry run pytest tests/ --cov=app
```

For targeted frontend checks:

```bash
cd frontend
pnpm type-check
pnpm lint
pnpm build
```

## Disclosure

Do not publish vulnerability details in public issues until a fix is available. Track sensitive findings in a private issue tracker or security advisory workflow.
