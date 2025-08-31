#!/usr/bin/env python3
"""
文件上传系统测试脚本
用于验证文件上传功能是否正常工作
"""
import asyncio
import os
import sys
from pathlib import Path
from PIL import Image
import tempfile
import io

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from app.modules.files.services import FileService
from app.core.database import AsyncSessionLocal
from app.core.config import settings


async def create_test_files():
    """创建测试文件"""
    test_files = {}
    
    # 创建测试图片
    img = Image.new('RGB', (800, 600), color='red')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    
    # 保存到临时文件
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        f.write(img_buffer.getvalue())
        test_files['image'] = f.name
    
    # 创建测试文档
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("这是一个测试文档文件\n包含中文内容")
        test_files['document'] = f.name
    
    return test_files


async def test_file_upload():
    """测试文件上传功能"""
    print("🚀 开始测试文件上传系统...")
    
    # 创建测试文件
    test_files = await create_test_files()
    
    async with AsyncSessionLocal() as db:
        file_service = FileService(db)
        
        try:
            # 测试图片上传
            print("\n📸 测试图片上传...")
            with open(test_files['image'], 'rb') as f:
                from fastapi import UploadFile
                
                # 模拟UploadFile对象
                class MockUploadFile:
                    def __init__(self, filename, content):
                        self.filename = filename
                        self.content = content
                        self.size = len(content)
                    
                    async def read(self):
                        return self.content
                    
                    async def seek(self, position):
                        pass
                
                content = f.read()
                mock_file = MockUploadFile("test_image.jpg", content)
                
                # 验证文件
                file_info = await file_service.validate_file(mock_file)
                print(f"✅ 图片验证成功: {file_info['size']} bytes, {file_info['mime_type']}")
                
                # 保存文件
                result = await file_service.save_file(mock_file, "test-user-id", False)
                print(f"✅ 图片上传成功: {result.id}")
                print(f"   - 文件名: {result.filename}")
                print(f"   - 原始文件名: {result.original_filename}")
                print(f"   - 文件大小: {result.file_size} bytes")
                print(f"   - 文件URL: {result.file_url}")
                print(f"   - 缩略图URL: {result.thumbnail_url}")
            
            # 测试文档上传
            print("\n📄 测试文档上传...")
            with open(test_files['document'], 'rb') as f:
                content = f.read()
                mock_file = MockUploadFile("test_document.txt", content)
                
                # 验证文件
                file_info = await file_service.validate_file(mock_file)
                print(f"✅ 文档验证成功: {file_info['size']} bytes, {file_info['mime_type']}")
                
                # 保存文件
                result = await file_service.save_file(mock_file, "test-user-id", False)
                print(f"✅ 文档上传成功: {result.id}")
                print(f"   - 文件名: {result.filename}")
                print(f"   - 文件URL: {result.file_url}")
            
            # 测试文件列表
            print("\n📋 测试文件列表...")
            file_list = await file_service.get_user_files("test-user-id")
            print(f"✅ 获取文件列表成功: 共 {file_list['total']} 个文件")
            
            # 测试大文件验证
            print("\n🚫 测试大文件限制...")
            large_content = b"x" * (settings.MAX_FILE_SIZE + 1)
            large_file = MockUploadFile("large_file.txt", large_content)
            
            try:
                await file_service.validate_file(large_file)
                print("❌ 大文件限制测试失败：应该抛出异常")
            except Exception as e:
                print(f"✅ 大文件限制测试成功: {str(e)}")
            
            # 测试不支持的文件类型
            print("\n🚫 测试不支持的文件类型...")
            unsupported_file = MockUploadFile("test.exe", b"fake executable")
            
            try:
                await file_service.validate_file(unsupported_file)
                print("❌ 文件类型限制测试失败：应该抛出异常")
            except Exception as e:
                print(f"✅ 文件类型限制测试成功: {str(e)}")
            
            print("\n🎉 所有测试完成！文件上传系统工作正常。")
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            # 清理测试文件
            for file_path in test_files.values():
                if os.path.exists(file_path):
                    os.unlink(file_path)


async def check_configuration():
    """检查配置"""
    print("🔧 检查文件上传配置...")
    
    print(f"📁 上传目录: {settings.UPLOAD_DIR}")
    print(f"📏 最大文件大小: {settings.MAX_FILE_SIZE / 1024 / 1024:.1f} MB")
    print(f"📋 支持的文件类型: {', '.join(settings.ALLOWED_FILE_TYPES)}")
    
    # 检查上传目录是否存在
    upload_dir = Path(settings.UPLOAD_DIR)
    if not upload_dir.exists():
        print(f"⚠️  上传目录不存在，正在创建: {upload_dir}")
        upload_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查子目录
    subdirs = ['images', 'documents', 'archives', 'thumbnails', 'temp']
    for subdir in subdirs:
        subdir_path = upload_dir / subdir
        if not subdir_path.exists():
            print(f"📁 创建子目录: {subdir_path}")
            subdir_path.mkdir(exist_ok=True)
        else:
            print(f"✅ 子目录存在: {subdir_path}")
    
    print("✅ 配置检查完成\n")


async def main():
    """主函数"""
    print("=" * 60)
    print("🧪 QA测试知识协作平台 - 文件上传系统测试")
    print("=" * 60)
    
    await check_configuration()
    await test_file_upload()
    
    print("\n" + "=" * 60)
    print("测试完成！")


if __name__ == "__main__":
    asyncio.run(main())