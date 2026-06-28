# QA 知识协作平台仓库

本仓库包含 `qa-knowledge-platform` 项目：一个面向 SaaS 与游戏质量工程团队的全栈 QA 知识协作平台。

常用入口：

- [项目 README](qa-knowledge-platform/README.md)
- [开发环境部署](qa-knowledge-platform/docs/deployment/dev.md)
- [生产环境部署](qa-knowledge-platform/docs/deployment/prod.md)
- [系统架构](qa-knowledge-platform/docs/architecture.md)
- [运维说明](qa-knowledge-platform/docs/operations.md)
- [安全说明](qa-knowledge-platform/docs/security.md)
- [技术路线图](qa-knowledge-platform/docs/technical-roadmap.md)
- [贡献者指南](AGENTS.md)

快速启动：

```powershell
cd qa-knowledge-platform
.\scripts\project-manager.ps1 setup
.\scripts\project-manager.ps1 start -Env dev
.\scripts\project-manager.ps1 test
```

生产部署路径已经文档化，并由 `qa-knowledge-platform/` 下提交的 Docker 部署文件支撑。
