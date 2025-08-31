from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables
from app.core.logging import setup_logging, app_logger
from app.core.exceptions import (
    QAKnowledgeException,
    qa_knowledge_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from app.core.middleware import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
)
from app.api.v1.router import api_router

# 设置日志
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    app_logger.info("Starting QA Knowledge Platform API...")
    await create_tables()
    app_logger.info("Database tables created successfully")
    yield
    # 关闭时的清理工作
    app_logger.info("Shutting down QA Knowledge Platform API...")


app = FastAPI(
    title="QA测试知识协作平台 API",
    description="专为测试团队打造的知识分享与协作平台后端API",
    version="1.0.0",
    lifespan=lifespan,
)

# 添加中间件
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(QAKnowledgeException, qa_knowledge_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 注册API路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "QA测试知识协作平台 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """简单健康检查"""
    return {"status": "healthy", "service": "qa-knowledge-platform-backend"}


@app.get("/health/detailed")
async def detailed_health_check():
    """详细健康检查"""
    from app.core.health import health_checker
    return await health_checker.comprehensive_health_check()