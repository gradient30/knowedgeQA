# 前端开发问题

## autoprefixer模块缺失导致编译失败 {#frontend-autoprefixer-issue}

**问题描述**: Next.js前端编译失败，提示找不到autoprefixer模块

**错误信息**:
```
Error: Cannot find module 'autoprefixer'
An error occurred in `next/font`.
```

**解决方案**:
1. 重新安装前端依赖：
```bash
docker-compose -f docker-compose.dev.yml exec frontend pnpm install
```

2. 或者重新构建前端容器：
```bash
docker-compose -f docker-compose.dev.yml build frontend
```

**根本原因**: 
- Docker容器中的node_modules可能不完整
- pnpm缓存问题导致某些依赖未正确安装

**预防措施**: 
- 确保package.json中包含所有必要的依赖
- 定期清理和重建Docker容器
- 使用.dockerignore避免本地node_modules干扰

**相关链接**: 
- [Next.js CSS配置](https://nextjs.org/docs/app/building-your-application/styling/css-modules)
- [PostCSS autoprefixer](https://github.com/postcss/autoprefixer)

---

## Next.js配置警告 - appDir选项废弃

**问题描述**: Next.js启动时显示配置警告，提示appDir选项无效

**错误信息**:
```
⚠ Invalid next.config.js options detected:
⚠     Unrecognized key(s) in object: 'appDir' at "experimental"
```

**解决方案**:
移除next.config.js中的过时配置选项：

```javascript
// 修改前
module.exports = {
  experimental: {
    appDir: true  // 移除此选项
  }
}

// 修改后
module.exports = {
  // App Router在Next.js 13.4+中已默认启用
}
```

**根本原因**: Next.js 13.4+版本中App Router已成为稳定功能，不再需要experimental配置

**预防措施**: 
- 定期更新Next.js版本并检查配置变更
- 参考官方迁移指南更新配置
- 使用TypeScript配置获得更好的类型检查

---

## Playwright浏览器版本兼容性问题 {#playwright-browser-compatibility}

**问题描述**: MCP Playwright服务无法启动浏览器，提示可执行文件不存在

**错误信息**:
```
Failed to initialize browser: browserType.launch: Executable doesn't exist at C:\Users\gradi\AppData\Local\ms-playwright\chromium-1179\chrome-win\chrome.exe
```

**解决方案**:
复制现有浏览器目录到MCP期望的版本路径：

```powershell
# 检查当前安装的浏览器版本
Get-ChildItem "C:\Users\$env:USERNAME\AppData\Local\ms-playwright" -Name

# 复制到MCP期望的版本 (根据错误信息调整版本号)
Copy-Item -Path "C:\Users\$env:USERNAME\AppData\Local\ms-playwright\chromium-1187" -Destination "C:\Users\$env:USERNAME\AppData\Local\ms-playwright\chromium-1179" -Recurse

# 验证修复
Test-Path "C:\Users\$env:USERNAME\AppData\Local\ms-playwright\chromium-1179\chrome-win\chrome.exe"
```

**根本原因**: 
- MCP Playwright服务期望特定版本的浏览器
- 本地安装的Playwright浏览器版本不匹配
- 浏览器可执行文件路径不正确

**验证方法**:
```javascript
// 测试UI自动化是否正常工作
await mcp_playwright_playwright_navigate({
  url: "http://localhost:3000",
  width: 1280,
  height: 720
});
```

**预防措施**: 
- 在项目中锁定Playwright版本
- 创建自动修复脚本
- 定期验证浏览器兼容性
- 记录工作的浏览器版本配置

**相关链接**: 
- [完整解决方案文档](./playwright-browser-compatibility-issue.md)
- [Playwright官方文档](https://playwright.dev/docs/browsers)