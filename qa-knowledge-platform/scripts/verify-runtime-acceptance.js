const assert = require('assert');

const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3000';

const apiChecks = [
  ['/api/v1/knowledge/categories?business_domain=saas', 1],
  ['/api/v1/knowledge/categories?business_domain=game', 1],
  ['/api/v1/knowledge/articles?business_domain=saas', 1],
  ['/api/v1/knowledge/articles?business_domain=game', 1],
  ['/api/v1/tools/?business_domain=saas', 1],
  ['/api/v1/tools/?business_domain=game', 1],
  ['/api/v1/news/items?business_domain=saas', 1],
  ['/api/v1/news/items?business_domain=game', 1],
  ['/api/v1/news/sources?business_domain=saas', 1],
  ['/api/v1/news/sources?business_domain=game', 1],
];

const frontendRoutes = [
  '/',
  '/knowledge',
  '/tools',
  '/news',
  '/files',
  '/login',
  '/register',
];

async function readJson(url, options) {
  const response = await fetch(url, options);
  const body = await response.text();

  if (!response.ok) {
    throw new Error(`${url} returned ${response.status}: ${body.slice(0, 300)}`);
  }

  return body ? JSON.parse(body) : null;
}

function itemCount(payload) {
  if (Array.isArray(payload)) {
    return payload.length;
  }
  if (Array.isArray(payload?.items)) {
    return payload.items.length;
  }
  if (typeof payload?.total === 'number') {
    return payload.total;
  }
  throw new Error(`unsupported list payload: ${JSON.stringify(payload).slice(0, 300)}`);
}

async function verifyHealth() {
  const health = await readJson(`${backendUrl}/health`);
  assert.strictEqual(health.status, 'healthy', 'backend health must be healthy');
  console.log('backend health: healthy');
}

async function verifyApiData() {
  for (const [path, minimum] of apiChecks) {
    const payload = await readJson(`${backendUrl}${path}`);
    const count = itemCount(payload);
    assert(
      count >= minimum,
      `${path} expected at least ${minimum} item(s), got ${count}`
    );
    console.log(`${path}: ${count}`);
  }
}

async function verifyFileUpload() {
  const form = new FormData();
  const content = `runtime acceptance ${new Date().toISOString()}\n`;
  form.append(
    'file',
    new Blob([content], { type: 'text/plain' }),
    'runtime-acceptance.txt'
  );

  const upload = await readJson(
    `${backendUrl}/api/v1/files/upload?is_public=true`,
    {
      method: 'POST',
      body: form,
    }
  );

  assert.strictEqual(upload.success, true, 'file upload must succeed');

  const files = await readJson(`${backendUrl}/api/v1/files/list`);
  assert(files.total >= 1, `file list expected at least 1 item, got ${files.total}`);
  console.log(`file upload: success, listed files ${files.total}`);
}

async function verifyFrontendRoutes() {
  for (const route of frontendRoutes) {
    const response = await fetch(`${frontendUrl}${route}`);
    assert(
      response.ok,
      `${route} expected HTTP 200-299, got ${response.status}`
    );
    console.log(`frontend ${route}: ${response.status}`);
  }
}

async function main() {
  await verifyHealth();
  await verifyApiData();
  await verifyFileUpload();
  await verifyFrontendRoutes();
  console.log('Runtime Docker acceptance passed.');
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
