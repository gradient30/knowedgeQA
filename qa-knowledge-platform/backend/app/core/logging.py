"""
日志配置
"""
import logging
import logging.config
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from app.core.config import settings


class TimestampFormatter(logging.Formatter):
    """自定义时间戳格式化器"""
    
    def format(self, record):
        # 添加时间戳
        record.timestamp = datetime.utcnow().isoformat()
        return super().format(record)


def setup_logging() -> None:
    """设置日志配置"""
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 日志配置
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": TimestampFormatter,
                "format": "[{timestamp}] {levelname} {name}: {message}",
                "style": "{",
            },
            "detailed": {
                "()": TimestampFormatter,
                "format": "[{timestamp}] {levelname} {name} ({filename}:{lineno}): {message}",
                "style": "{",
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(timestamp)s %(levelname)s %(name)s %(filename)s %(lineno)d %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": log_dir / "app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": log_dir / "error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "app": {
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False,
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"],
        },
    }
    
    # 应用日志配置
    logging.config.dictConfig(logging_config)
    
    # 设置第三方库日志级别
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    return logging.getLogger(f"app.{name}")


# 创建应用日志记录器
app_logger = get_logger("main")
auth_logger = get_logger("auth")
api_logger = get_logger("api")
db_logger = get_logger("database")
task_logger = get_logger("tasks")