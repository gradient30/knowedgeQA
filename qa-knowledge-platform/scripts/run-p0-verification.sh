#!/bin/bash

# P0问题完整验证流程
# 包括Docker环境搭建、服务启动、自动化测试

set -e

echo "🎯 开始P0问题完整验证流程..."

# 检查必要的工具
echo "🔧 检查必要工具..."
command -v docker >/dev/null 2>&1 || { echo "❌ Docker未安装"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose未安装"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js未安装"; exit 1; }

# 设置权限
chmod +x scripts/p0-test.sh

# 步骤1: 启动Docker测试环境
echo "📦 步骤1: 启动Docker测试环境..."
./scripts/p0-test.sh

# 步骤2: 等待服务完全启动
echo "⏳ 步骤2: 等待服务完全启动..."
sleep 60

# 步骤3: 安装Playwright（如果需要）
echo "🎭 步骤3: 准备自动化测试环境..."
if ! command -v npx >/dev/null 2>&1; then
  echo "❌ npm/npx未安装，无法运行自动化测试"
  echo "请手动访问 http://localhost:3000 进行验证"
  exit 1
fi

# 检查是否已安装playwright
if ! npx playwright --version >/dev/null 2>&1; then
  echo "📦 安装Playwright..."
  npx playwright install chromium
fi

# 步骤4: 运行自动化测试
echo "🤖 步骤4: 运行P0自动化测试..."
node scripts/p0-automated-test.js

# 步骤5: 显示测试结果
echo "📊 步骤5: 测试完成"

# 询问是否保持环境运行
read -p "是否保持测试环境运行以便手动验证？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "🔗 测试环境保持运行，访问地址:"
  echo "   前端: http://localhost:3000"
  echo "   后端: http://localhost:8000"
  echo "   后端健康检查: http://localhost:8000/health"
  echo ""
  echo "🛑 完成测试后请运行: docker-compose -f docker-compose.p0-test.yml down -v"
else
  echo "🧹 清理测试环境..."
  docker-compose -f docker-compose.p0-test.yml down -v
  echo "✅ 清理完成"
fi