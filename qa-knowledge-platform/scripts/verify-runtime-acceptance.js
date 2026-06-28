const assert = require('assert');

const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
const acceptanceUserId = '00000000-0000-0000-0000-000000000001';

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

function writeJson(method, payload) {
  return {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  };
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

async function verifyKnowledgeWriteFlow() {
  const categories = await readJson(
    `${backendUrl}/api/v1/knowledge/categories?business_domain=saas`
  );
  assert(categories.length > 0, 'SaaS knowledge category is required');

  const marker = `运行态验收知识 ${Date.now()}`;
  const article = await readJson(
    `${backendUrl}/api/v1/knowledge/articles`,
    writeJson('POST', {
      category_id: categories[0].id,
      user_id: acceptanceUserId,
      title: marker,
      summary: 'SaaS API compatibility runtime acceptance',
      content: '验证创建、更新、搜索和删除知识文章。',
      type: '最佳实践',
      business_domain: 'saas',
      visibility: 'team',
      project_key: 'runtime-acceptance',
      tags: ['runtime', 'saas'],
    })
  );

  const updated = await readJson(
    `${backendUrl}/api/v1/knowledge/articles/${article.id}`,
    writeJson('PUT', {
      summary: 'updated runtime acceptance evidence',
      review_status: 'approved',
    })
  );
  assert.strictEqual(updated.summary, 'updated runtime acceptance evidence');
  assert.strictEqual(updated.review_status, 'approved');

  const search = await readJson(
    `${backendUrl}/api/v1/knowledge/search?q=${encodeURIComponent(marker)}&business_domain=saas`
  );
  assert(search.some((item) => item.id === article.id), 'created article must be searchable');

  await readJson(`${backendUrl}/api/v1/knowledge/articles/${article.id}`, {
    method: 'DELETE',
  });
  console.log('knowledge write flow: create, approve, update, search, delete');
}

async function verifyToolsWriteFlow() {
  const categories = await readJson(
    `${backendUrl}/api/v1/tools/categories?business_domain=game`
  );
  assert(categories.length > 0, 'Game tool category is required');

  const tool = await readJson(
    `${backendUrl}/api/v1/tools/`,
    writeJson('POST', {
      category_id: categories[0].id,
      name: `运行态验收工具 ${Date.now()}`,
      url: 'https://example.com/runtime-tool',
      description: '验证工具创建和删除。',
      business_domain: 'game',
      project_key: 'runtime-acceptance',
      features: ['FPS', 'runtime'],
    })
  );
  await readJson(`${backendUrl}/api/v1/tools/${tool.id}`, { method: 'DELETE' });

  const gameTools = await readJson(`${backendUrl}/api/v1/tools/?business_domain=game`);
  assert(gameTools.length > 0, 'Game tool is required for rating flow');
  const targetTool = gameTools[0];

  await readJson(
    `${backendUrl}/api/v1/tools/${targetTool.id}/rating`,
    writeJson('POST', {
      user_id: acceptanceUserId,
      rating: 5,
      review: 'runtime acceptance rating',
      pros_cons: { pros: ['stable'], cons: [] },
    })
  );
  await readJson(
    `${backendUrl}/api/v1/tools/${targetTool.id}/favorite?user_id=${acceptanceUserId}`,
    { method: 'POST' }
  );
  const usage = await readJson(`${backendUrl}/api/v1/tools/${targetTool.id}/usage`, {
    method: 'POST',
  });
  assert(usage.usage_count >= targetTool.usage_count + 1);
  console.log('tools write flow: create, delete, rate, favorite, usage');
}

async function verifyNewsWriteFlow() {
  const source = await readJson(
    `${backendUrl}/api/v1/news/sources`,
    writeJson('POST', {
      name: `运行态验收资讯源 ${Date.now()}`,
      url: 'https://example.com/runtime-news',
      category: '游戏测试',
      business_domain: 'game',
      keywords: ['runtime', 'game'],
      frequency_hours: 24,
      is_active: true,
    })
  );
  const updated = await readJson(
    `${backendUrl}/api/v1/news/sources/${source.id}`,
    writeJson('PUT', { frequency_hours: 12 })
  );
  assert.strictEqual(updated.frequency_hours, 12);
  await readJson(`${backendUrl}/api/v1/news/sources/${source.id}`, {
    method: 'DELETE',
  });

  const newsItems = await readJson(`${backendUrl}/api/v1/news/items?business_domain=game`);
  assert(newsItems.length > 0, 'Game news item is required for review flow');
  const reviewed = await readJson(
    `${backendUrl}/api/v1/news/items/${newsItems[0].id}/publish`,
    { method: 'POST' }
  );
  assert.strictEqual(reviewed.review_status, 'approved');
  const rejected = await readJson(
    `${backendUrl}/api/v1/news/items/${newsItems[0].id}/reject`,
    { method: 'POST' }
  );
  assert.strictEqual(rejected.review_status, 'rejected');
  console.log('news write flow: source create, update, delete, publish, reject');
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
  await verifyKnowledgeWriteFlow();
  await verifyToolsWriteFlow();
  await verifyNewsWriteFlow();
  await verifyFrontendRoutes();
  console.log('Runtime Docker acceptance passed.');
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
