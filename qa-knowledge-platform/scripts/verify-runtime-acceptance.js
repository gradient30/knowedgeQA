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

async function verifyAcceptanceLogin() {
  const login = await readJson(
    `${backendUrl}/api/v1/auth/login`,
    writeJson('POST', {
      email: 'admin@qa-platform.com',
      password: 'admin123',
    })
  );
  assert(login.access_token, 'runtime acceptance requires an admin access token');
  return {
    Authorization: `Bearer ${login.access_token}`,
  };
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

async function verifyFileUpload(authHeaders) {
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
      headers: authHeaders,
      body: form,
    }
  );

  assert.strictEqual(upload.success, true, 'file upload must succeed');

  const files = await readJson(`${backendUrl}/api/v1/files/list`, {
    headers: authHeaders,
  });
  assert(files.total >= 1, `file list expected at least 1 item, got ${files.total}`);
  console.log(`file upload: success, listed files ${files.total}`);
  return upload.file_info.id;
}

async function verifyKnowledgeWriteFlow(attachmentFileId) {
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
      attachment_file_ids: [attachmentFileId],
    })
  );
  assert.deepStrictEqual(
    article.attachment_file_ids,
    [attachmentFileId],
    'created article must link uploaded evidence file'
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
  assert.deepStrictEqual(updated.attachment_file_ids, [attachmentFileId]);

  const detail = await readJson(`${backendUrl}/api/v1/knowledge/articles/${article.id}`);
  assert.deepStrictEqual(
    detail.attachment_file_ids,
    [attachmentFileId],
    'article detail must return linked evidence file'
  );

  const comment = await readJson(
    `${backendUrl}/api/v1/knowledge/articles/${article.id}/comments`,
    writeJson('POST', {
      user_id: acceptanceUserId,
      content: 'QA manager runtime acceptance comment',
    })
  );
  assert.strictEqual(comment.content, 'QA manager runtime acceptance comment');
  const comments = await readJson(
    `${backendUrl}/api/v1/knowledge/articles/${article.id}/comments`
  );
  assert(comments.some((item) => item.id === comment.id), 'created comment must be listed');

  const liked = await readJson(
    `${backendUrl}/api/v1/knowledge/articles/${article.id}/like?user_id=${acceptanceUserId}`,
    { method: 'POST' }
  );
  assert.strictEqual(liked.liked, true);
  assert(liked.like_count >= 1);

  const favorited = await readJson(
    `${backendUrl}/api/v1/knowledge/articles/${article.id}/favorite?user_id=${acceptanceUserId}`,
    { method: 'POST' }
  );
  assert.strictEqual(favorited.favorited, true);
  assert(favorited.favorite_count >= 1);

  const metrics = await readJson(
    `${backendUrl}/api/v1/knowledge/metrics?business_domain=saas`
  );
  assert(metrics.comment_count >= 1, 'knowledge metrics must include comments');
  assert(metrics.like_count >= 1, 'knowledge metrics must include likes');
  assert(metrics.favorite_count >= 1, 'knowledge metrics must include favorites');

  const search = await readJson(
    `${backendUrl}/api/v1/knowledge/search?q=${encodeURIComponent(marker)}&business_domain=saas`
  );
  assert(search.some((item) => item.id === article.id), 'created article must be searchable');

  await readJson(`${backendUrl}/api/v1/knowledge/articles/${article.id}`, {
    method: 'DELETE',
  });
  console.log('knowledge write flow: create with evidence file, approve, comment, like, favorite, metrics, update, search, delete');
  return article.id;
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
  return {
    sourceId: source.id,
    itemId: newsItems[0].id,
  };
}

async function verifyAuditFlow(articleId, newsAuditTarget) {
  const knowledgeLogs = await readJson(
    `${backendUrl}/api/v1/audit/logs?resource_type=knowledge_article&resource_id=${articleId}&business_domain=saas`
  );
  assert.deepStrictEqual(
    knowledgeLogs.map((log) => log.action),
    ['delete', 'review', 'create'],
    'knowledge audit logs must record create, review, and delete'
  );
  assert.strictEqual(
    knowledgeLogs[1].metadata.review_status,
    'approved',
    'knowledge review audit must include approved status'
  );

  const sourceLogs = await readJson(
    `${backendUrl}/api/v1/audit/logs?resource_type=news_source&resource_id=${newsAuditTarget.sourceId}&business_domain=game`
  );
  assert.deepStrictEqual(
    sourceLogs.map((log) => log.action),
    ['delete', 'update', 'create'],
    'news source audit logs must record create, update, and delete'
  );

  const reviewLogs = await readJson(
    `${backendUrl}/api/v1/audit/logs?resource_type=news_item&resource_id=${newsAuditTarget.itemId}&action=review&limit=2`
  );
  assert.deepStrictEqual(
    reviewLogs.map((log) => log.metadata.review_status),
    ['rejected', 'approved'],
    'news item audit logs must record publish and reject decisions'
  );
  console.log('audit flow: knowledge lifecycle, news review, and source configuration changes');
}

async function verifyIntelligenceFlow() {
  const gameCategories = await readJson(
    `${backendUrl}/api/v1/knowledge/categories?business_domain=game`
  );
  assert(gameCategories.length > 0, 'Game knowledge category is required');
  const gameMarker = `运行态验收游戏相似文章 ${Date.now()}`;
  const gameArticle = await readJson(
    `${backendUrl}/api/v1/knowledge/articles`,
    writeJson('POST', {
      category_id: gameCategories[0].id,
      user_id: acceptanceUserId,
      title: gameMarker,
      summary: '游戏弱网与提审质量风险',
      content: '验证相似文章只能使用已审核游戏知识。',
      type: 'Bug案例',
      business_domain: 'game',
      visibility: 'team',
      project_key: 'runtime-acceptance-game',
      tags: ['runtime', 'game'],
      attachment_file_ids: [],
    })
  );
  await readJson(
    `${backendUrl}/api/v1/knowledge/articles/${gameArticle.id}`,
    writeJson('PUT', { review_status: 'approved' })
  );

  const similarArticles = await readJson(
    `${backendUrl}/api/v1/intelligence/similar-articles?business_domain=saas&q=${encodeURIComponent('灰度')}`
  );
  assert(similarArticles.length > 0, 'similar articles must use reviewed content');
  assert(
    similarArticles.every((item) => item.source_links?.[0]?.startsWith('/api/v1/knowledge/articles/')),
    'similar articles must include source links'
  );
  const gameSimilarArticles = await readJson(
    `${backendUrl}/api/v1/intelligence/similar-articles?business_domain=game&q=${encodeURIComponent('弱网')}`
  );
  assert(
    gameSimilarArticles.some((item) => item.id === gameArticle.id),
    'game similar articles must use reviewed game content'
  );

  const toolRecommendations = await readJson(
    `${backendUrl}/api/v1/intelligence/tool-recommendations?business_domain=saas&q=API`
  );
  assert(toolRecommendations.length > 0, 'tool recommendations must use recommended tools');
  assert(
    toolRecommendations.every((item) => item.source_links?.[0]?.startsWith('/api/v1/tools/')),
    'tool recommendations must include source links'
  );

  const newsSummary = await readJson(
    `${backendUrl}/api/v1/intelligence/news-summary?business_domain=saas&limit=3`
  );
  assert(newsSummary.item_count > 0, 'news summary must use reviewed news');
  assert(
    newsSummary.source_links.every((link) => link.startsWith('/api/v1/news/items/')),
    'news summary must include source links'
  );
  await readJson(`${backendUrl}/api/v1/knowledge/articles/${gameArticle.id}`, {
    method: 'DELETE',
  });
  console.log('intelligence flow: similar articles, tool recommendations, source-backed news summary');
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
  const authHeaders = await verifyAcceptanceLogin();
  await verifyApiData();
  const attachmentFileId = await verifyFileUpload(authHeaders);
  const articleId = await verifyKnowledgeWriteFlow(attachmentFileId);
  await verifyToolsWriteFlow();
  const newsAuditTarget = await verifyNewsWriteFlow();
  await verifyAuditFlow(articleId, newsAuditTarget);
  await verifyIntelligenceFlow();
  await verifyFrontendRoutes();
  console.log('Runtime Docker acceptance passed.');
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
