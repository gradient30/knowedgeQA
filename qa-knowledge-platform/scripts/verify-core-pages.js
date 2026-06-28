const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const pages = [
  {
    path: 'frontend/src/app/knowledge/page.tsx',
    apiImport: '@/lib/api/knowledge',
    apiCall: 'listArticles(',
    staticMarker: 'const articles:',
  },
  {
    path: 'frontend/src/app/tools/page.tsx',
    apiImport: '@/lib/api/tools',
    apiCall: 'listTools(',
    staticMarker: 'const tools:',
  },
  {
    path: 'frontend/src/app/news/page.tsx',
    apiImport: '@/lib/api/news',
    apiCall: 'listNewsItems(',
    staticMarker: 'const newsItems:',
  },
];

for (const page of pages) {
  const fullPath = path.join(root, page.path);
  const content = fs.readFileSync(fullPath, 'utf8');
  if (content.includes('开发中')) {
    throw new Error(`${page.path} still contains placeholder text`);
  }
  for (const required of ['SaaS', '游戏', '业务域']) {
    if (!content.includes(required)) {
      throw new Error(`${page.path} is missing required marker: ${required}`);
    }
  }
  if (!content.includes(page.apiImport)) {
    throw new Error(`${page.path} does not import ${page.apiImport}`);
  }
  if (!content.includes(page.apiCall)) {
    throw new Error(`${page.path} does not call ${page.apiCall}`);
  }
  if (content.includes(page.staticMarker)) {
    throw new Error(`${page.path} still uses static demo data`);
  }
}

console.log('Core pages expose SaaS/game QA workspace markers.');
