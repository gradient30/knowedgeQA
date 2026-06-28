const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');

const checks = [
  {
    file: 'scripts/project-manager.ps1',
    markers: [
      'function Restore-FrontendDevServer',
      'Restore-FrontendDevServer',
      '运行SaaS/Game UI验收',
    ],
  },
  {
    file: 'scripts/project-manager.sh',
    markers: [
      'restore_frontend_dev_server()',
      'restore_frontend_dev_server',
      '运行SaaS/Game UI验收',
    ],
  },
];

for (const check of checks) {
  const content = fs.readFileSync(path.join(root, check.file), 'utf8');
  for (const marker of check.markers) {
    if (!content.includes(marker)) {
      throw new Error(`${check.file} missing marker: ${marker}`);
    }
  }
}

console.log('Project manager scripts restore frontend before UI acceptance.');
