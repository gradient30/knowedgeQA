"""
文件存储服务
支持本地存储和云存储
"""
import os
import aiofiles
from abc import ABC, abstractmethod
from typing import Optional, BinaryIO
from app.core.config import settings


class StorageBackend(ABC):
    """存储后端抽象基类"""
    
    @abstractmethod
    async def save_file(self, file_path: str, content: bytes) -> str:
        """保存文件，返回存储路径"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        pass
    
    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """检查文件是否存在"""
        pass
    
    @abstractmethod
    async def get_file_url(self, file_path: str) -> str:
        """获取文件访问URL"""
        pass


class LocalStorageBackend(StorageBackend):
    """本地文件存储后端"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or settings.UPLOAD_DIR
        os.makedirs(self.base_dir, exist_ok=True)
    
    async def save_file(self, file_path: str, content: bytes) -> str:
        """保存文件到本地"""
        full_path = os.path.join(self.base_dir, file_path)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        async with aiofiles.open(full_path, 'wb') as f:
            await f.write(content)
        
        return full_path
    
    async def delete_file(self, file_path: str) -> bool:
        """删除本地文件"""
        full_path = os.path.join(self.base_dir, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
    
    async def file_exists(self, file_path: str) -> bool:
        """检查本地文件是否存在"""
        full_path = os.path.join(self.base_dir, file_path)
        return os.path.exists(full_path)
    
    async def get_file_url(self, file_path: str) -> str:
        """获取本地文件URL"""
        return f"/api/v1/files/download/{os.path.basename(file_path)}"


class CloudStorageBackend(StorageBackend):
    """云存储后端基类（待实现具体云服务）"""
    
    def __init__(self):
        # 这里可以根据配置初始化不同的云存储客户端
        pass
    
    async def save_file(self, file_path: str, content: bytes) -> str:
        """保存文件到云存储"""
        # TODO: 实现云存储上传逻辑
        raise NotImplementedError("云存储功能待实现")
    
    async def delete_file(self, file_path: str) -> bool:
        """从云存储删除文件"""
        # TODO: 实现云存储删除逻辑
        raise NotImplementedError("云存储功能待实现")
    
    async def file_exists(self, file_path: str) -> bool:
        """检查云存储文件是否存在"""
        # TODO: 实现云存储文件检查逻辑
        raise NotImplementedError("云存储功能待实现")
    
    async def get_file_url(self, file_path: str) -> str:
        """获取云存储文件URL"""
        # TODO: 实现云存储URL生成逻辑
        raise NotImplementedError("云存储功能待实现")


def get_storage_backend() -> StorageBackend:
    """获取存储后端实例"""
    if settings.USE_CLOUD_STORAGE:
        return CloudStorageBackend()
    else:
        return LocalStorageBackend()