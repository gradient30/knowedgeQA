# QA测试知识协作平台 - 后端API

专为测试团队打造的知识分享与协作平台后端服务。

## 技术栈

- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 15+ with SQLAlchemy 2.0
- **认证**: FastAPI-Users
- **任务队列**: Celery + Redis
- **开发语言**: Python 3.11+

## 快速开始

### 开发环境

```bash
# 安装依赖
poetry install

# 启动开发服务器
uvicorn app.main:app --reload

# 运行测试
pytest tests/ --cov=app
```

### API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
app/
├── core/           # 核心配置和工具
├── modules/        # 业务模块
├── api/           # API路由
└── main.py        # 应用入口
```

## 环境变量

参考 `.env.dev` 文件配置开发环境变量。