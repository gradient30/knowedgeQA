"""
全局异常处理
"""
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union

logger = logging.getLogger(__name__)


class QAKnowledgeException(Exception):
    """平台自定义异常基类"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(QAKnowledgeException):
    """认证错误"""
    def __init__(self, message: str = "认证失败", details: dict = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)


class AuthorizationError(QAKnowledgeException):
    """授权错误"""
    def __init__(self, message: str = "权限不足", details: dict = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)


class ValidationError(QAKnowledgeException):
    """验证错误"""
    def __init__(self, message: str = "数据验证失败", details: dict = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)


class NotFoundError(QAKnowledgeException):
    """资源不存在错误"""
    def __init__(self, message: str = "资源不存在", details: dict = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class ConflictError(QAKnowledgeException):
    """冲突错误"""
    def __init__(self, message: str = "资源冲突", details: dict = None):
        super().__init__(message, status.HTTP_409_CONFLICT, details)


async def qa_knowledge_exception_handler(request: Request, exc: QAKnowledgeException):
    """自定义异常处理器"""
    logger.error(f"QA Knowledge Exception: {exc.message}", extra={
        "status_code": exc.status_code,
        "details": exc.details,
        "path": request.url.path,
        "method": request.method
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path,
            "timestamp": str(request.state.timestamp) if hasattr(request.state, 'timestamp') else None
        }
    )


async def http_exception_handler(request: Request, exc: Union[HTTPException, StarletteHTTPException]):
    """HTTP异常处理器"""
    logger.warning(f"HTTP Exception: {exc.detail}", extra={
        "status_code": exc.status_code,
        "path": request.url.path,
        "method": request.method
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "path": request.url.path,
            "timestamp": str(request.state.timestamp) if hasattr(request.state, 'timestamp') else None
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    logger.warning(f"Validation Error: {exc.errors()}", extra={
        "path": request.url.path,
        "method": request.method,
        "errors": exc.errors()
    })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "请求数据验证失败",
            "details": exc.errors(),
            "path": request.url.path,
            "timestamp": str(request.state.timestamp) if hasattr(request.state, 'timestamp') else None
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"Unhandled Exception: {str(exc)}", extra={
        "path": request.url.path,
        "method": request.method,
        "exception_type": type(exc).__name__
    }, exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "服务器内部错误",
            "path": request.url.path,
            "timestamp": str(request.state.timestamp) if hasattr(request.state, 'timestamp') else None
        }
    )