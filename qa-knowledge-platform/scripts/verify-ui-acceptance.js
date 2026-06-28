const fs = require('fs');
const path = require('path');

const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
const browserChannel = process.env.PLAYWRIGHT_CHANNEL || 'msedge';
const outputDir = path.resolve(__dirname, '..', 'output', 'acceptance');
const dataTimeoutMs = 30000;

const pages = [
  {
    path: '/knowledge',
    name: 'knowledge',
    action: '新建知识',
    modalPlaceholder: '例如：SaaS API',
    saasText: 'SaaS灰度发布复盘',
    gameText: '游戏版本质量报告',
  },
  {
    path: '/tools',
    name: 'tools',
    action: '添加工具',
    modalPlaceholder: '例如：弱网回归',
    saasText: 'SaaS接口契约测试工具',
    gameText: '游戏帧率巡检工具',
  },
  {
    path: '/news',
    name: 'news',
    action: '配置资讯源',
    modalPlaceholder: '例如：SaaS 质量工程周报',
    saasText: 'DORA 指标驱动 SaaS 质量治理复盘',
    gameText: '网易游戏 AI 测试实践与自动化探索',
  },
];

function loadPlaywright() {
  try {
    return require('playwright');
  } catch (error) {
    if (error.code === 'MODULE_NOT_FOUND') {
      throw new Error(
        'Playwright is not installed. Run this gate with: npx --yes --package playwright node scripts/verify-ui-acceptance.js'
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

async function chooseDomain(page, label) {
  await page
    .locator('.ant-segmented-item')
    .filter({ hasText: label })
    .first()
    .click();
}

async function waitForVisibleText(page, text) {
  try {
    await page.getByText(text, { exact: false }).first().waitFor({
      state: 'visible',
      timeout: dataTimeoutMs,
    });
  } catch (error) {
    const pageText = await page
      .locator('body')
      .innerText({ timeout: 5000 })
      .catch(() => '<unable to read page text>');
    throw new Error(
      `Expected text "${text}" was not visible within ${dataTimeoutMs}ms.\n` +
        `Current page text:\n${pageText}`,
      { cause: error }
    );
  }
}

function isBenignDevRequestFailure(request) {
  const failureText = request.failure()?.errorText || '';
  return request.url().includes('.hot-update.') && failureText.includes('ERR_ABORTED');
}

async function main() {
  fs.mkdirSync(outputDir, { recursive: true });

  const { chromium } = loadPlaywright();
  const browser = await launchBrowser(chromium);
  const page = await browser.newPage();
  page.setDefaultTimeout(30000);
  const browserErrors = [];

  page.on('console', (message) => {
    if (message.type() === 'error') {
      browserErrors.push(message.text());
    }
  });
  page.on('requestfailed', (request) => {
    if (isBenignDevRequestFailure(request)) {
      return;
    }
    browserErrors.push(`${request.method()} ${request.url()} ${request.failure()?.errorText}`);
  });

  try {
    for (const check of pages) {
      const url = `${frontendUrl}${check.path}`;
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForLoadState('networkidle', { timeout: dataTimeoutMs }).catch(() => undefined);

      await waitForVisibleText(page, check.saasText);
      await waitForVisibleText(page, check.gameText);

      await chooseDomain(page, '游戏');
      await waitForVisibleText(page, check.gameText);

      await chooseDomain(page, 'SaaS');
      await waitForVisibleText(page, check.saasText);

      await page.locator('main button.ant-btn-primary').last().click();
      await page.getByPlaceholder(check.modalPlaceholder, { exact: false }).first().waitFor({
        state: 'visible',
        timeout: 5000,
      });
      await page.screenshot({
        path: path.join(outputDir, `ui-${check.name}.png`),
        fullPage: true,
      });
      await page.keyboard.press('Escape');

      console.log(`ui ${check.path}: live data, filter, and create action verified`);
    }
  } finally {
    await browser.close();
  }

  if (browserErrors.length > 0) {
    throw new Error(`Browser errors detected:\n${browserErrors.join('\n')}`);
  }

  console.log('UI acceptance passed.');
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
