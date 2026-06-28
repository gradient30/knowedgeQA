# Acceptance Evidence

Generated on 2026-06-28 from the local Docker dev stack.

Evidence commands:

- `.\scripts\project-manager.ps1 test`
- `wsl bash ./scripts/project-manager.sh test`
- `node scripts\verify-runtime-acceptance.js`
- `npx --yes --package playwright node scripts\verify-ui-acceptance.js`
- Stop `frontend`, run `$docker compose -f docker-compose.dev.yml run --rm --no-deps -e NODE_ENV=production -e NEXT_TELEMETRY_DISABLED=1 frontend sh -lc "rm -rf .next && pnpm build"`, then start `frontend`

Screenshot evidence:

- `output/acceptance/ui-knowledge.png`
- `output/acceptance/ui-tools.png`
- `output/acceptance/ui-news.png`

The runtime gate verifies live backend health, SaaS/Game seed data, file upload, knowledge create with linked evidence file/approve/comment/like/favorite/metrics/update/search/delete, tool create/delete/rate/favorite/usage, news source CRUD, news publish/reject, source-backed intelligence flow, and frontend route availability.
