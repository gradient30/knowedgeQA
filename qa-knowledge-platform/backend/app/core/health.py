"""
健康检查模块
"""
import asyncio
import time
from datetime import datetime
from typing import Dict, Any

import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_session
from app.core.logging import get_logger

logger = get_logger("health")


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.redis_client = None
    
    async def check_database(self) -> Dict[str, Any]:
        """检查数据库连接"""
        try:
            start_time = time.time()
            
            # 获取数据库会话
            async for session in get_async_session():
                # 执行简单查询
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                
                response_time = time.time() - start_time
                
                return {
                    "status": "healthy",
                    "response_time": f"{response_time:.3f}s",
                    "timestamp": datetime.utcnow().isoformat(),
                }
                
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    async def check_redis(self) -> Dict[str, Any]:
        """检查Redis连接"""
        try:
            start_time = time.time()
            
            # 创建Redis客户端
            if not self.redis_client:
                self.redis_client = redis.from_url(settings.REDIS_URL)
            
            # 执行ping命令
            await self.redis_client.ping()
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": f"{response_time:.3f}s",
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    async def check_celery(self) -> Dict[str, Any]:
        """检查Celery任务队列"""
        try:
            from app.core.celery_app import celery_app
            
            # 检查Celery状态
            inspect = celery_app.control.inspect()
            stats = inspect.stats()
            
            if stats:
                return {
                    "status": "healthy",
                    "workers": len(stats),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "No active workers",
                    "timestamp": datetime.utcnow().isoformat(),
                }
                
        except Exception as e:
            logger.error(f"Celery health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    async def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        import psutil
        import platform
        
        try:
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent,
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent,
                },
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"System info check failed: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """综合健康检查"""
        start_time = time.time()
        
        # 并发执行所有检查
        database_check, redis_check, celery_check, system_info = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_celery(),
            self.get_system_info(),
            return_exceptions=True
        )
        
        total_time = time.time() - start_time
        
        # 判断整体健康状态
        overall_status = "healthy"
        if (isinstance(database_check, dict) and database_check.get("status") != "healthy" or
            isinstance(redis_check, dict) and redis_check.get("status") != "healthy"):
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "total_check_time": f"{total_time:.3f}s",
            "checks": {
                "database": database_check if isinstance(database_check, dict) else {"error": str(database_check)},
                "redis": redis_check if isinstance(redis_check, dict) else {"error": str(redis_check)},
                "celery": celery_check if isinstance(celery_check, dict) else {"error": str(celery_check)},
            },
            "system": system_info if isinstance(system_info, dict) else {"error": str(system_info)},
        }


# 全局健康检查器实例
health_checker = HealthChecker()