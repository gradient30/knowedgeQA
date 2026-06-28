# Technical Roadmap

This roadmap describes practical iteration areas for evolving the platform toward large SaaS and game QA operations. It is not a commitment schedule.

## Current Baseline

The project has a deterministic MVP for:

- SaaS and game business taxonomy.
- Knowledge articles with collaboration signals.
- Authenticated evidence files.
- Tool catalog governance.
- QA news source governance.
- Notification settings, templates, and logs.
- Audit logs and administrator workflows.
- Source-backed intelligence APIs.

## P0: Production Hardening

- Add login failure throttling and account lock policy.
- Replace simulated user data export with real article, comment, file, and audit export.
- Complete invitation email delivery and acceptance flow.
- Add frontend forgot-password request UX to match the backend reset-token flow.
- Add malware scanning and object storage support for production file uploads.
- Add production observability: structured log shipping, metrics, dashboards, and alerts.

## P1: Enterprise SaaS QA Workflows

- Add workspace and tenant boundaries if multiple organizations share one deployment.
- Add release quality dashboards for incident review, regression risk, and DORA-style signals.
- Add approval policies for high-impact knowledge and tool changes.
- Add richer search across articles, tools, news, and evidence files.

## P2: Game QA Workflows

- Add build/version quality reports with platform, device, region, and performance dimensions.
- Track game-specific evidence such as FPS, crash, weak network, compatibility, and localization results.
- Add review workflows for live operations, hotfixes, and seasonal events.
- Add integrations for crash analytics, telemetry, and test device labs.

## P3: Intelligence Evolution

Current intelligence is deterministic and source-backed. Future LLM or agent features should require:

- Reviewed production datasets.
- Source citation in every generated answer.
- Evaluation sets for SaaS and game QA tasks.
- Human review for release-impacting recommendations.
- Audit trails for generated suggestions and accepted actions.

## Engineering Quality

Keep these gates mandatory for shared changes:

- Backend regression with coverage.
- Alembic single-head and fresh database upgrade.
- Frontend type-check, lint, and build.
- Runtime acceptance.
- Browser UI acceptance.
- Real browser E2E acceptance for key flows.
- Documentation gate when README, deployment, architecture, or acceptance docs change.
