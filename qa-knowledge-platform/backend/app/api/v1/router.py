from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.modules.users.api import router as users_router
from app.modules.knowledge.api import router as knowledge_router
from app.modules.tools.api import router as tools_router
from app.modules.news.api import router as news_router
from app.modules.files.api import router as files_router
from app.modules.notifications.api import router as notifications_router

api_router = APIRouter()

# 注册认证路由 (无需认证的公开接口)
api_router.include_router(auth_router, prefix="/auth", tags=["用户认证"])

# 注册各模块路由 (需要认证的接口)
api_router.include_router(users_router, prefix="/users", tags=["用户管理"])
api_router.include_router(knowledge_router, prefix="/knowledge", tags=["知识库"])
api_router.include_router(tools_router, prefix="/tools", tags=["工具库"])
api_router.include_router(news_router, prefix="/news", tags=["资讯"])
api_router.include_router(files_router, prefix="/files", tags=["文件管理"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["邮件通知"])