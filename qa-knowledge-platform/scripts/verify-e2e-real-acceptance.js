const assert = require('assert');
const fs = require('fs');
const path = require('path');

const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
const browserChannel = process.env.PLAYWRIGHT_CHANNEL || 'msedge';
const outputDir = path.resolve(__dirname, '..', 'output', 'acceptance');
const runId = Date.now();

function loadPlaywright() {
  try {
    return require('playwright');
  } catch (error) {
    if (error.code === 'MODULE_NOT_FOUND') {
      throw new Error(
        'Playwright is not installed. Run: npx --yes --package playwright node scripts/verify-e2e-real-acceptance.js'
      );
    }
    throw error;
  }
}

async function launchBrowser(chromium) {
  try {
    return await chromium.launch({ channel: browserChannel });
  } catch (error) {
    if (browserChannel) {
      console.warn(`Could not launch ${browserChannel}: ${error.message}`);
    }
    return chromium.launch();
  }
}

async function readJson(url, options) {
  const response = await fetch(url, options);
  const body = await response.text();

  if (!response.ok) {
    throw new Error(`${url} returned ${response.status}: ${body.slice(0, 300)}`);
  }

  return body ? JSON.parse(body) : null;
}

async function deleteIfExists(url, options) {
  try {
    await fetch(url, options);
  } catch {
    // Cleanup must not hide the original E2E failure.
  }
}

function isBenignRequestFailure(request) {
  const failureText = request.failure()?.errorText || '';
  return (
    failureText.includes('ERR_ABORTED') &&
    (request.url().includes('.hot-update.') ||
      request.url().includes('/_next/static/chunks/') ||
      request.url().includes('?_rsc='))
  );
}

function isBenignConsoleError(text) {
  return text.includes('Failed to fetch RSC payload') && text.includes('Falling back');
}

async function waitForText(page, text) {
  try {
    await page.waitForFunction(
      (expected) => document.body.innerText.includes(expected),
      text,
      { timeout: 30000 }
    );
  } catch (error) {
    const bodyText = await page
      .locator('body')
      .innerText({ timeout: 5000 })
      .catch(() => '<unable to read page text>');
    throw new Error(
      `Expected text "${text}" was not visible.\nCurrent page text:\n${bodyText}`,
      { cause: error }
    );
  }
}

async function chooseDomain(page, label) {
  await page
    .locator('.ant-segmented-item')
    .filter({ hasText: label })
    .first()
    .click();
}

async function getBrowserToken(page) {
  const token = await page.evaluate(() => localStorage.getItem('access_token'));
  assert(token, 'login must persist access_token in browser localStorage');
  return token;
}

async function login(page) {
  await page.goto(`${frontendUrl}/login`, { waitUntil: 'networkidle' });
  await page.locator('#login_email').fill('admin@qa-platform.com');
  await page.locator('#login_password').fill('admin123');
  await Promise.all([
    page.waitForFunction(() => Boolean(localStorage.getItem('access_token')), {
      timeout: 30000,
    }),
    page.locator('#login_password').press('Enter'),
  ]);
  await page.screenshot({
    path: path.join(outputDir, 'e2e-real-login.png'),
    fullPage: true,
  });
  console.log('e2e login: admin browser login persisted token');
}

async function verifyKnowledge(page, cleanup) {
  const marker = `E2E真实验收知识-${runId}`;
  await page.goto(`${frontendUrl}/knowledge`, { waitUntil: 'networkidle' });
  await waitForText(page, 'QA知识库');
  await waitForText(page, 'SaaS灰度发布复盘');
  await chooseDomain(page, '游戏');
  await waitForText(page, '游戏版本质量报告');
  await chooseDomain(page, '全部');

  await page.locator('main button.ant-btn-primary').first().click();
  await page.getByPlaceholder('例如：SaaS API 兼容性验收复盘').fill(marker);
  await page.locator('textarea').fill('验收背景：真实浏览器创建。\n测试结论：通过。\n风险与后续：自动清理。');
  await page.getByLabel('摘要').fill('真实浏览器 E2E 创建知识');
  await page.getByLabel('项目').fill('e2e-real');
  await page.getByLabel('标签').fill('e2e,saas');
  const [createResponse] = await Promise.all([
    page.waitForResponse(
      (response) =>
        response.url().includes('/api/v1/knowledge/articles') &&
        response.request().method() === 'POST',
      { timeout: 30000 }
    ),
    page.locator('.ant-modal-footer button.ant-btn-primary').last().click(),
  ]);
  const createdArticle = await createResponse.json();
  cleanup.push(async () => {
    await deleteIfExists(`${backendUrl}/api/v1/knowledge/articles/${createdArticle.id}`, {
      method: 'DELETE',
    });
  });
  await waitForText(page, marker);
  await page.screenshot({
    path: path.join(outputDir, 'e2e-real-knowledge.png'),
    fullPage: true,
  });

  console.log('e2e knowledge: live data, domain filter, create flow verified');
}

async function verifyTools(page, cleanup) {
  const marker = `E2E真实验收工具-${runId}`;
  await page.goto(`${frontendUrl}/tools`, { waitUntil: 'networkidle' });
  await waitForText(page, '测试工具库');
  await waitForText(page, 'SaaS接口契约测试工具');
  await chooseDomain(page, '游戏');
  await waitForText(page, '游戏帧率巡检工具');
  await chooseDomain(page, '全部');

  await page.locator('main button.ant-btn-primary').first().click();
  await page.getByPlaceholder('例如：弱网回归巡检工具').fill(marker);
  await page.getByLabel('项目').fill('e2e-real');
  await page.getByLabel('特性').fill('e2e,api');
  await page.locator('textarea').fill('真实浏览器 E2E 创建工具。');
  const [createResponse] = await Promise.all([
    page.waitForResponse(
      (response) =>
        response.url().includes('/api/v1/tools/') &&
        response.request().method() === 'POST',
      { timeout: 30000 }
    ),
    page.locator('.ant-modal-footer button.ant-btn-primary').last().click(),
  ]);
  const createdTool = await createResponse.json();
  cleanup.push(async () => {
    await deleteIfExists(`${backendUrl}/api/v1/tools/${createdTool.id}`, {
      method: 'DELETE',
    });
  });
  await waitForText(page, marker);
  await page.screenshot({
    path: path.join(outputDir, 'e2e-real-tools.png'),
    fullPage: true,
  });

  console.log('e2e tools: live data, domain filter, create flow verified');
}

async function verifyFiles(page, cleanup) {
  const fileName = `e2e-real-upload-${runId}.txt`;
  const filePath = path.join(outputDir, fileName);
  fs.writeFileSync(filePath, `real browser upload acceptance ${new Date().toISOString()}\n`);

  await page.goto(`${frontendUrl}/files`, { waitUntil: 'networkidle' });
  await waitForText(page, '文件中心');
  await page.locator('input[type="file"]').waitFor({ state: 'attached', timeout: 30000 });
  const token = await getBrowserToken(page);

  const [uploadResponse] = await Promise.all([
    page.waitForResponse(
      (response) =>
        response.url().includes('/api/v1/files/upload') &&
        response.request().method() === 'POST',
      { timeout: 30000 }
    ),
    page.setInputFiles('input[type="file"]', filePath),
  ]);
  const uploadPayload = await uploadResponse.json();
  assert.strictEqual(uploadResponse.status(), 200, 'file upload request must return 200');
  assert.strictEqual(uploadPayload.success, true, 'file upload response must be successful');
  cleanup.push(async () => {
    await deleteIfExists(`${backendUrl}/api/v1/files/${uploadPayload.file_info.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
  });
  await waitForText(page, fileName);
  await waitForText(page, '已上传文件');
  await page.getByRole('tab', { name: '文件管理' }).click();
  await waitForText(page, fileName);
  await page.screenshot({
    path: path.join(outputDir, 'e2e-real-files.png'),
    fullPage: true,
  });

  console.log('e2e files: authenticated UI upload and management list verified');
}

async function verifyNews(page) {
  await page.goto(`${frontendUrl}/news`, { waitUntil: 'networkidle' });
  await waitForText(page, '质量情报中心');
  await waitForText(page, 'DORA 指标驱动 SaaS 质量治理复盘');
  await chooseDomain(page, '游戏');
  await waitForText(page, '网易游戏 AI 测试实践与自动化探索');
  await page.locator('main button.ant-btn-primary').first().click();
  await page.getByPlaceholder('例如：SaaS 质量工程周报').waitFor({
    state: 'visible',
    timeout: 10000,
  });
  await page.keyboard.press('Escape');
  await page.screenshot({
    path: path.join(outputDir, 'e2e-real-news.png'),
    fullPage: true,
  });
  console.log('e2e news: live data, domain filter, source configuration modal verified');
}

async function verifyNotifications(page) {
  const email = `e2e-real-${runId}@example.com`;
  await page.goto(`${frontendUrl}/admin/notifications`, { waitUntil: 'domcontentloaded' });
  await waitForText(page, '邮件通知管理');
  await waitForText(page, 'SMTP服务状态');
  await page.getByRole('button', { name: '发送测试邮件' }).click();
  const modal = page.locator('.ant-modal').filter({ hasText: '发送测试邮件' }).last();
  await modal.getByPlaceholder('请输入收件人邮箱').fill(email);
  await modal.getByRole('button', { name: '发送测试邮件' }).click();
  await waitForText(page, '测试邮件发送成功');
  await page.getByRole('tab', { name: /发送日志/ }).click();
  await waitForText(page, email);
  await page.screenshot({
    path: path.join(outputDir, 'e2e-real-notifications.png'),
    fullPage: true,
  });
  console.log('e2e notifications: admin test email and log display verified');
}

async function runCleanup(cleanup) {
  for (const item of cleanup.reverse()) {
    await item();
  }
}

async function main() {
  fs.mkdirSync(outputDir, { recursive: true });

  const health = await readJson(`${backendUrl}/health`);
  assert.strictEqual(health.status, 'healthy', 'backend must be healthy before E2E');

  const { chromium } = loadPlaywright();
  const browser = await launchBrowser(chromium);
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.setDefaultTimeout(30000);
  const browserErrors = [];
  const cleanup = [];

  page.on('console', (message) => {
    if (message.type() === 'error') {
      const text = message.text();
      if (!isBenignConsoleError(text)) {
        browserErrors.push(text);
      }
    }
  });
  page.on('requestfailed', (request) => {
    if (!isBenignRequestFailure(request)) {
      browserErrors.push(`${request.method()} ${request.url()} ${request.failure()?.errorText}`);
    }
  });

  try {
    await login(page);
    await verifyKnowledge(page, cleanup);
    await verifyTools(page, cleanup);
    await verifyFiles(page, cleanup);
    await verifyNews(page);
    await verifyNotifications(page);
  } finally {
    await runCleanup(cleanup);
    await browser.close();
  }

  if (browserErrors.length > 0) {
    throw new Error(`Browser errors detected:\n${browserErrors.join('\n')}`);
  }

  console.log('Real browser E2E acceptance passed.');
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
