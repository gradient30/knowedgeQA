# 项目初始化和环境搭建问题

## Docker构建失败 - Poetry --no-dev参数废弃 {#docker-poetry-issue}

**问题描述**: Docker构建后端服务时失败，提示Poetry的`--no-dev`参数不存在

**错误信息**:
```
The option "--no-dev" does not exist
```

**解决方案**:
1. 修改Dockerfile.dev中的Poetry安装命令
2. 使用`--no-root`参数先安装依赖，再复制代码后安装项目本身

```dockerfile
# 修改前
RUN poetry install --no-dev

# 修改后
RUN poetry install --no-root
COPY . .
RUN poetry install
```

**根本原因**: Poetry新版本废弃了`--no-dev`参数，改用`--without=dev`或`--only=main`

**预防措施**: 
- 定期更新文档中的命令参数
- 使用固定版本的Poetry避免破坏性变更

**相关链接**: [Poetry文档 - 依赖管理](https://python-poetry.org/docs/cli/#install)

---

## 缺少README.md文件导致Poetry安装失败

**问题描述**: Poetry尝试安装当前项目时失败，提示README.md文件不存在

**错误信息**:
```
Error: The current project could not be installed: Readme path `/app/README.md` does not exist.
```

**解决方案**:
1. 在backend目录创建README.md文件
2. 或在pyproject.toml中配置`packages`字段

**根本原因**: Poetry需要README.md文件来安装当前项目包

**预防措施**: 
- 项目初始化时确保创建必要的文档文件
- 在pyproject.toml中正确配置包信息

---

## Docker初始化脚本路径错误

**问题描述**: PostgreSQL容器启动时无法读取初始化脚本，提示"Is a directory"

**错误信息**:
```
psql:/docker-entrypoint-initdb.d/init.sql: error: could not read from input file: Is a directory
```

**解决方案**:
1. 删除错误的init.sql目录
2. 创建正确的init.sql文件

```bash
rmdir backend/scripts/init.sql
# 创建正确的SQL文件
```

**根本原因**: 意外创建了同名目录而不是文件

**预防措施**: 
- 仔细检查文件类型
- 使用版本控制跟踪文件变更