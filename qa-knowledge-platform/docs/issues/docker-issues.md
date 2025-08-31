# Docker相关问题

## Docker Compose版本警告

**问题描述**: 运行docker-compose命令时显示版本属性过时警告

**错误信息**:
```
time="2025-08-30T22:46:45+08:00" level=warning msg="the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion"
```

**解决方案**:
从docker-compose.yml文件中移除version字段：

```yaml
# 修改前
version: '3.8'
services:
  ...

# 修改后  
services:
  ...
```

**根本原因**: Docker Compose新版本不再需要显式指定version字段

**预防措施**: 
- 使用最新的Docker Compose文件格式
- 定期更新Docker Compose配置

---

## 容器重启失败 - 文件挂载类型冲突

**问题描述**: 重启容器时失败，提示文件挂载类型不匹配

**错误信息**:
```
Are you trying to mount a directory onto a file (or vice-versa)? Check if the specified host path exists and is the expected type
```

**解决方案**:
1. 停止所有容器：`docker-compose down`
2. 清理问题文件/目录
3. 重新启动：`docker-compose up -d`

**根本原因**: 主机上的文件类型与容器期望的类型不匹配

**预防措施**: 
- 确保挂载路径的文件类型正确
- 使用完整的停止和启动流程而不是重启