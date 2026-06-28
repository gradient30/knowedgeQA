# QA Knowledge Platform Repository

This repository hosts `qa-knowledge-platform`, a full-stack QA knowledge collaboration platform for SaaS and game quality engineering teams.

Start here:

- [Project README](qa-knowledge-platform/README.md)
- [Development deployment](qa-knowledge-platform/docs/deployment/dev.md)
- [Production deployment](qa-knowledge-platform/docs/deployment/prod.md)
- [Architecture](qa-knowledge-platform/docs/architecture.md)
- [Operations](qa-knowledge-platform/docs/operations.md)
- [Security](qa-knowledge-platform/docs/security.md)
- [Technical roadmap](qa-knowledge-platform/docs/technical-roadmap.md)
- [Contributor guide](AGENTS.md)

Quick start:

```powershell
cd qa-knowledge-platform
.\scripts\project-manager.ps1 setup
.\scripts\project-manager.ps1 start -Env dev
.\scripts\project-manager.ps1 test
```

The production deployment path is documented and backed by committed Docker artifacts under `qa-knowledge-platform/`.
