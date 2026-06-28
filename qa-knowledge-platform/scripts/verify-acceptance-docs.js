const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');

const requiredFiles = [
  'docs/plans/acceptance-matrix-saas-game-qa.md',
  'P1-verification-checklist.md',
  'P2-verification-checklist.md',
  'P3-verification-checklist.md',
];

const requiredMarkers = [
  'SaaS/Game Baseline Acceptance',
  'saas',
  'game',
  'GET /api/v1/knowledge/articles',
  'GET /api/v1/tools',
  'GET /api/v1/news/items',
  'node scripts/verify-runtime-acceptance.js',
  'npx --yes --package playwright node scripts/verify-ui-acceptance.js',
  'Runtime Docker acceptance',
  'UI acceptance',
  'knowledge write flow',
  'create with evidence file',
  'comment, like, favorite, metrics',
  'intelligence flow',
  'source-backed news summary',
  'output/acceptance/ui-knowledge.png',
  'pnpm build',
];

for (const file of requiredFiles) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) {
    throw new Error(`${file} is missing`);
  }
}

const matrix = fs.readFileSync(
  path.join(root, 'docs/plans/acceptance-matrix-saas-game-qa.md'),
  'utf8'
);

for (const marker of requiredMarkers) {
  if (!matrix.includes(marker)) {
    throw new Error(`acceptance matrix missing marker: ${marker}`);
  }
}

for (const staleMarker of ['Blocked: command not found', 'Docker availability | `docker --version` | Blocked']) {
  if (matrix.includes(staleMarker)) {
    throw new Error(`acceptance matrix contains stale blocked evidence: ${staleMarker}`);
  }
}

for (const checklist of requiredFiles.slice(1)) {
  const content = fs.readFileSync(path.join(root, checklist), 'utf8');
  if (!content.includes('SaaS/Game Baseline Acceptance')) {
    throw new Error(`${checklist} missing SaaS/Game acceptance section`);
  }
}

console.log('Acceptance docs cover SaaS/Game release markers.');
