# 技术栈与构建系统

## QA测试知识协作平台 - 核心技术选型

### 前端技术栈 (已确定)
- **框架**: Next.js 14 (App Router) - 内置SSR/SSG，开发效率高
- **UI组件库**: Ant Design 5.x - 中文友好，快速构建管理界面
- **样式方案**: Tailwind CSS + Ant Design - 快速样式开发
- **状态管理**: Zustand - 轻量级，TypeScript友好
- **Markdown编辑器**: @uiw/react-md-editor - 支持预览，易于集成
- **开发语言**: TypeScript 5.x - 类型安全，提升开发质量

### 后端技术栈 (已确定)
- **API框架**: FastAPI 0.104+ - 高性能异步，自动API文档
- **数据库**: PostgreSQL 15+ - 支持JSON字段，内置全文搜索
- **ORM**: SQLAlchemy 2.0 + Alembic - 异步操作，迁移管理完善
- **认证系统**: FastAPI-Users - 开箱即用的用户管理
- **任务队列**: Celery + Redis - 处理爬虫和邮件等异步任务
- **爬虫引擎**: httpx + BeautifulSoup4 - 异步HTTP，HTML解析
- **搜索引擎**: PostgreSQL Full-Text Search - MVP阶段避免ES复杂性

### 开发工具链 (必须遵循)
- **包管理**: pnpm (Node.js), Poetry (Python)
- **代码质量**: ESLint, Prettier (前端), Black, isort (后端)
- **测试框架**: Jest + React Testing Library, pytest, Playwright
- **容器化**: Docker + Docker Compose
- **版本控制**: Git + 规范化提交信息

### 关键开发命令

#### 项目初始化和环境管理
```bash
# 项目初始化 (仅首次)
./scripts/project-manager.sh setup

# 启动开发环境
./scripts/project-manager.sh start --env dev

# 停止所有服务
./scripts/project-manager.sh stop --env dev

# 查看服务状态
./scripts/project-manager.sh status --env dev
```

#### 开发和测试
```bash
# 前端开发 (在frontend目录)
pnpm dev                    # 启动开发服务器
pnpm build                  # 构建生产版本
pnpm test                   # 运行单元测试
pnpm test -- --coverage    # 运行测试并生成覆盖率报告

# 后端开发 (在backend目录)
poetry run uvicorn app.main:app --reload  # 启动开发服务器
poetry run pytest tests/ --cov=app        # 运行测试和覆盖率
poetry run alembic upgrade head           # 数据库迁移
poetry run python scripts/init_db.py      # 初始化数据库

# E2E测试
npx playwright test         # 运行端到端测试
npx playwright test --ui    # 交互式测试界面
```

#### 代码质量检查
```bash
# 前端代码质量
pnpm lint                   # ESLint检查
pnpm lint:fix              # 自动修复ESLint问题
pnpm format                # Prettier格式化

# 后端代码质量
poetry run black .         # Python代码格式化
poetry run isort .         # Python导入排序
poetry run mypy app/       # 类型检查
```

#### 部署和运维
```bash
# 构建和部署
./scripts/project-manager.sh build --env staging
./scripts/project-manager.sh deploy --env staging

# 数据管理
./scripts/project-manager.sh backup --env prod
./scripts/project-manager.sh migrate --env staging

# 监控和日志
./scripts/project-manager.sh health --env prod
./scripts/project-manager.sh logs --env prod backend
./scripts/monitor.sh system prod
```

## 环境配置标准

### 开发环境 (dev)
- **目标**: 本地开发，快速迭代
- **特点**: 热重载，详细日志，测试数据
- **数据库**: 本地PostgreSQL容器
- **Redis**: 本地Redis容器
- **文件存储**: 本地文件系统

### 预发布环境 (staging)
- **目标**: 生产环境验证，用户验收测试
- **特点**: 生产级配置，性能监控
- **数据库**: 独立PostgreSQL实例
- **Redis**: 独立Redis实例
- **文件存储**: 云存储服务

### 生产环境 (prod)
- **目标**: 正式服务，高可用性
- **特点**: 负载均衡，自动备份，监控告警
- **数据库**: 高可用PostgreSQL集群
- **Redis**: Redis集群
- **文件存储**: CDN + 云存储

## 性能和质量要求

### QA平台性能指标
- **页面加载时间**: <2秒 (首屏)
- **并发用户支持**: 100用户 (MVP阶段)
- **数据库查询**: <100ms (常用查询)
- **文件上传**: 支持10MB以内文件
- **系统可用性**: 99% (MVP阶段)

### 代码质量标准
- **测试覆盖率**: >80% (单元测试)
- **代码复杂度**: 圈复杂度<10
- **类型覆盖**: TypeScript严格模式
- **安全扫描**: 无高危漏洞
- **性能预算**: Bundle大小<1MB

### 开发效率指标
- **构建时间**: <3分钟 (完整构建)
- **热重载**: <2秒 (开发环境)
- **测试执行**: <5分钟 (完整测试套件)
- **部署时间**: <10分钟 (自动化部署)

## 技术债务管理

### 已知技术选择权衡
- **搜索引擎**: 使用PG全文搜索而非Elasticsearch (MVP简化)
- **文件存储**: 先本地存储，后期迁移云存储
- **缓存策略**: Redis基础缓存，暂不引入复杂缓存层
- **监控系统**: 基础健康检查，完整监控在V2.0

### 技术升级路径
- **V1.0 → V1.1**: 引入Elasticsearch提升搜索体验
- **V1.1 → V2.0**: 微服务架构，支持500+用户
- **V2.0+**: AI辅助功能，智能推荐系统

## 特殊技术要求

### QA测试领域特定需求
- **测试用例编辑器**: 支持步骤化编辑，预期结果管理
- **Bug报告组件**: 结构化Bug信息，附件上传
- **工具评分系统**: 5星评分，优缺点对比
- **爬虫系统**: 测试行业网站内容抓取，关键词过滤
- **权限控制**: 测试团队层级权限，内容可见性控制

### 中文环境优化
- **字体优化**: 中文字体渲染优化
- **输入法支持**: Markdown编辑器中文输入优化
- **搜索优化**: 中文分词，拼音搜索支持
- **时区处理**: 东八区时间显示
- **本地化**: 错误信息、提示文本中文化

## 项目修复准则 (技术负责人必须遵循)

### 核心修复准则
1. **原始需求导向**: 所有修复必须基于qa-knowledge-platform目录内的原始需求，不得偏离主项目范围
2. **最小化MVP规则**: 严格遵循最小可行产品原则，禁止过度设计和功能蔓延
3. **6A+RIPPER标准**: 作为技术负责人及领域专家，必须按照6A+RIPPER规则进行问题确认和修复，确保质量和安全

### 修复执行规范
- **需求追溯**: 每个修复都必须明确对应原始需求编号
- **范围控制**: 严禁实现超出当前阶段的功能
- **确认机制**: 定位问题和确认修复方案后必须与产品经理确认
- **中文交流**: 所有对话和文档使用中文，确保团队沟通无障碍

### 质量保证要求
- **Architecture (架构)**: 保持架构简洁，避免过度工程化
- **API (接口)**: 确保接口稳定可用
- **Authentication (认证)**: 认证功能安全可靠
- **Authorization (授权)**: 权限控制准确
- **Audit (审计)**: 操作可追溯
- **Availability (可用性)**: 系统稳定运行
- **Reliability (可靠性)**: 功能可靠
- **Integration (集成)**: 组件集成无缝
- **Performance (性能)**: 满足性能要求
- **Privacy (隐私)**: 保护用户隐私
- **Error handling (错误处理)**: 错误处理完善
- **Resilience (弹性)**: 系统具备容错能力