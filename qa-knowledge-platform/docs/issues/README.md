# 问题解决方案文档

本目录记录项目开发过程中遇到的问题及其解决方案，便于后续参考和团队知识共享。

## 文档结构

- `setup-issues.md` - 项目初始化和环境搭建问题
- `docker-issues.md` - Docker相关问题
- `frontend-issues.md` - 前端开发问题
- `backend-issues.md` - 后端开发问题
- `database-issues.md` - 数据库相关问题

## 问题记录格式

每个问题应包含以下信息：

```markdown
## 问题标题

**问题描述**: 详细描述遇到的问题
**错误信息**: 完整的错误日志
**解决方案**: 具体的解决步骤
**根本原因**: 问题产生的根本原因
**预防措施**: 如何避免类似问题
**相关链接**: 参考文档或资源
```

## 快速索引

- [Docker构建失败 - Poetry参数问题](#docker-poetry-issue)
- [SQLAlchemy metadata冲突](#sqlalchemy-metadata-issue)
- [前端autoprefixer缺失](#frontend-autoprefixer-issue)