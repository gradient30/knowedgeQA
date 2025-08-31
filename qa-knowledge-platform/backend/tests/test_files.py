"""
文件上传系统测试
"""
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from PIL import Image
import io

from app.main import app
from app.core.config import settings


client = TestClient(app)


class TestFileUpload:
    """文件上传测试类"""
    
    def create_test_image(self, width=800, height=600, format='JPEG'):
        """创建测试图片"""
        img = Image.new('RGB', (width, height), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format)
        img_bytes.seek(0)
        return img_bytes
    
    def create_test_file(self, content="Test file content", filename="test.txt"):
        """创建测试文件"""
        file_bytes = io.BytesIO(content.encode())
        file_bytes.name = filename
        return file_bytes
    
    def test_upload_image_success(self):
        """测试图片上传成功"""
        # 创建测试图片
        test_image = self.create_test_image()
        
        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "文件上传成功"
        assert data["file_info"] is not None
        assert data["file_info"]["file_extension"] == ".jpg"
        assert data["file_info"]["thumbnail_url"] is not None
    
    def test_upload_document_success(self):
        """测试文档上传成功"""
        test_file = self.create_test_file("Test document content", "test.txt")
        
        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("test.txt", test_file, "text/plain")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["file_info"]["file_extension"] == ".txt"
        assert data["file_info"]["thumbnail_url"] is None  # 文档不生成缩略图
    
    def test_upload_large_file_failure(self):
        """测试大文件上传失败"""
        # 创建超过限制的大文件
        large_content = "x" * (settings.MAX_FILE_SIZE + 1)
        large_file = io.BytesIO(large_content.encode())
        
        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("large.txt", large_file, "text/plain")}
        )
        
        assert response.status_code == 400
        assert "文件大小超过限制" in response.json()["detail"]
    
    def test_upload_unsupported_file_type(self):
        """测试不支持的文件类型"""
        test_file = self.create_test_file("Executable content", "test.exe")
        
        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("test.exe", test_file, "application/octet-stream")}
        )
        
        assert response.status_code == 400
        assert "不支持的文件类型" in response.json()["detail"]
    
    def test_upload_multiple_files(self):
        """测试批量文件上传"""
        files = [
            ("files", ("test1.txt", self.create_test_file("Content 1", "test1.txt"), "text/plain")),
            ("files", ("test2.jpg", self.create_test_image(), "image/jpeg"))
        ]
        
        response = client.post("/api/v1/files/upload-multiple", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(item["success"] for item in data)
    
    def test_image_compression(self):
        """测试图片压缩功能"""
        # 创建大尺寸图片
        large_image = self.create_test_image(width=3000, height=2000)
        
        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("large.jpg", large_image, "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证图片被压缩
        file_info = data["file_info"]
        assert file_info is not None
        # 可以通过检查文件大小或元数据来验证压缩
    
    def test_download_file(self):
        """测试文件下载"""
        # 先上传文件
        test_file = self.create_test_file("Download test content", "download_test.txt")
        upload_response = client.post(
            "/api/v1/files/upload",
            files={"file": ("download_test.txt", test_file, "text/plain")}
        )
        
        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_info"]["id"]
        
        # 下载文件
        download_response = client.get(f"/api/v1/files/download/{file_id}")
        assert download_response.status_code == 200
        assert download_response.content == b"Download test content"
    
    def test_download_nonexistent_file(self):
        """测试下载不存在的文件"""
        response = client.get("/api/v1/files/download/nonexistent-id")
        assert response.status_code == 404
        assert "文件不存在" in response.json()["detail"]
    
    def test_get_file_info(self):
        """测试获取文件信息"""
        # 先上传文件
        test_file = self.create_test_file("Info test content", "info_test.txt")
        upload_response = client.post(
            "/api/v1/files/upload",
            files={"file": ("info_test.txt", test_file, "text/plain")}
        )
        
        file_id = upload_response.json()["file_info"]["id"]
        
        # 获取文件信息
        info_response = client.get(f"/api/v1/files/info/{file_id}")
        assert info_response.status_code == 200
        
        info_data = info_response.json()
        assert info_data["original_name"] == "info_test.txt"
        assert info_data["file_size"] > 0
        assert info_data["mime_type"] == "text/plain"
    
    def test_list_user_files(self):
        """测试获取用户文件列表"""
        # 上传几个文件
        for i in range(3):
            test_file = self.create_test_file(f"Content {i}", f"test{i}.txt")
            client.post(
                "/api/v1/files/upload",
                files={"file": (f"test{i}.txt", test_file, "text/plain")}
            )
        
        # 获取文件列表
        response = client.get("/api/v1/files/list")
        assert response.status_code == 200
        
        data = response.json()
        assert "files" in data
        assert "total" in data
        assert data["total"] >= 3
    
    def test_delete_file(self):
        """测试删除文件"""
        # 先上传文件
        test_file = self.create_test_file("Delete test content", "delete_test.txt")
        upload_response = client.post(
            "/api/v1/files/upload",
            files={"file": ("delete_test.txt", test_file, "text/plain")}
        )
        
        file_id = upload_response.json()["file_info"]["id"]
        
        # 删除文件
        delete_response = client.delete(f"/api/v1/files/{file_id}")
        assert delete_response.status_code == 200
        assert "文件删除成功" in delete_response.json()["message"]
        
        # 验证文件已被删除
        download_response = client.get(f"/api/v1/files/download/{file_id}")
        assert download_response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__])