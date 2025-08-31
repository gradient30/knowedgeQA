#!/bin/bash

# P0问题验证脚本
# 用于在Docker环境中验证导航栏功能

set -e

echo "🔍 开始P0问题验证..."

# 清理之前的容器和卷
echo "📦 清理之前的测试环境..."
docker-compose -f docker-compose.p0-test.yml down -v --remove-orphans

# 构建并启动服务
echo "🚀 启动P0测试环境..."
docker-compose -f docker-compose.p0-test.yml up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose -f docker-compose.p0-test.yml ps

# 检查前端服务健康状态
echo "🏥 检查前端服务健康状态..."
for i in {1..10}; do
  if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ 前端服务已启动"
    break
  else
    echo "⏳ 等待前端服务启动... ($i/10)"
    sleep 5
  fi
done

# 检查后端服务健康状态
echo "🏥 检查后端服务健康状态..."
for i in {1..10}; do
  if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端服务已启动"
    break
  else
    echo "⏳ 等待后端服务启动... ($i/10)"
    sleep 5
  fi
done

# 显示前端日志
echo "📋 前端服务日志:"
docker-compose -f docker-compose.p0-test.yml logs --tail=20 frontend-p0

# 显示后端日志
echo "📋 后端服务日志:"
docker-compose -f docker-compose.p0-test.yml logs --tail=20 backend-p0

echo "🎯 P0测试环境已启动，请访问 http://localhost:3000 进行手动验证"
echo "📝 验证清单:"
echo "   1. 页面是否正常加载（不显示Next.js内部代码）"
echo "   2. 测试导航栏是否显示"
echo "   3. 登录功能是否正常"
echo "   4. 登录后导航栏是否包含用户菜单"
echo ""
echo "🛑 测试完成后运行: docker-compose -f docker-compose.p0-test.yml down -v"