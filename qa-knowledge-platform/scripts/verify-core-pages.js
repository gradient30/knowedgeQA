const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const pages = [
  'frontend/src/app/knowledge/page.tsx',
  'frontend/src/app/tools/page.tsx',
  'frontend/src/app/news/page.tsx',
];

for (const page of pages) {
  const fullPath = path.join(root, page);
  const content = fs.readFileSync(fullPath, 'utf8');
  if (content.includes('开发中')) {
    throw new Error(`${page} still contains placeholder text`);
  }
  for (const required of ['SaaS', '游戏', '业务域']) {
    if (!content.includes(required)) {
      throw new Error(`${page} is missing required marker: ${required}`);
    }
  }
}

console.log('Core pages expose SaaS/game QA workspace markers.');
