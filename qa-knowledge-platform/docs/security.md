# 安全说明

只有在密钥不进入 Git、并且部署使用环境隔离配置时，本仓库才适合作为公共仓库维护。

## 密钥

禁止提交：

- `.env`
- `.env.prod`
- SMTP 密码
- JWT `SECRET_KEY`
- 生产数据库或 Redis 密码
- 云存储凭据
- TLS 私钥

`.env.prod.example` 只能作为占位模板使用。

## 认证

后端使用 JWT 认证和基于角色的 API 流程。邮箱验证、密码重置和邮箱变更使用持久化的一次性 token。无效或复用的 token 会被后端测试和运行态验收拦截。

生产环境必须：

- 设置强随机 `SECRET_KEY`。
- 根据业务风险配置 `ACCESS_TOKEN_EXPIRE_MINUTES`。
- 将 `ALLOWED_HOSTS` 限制为可信前端来源。
- 通过 HTTPS 提供前端和 API。

## 授权

敏感流程需要认证用户和角色检查：

- 私有文件下载和删除。
- 管理员用户治理。
- 通知管理。
- 审核和发布操作。
- 审计日志访问。

新增 API 时，应在路由或服务入口附近放置授权检查，并补充禁止访问测试。

## 文件上传

当前上传控制包括文件大小限制、扩展名白名单、认证上传/列表/下载/删除，以及私有文件的所有者/管理员访问控制。生产部署还应补充：

- 上传文件病毒或恶意内容扫描。
- 多节点部署所需的对象存储。
- CDN 规则不得绕过后端私有文件授权。

## 网络与运行时

推荐生产基线：

- 仅通过反向代理或负载均衡器提供 HTTPS。
- PostgreSQL 和 Redis 不暴露到公网。
- Redis 启用密码。
- Docker 卷定期备份。
- 日志保留并限制访问权限。
- 定期复核管理员账号。

## 依赖与代码检查

发布前运行标准门禁：

```bash
bash ./scripts/project-manager.sh test
```

或：

```powershell
.\scripts\project-manager.ps1 test
```

后端定向检查：

```bash
cd backend
poetry run pytest tests/ --cov=app
```

前端定向检查：

```bash
cd frontend
pnpm type-check
pnpm lint
pnpm build
```

## 漏洞披露

修复可用前，不要在公开 issue 中披露漏洞细节。敏感发现应在私有 issue 跟踪器或安全公告流程中处理。
