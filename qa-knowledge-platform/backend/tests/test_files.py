"""
文件上传系统测试
"""
import io

import pytest
from httpx import AsyncClient
from PIL import Image

from app.core.config import settings


@pytest.fixture(autouse=True)
def isolated_upload_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path / "uploads"))


class TestFileUpload:
    """文件上传测试类"""

    async def create_and_login_user(
        self,
        client: AsyncClient,
        username: str = "fileuser",
        email: str = "fileuser@example.com",
        role: str = "member",
    ) -> dict:
        user_data = {
            "username": username,
            "email": email,
            "password": "testpassword123",
            "role": role,
        }
        register_response = await client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "testpassword123"},
        )
        assert login_response.status_code == 200
        return {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    def create_test_image(self, width=800, height=600, format="JPEG"):
        """创建测试图片"""
        img = Image.new("RGB", (width, height), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format)
        img_bytes.seek(0)
        return img_bytes

    def create_test_file(self, content="Test file content", filename="test.txt"):
        """创建测试文件"""
        file_bytes = io.BytesIO(content.encode())
        file_bytes.name = filename
        return file_bytes

    @pytest.mark.asyncio
    async def test_upload_requires_authenticated_user(self, client: AsyncClient):
        """匿名用户不能上传证据文件"""
        response = await client.post(
            "/api/v1/files/upload",
            files={"file": ("test.txt", self.create_test_file(), "text/plain")},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_upload_image_success(self, client: AsyncClient):
        """测试图片上传成功"""
        headers = await self.create_and_login_user(client)
        response = await client.post(
            "/api/v1/files/upload",
            files={"file": ("test.jpg", self.create_test_image(), "image/jpeg")},
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "文件上传成功"
        assert data["file_info"] is not None
        assert data["file_info"]["file_extension"] == ".jpg"
        assert data["file_info"]["thumbnail_url"] is not None

    @pytest.mark.asyncio
    async def test_upload_document_success(self, client: AsyncClient):
        """测试文档上传成功"""
        headers = await self.create_and_login_user(client)
        response = await client.post(
            "/api/v1/files/upload",
            files={
                "file": (
                    "test.txt",
                    self.create_test_file("Test document content", "test.txt"),
                    "text/plain",
                )
            },
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["file_info"]["file_extension"] == ".txt"
        assert data["file_info"]["thumbnail_url"] is None

    @pytest.mark.asyncio
    async def test_upload_large_file_failure(self, client: AsyncClient):
        """测试大文件上传失败"""
        headers = await self.create_and_login_user(client)
        large_content = "x" * (settings.MAX_FILE_SIZE + 1)
        large_file = io.BytesIO(large_content.encode())

        response = await client.post(
            "/api/v1/files/upload",
            files={"file": ("large.txt", large_file, "text/plain")},
            headers=headers,
        )

        assert response.status_code == 400
        assert "文件大小超过限制" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_unsupported_file_type(self, client: AsyncClient):
        """测试不支持的文件类型"""
        headers = await self.create_and_login_user(client)
        response = await client.post(
            "/api/v1/files/upload",
            files={
                "file": (
                    "test.exe",
                    self.create_test_file("Executable content", "test.exe"),
                    "application/octet-stream",
                )
            },
            headers=headers,
        )

        assert response.status_code == 400
        assert "不支持的文件类型" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_multiple_files(self, client: AsyncClient):
        """测试批量文件上传"""
        headers = await self.create_and_login_user(client)
        files = [
            (
                "files",
                (
                    "test1.txt",
                    self.create_test_file("Content 1", "test1.txt"),
                    "text/plain",
                ),
            ),
            ("files", ("test2.jpg", self.create_test_image(), "image/jpeg")),
        ]

        response = await client.post(
            "/api/v1/files/upload-multiple", files=files, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(item["success"] for item in data)

    @pytest.mark.asyncio
    async def test_image_compression(self, client: AsyncClient):
        """测试图片压缩功能"""
        headers = await self.create_and_login_user(client)
        response = await client.post(
            "/api/v1/files/upload",
            files={
                "file": (
                    "large.jpg",
                    self.create_test_image(width=3000, height=2000),
                    "image/jpeg",
                )
            },
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json()["file_info"] is not None

    @pytest.mark.asyncio
    async def test_download_file(self, client: AsyncClient):
        """测试文件下载"""
        headers = await self.create_and_login_user(client)
        upload_response = await client.post(
            "/api/v1/files/upload",
            files={
                "file": (
                    "download_test.txt",
                    self.create_test_file("Download test content", "download_test.txt"),
                    "text/plain",
                )
            },
            headers=headers,
        )

        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_info"]["id"]

        download_response = await client.get(
            f"/api/v1/files/download/{file_id}", headers=headers
        )
        assert download_response.status_code == 200
        assert download_response.content == b"Download test content"

    @pytest.mark.asyncio
    async def test_download_nonexistent_file(self, client: AsyncClient):
        """测试下载不存在的文件"""
        response = await client.get("/api/v1/files/download/nonexistent-id")
        assert response.status_code == 404
        assert "文件不存在" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_file_info(self, client: AsyncClient):
        """测试获取文件信息"""
        headers = await self.create_and_login_user(client)
        upload_response = await client.post(
            "/api/v1/files/upload",
            files={
                "file": (
                    "info_test.txt",
                    self.create_test_file("Info test content", "info_test.txt"),
                    "text/plain",
                )
            },
            headers=headers,
        )

        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_info"]["id"]

        info_response = await client.get(
            f"/api/v1/files/info/{file_id}", headers=headers
        )
        assert info_response.status_code == 200

        info_data = info_response.json()
        assert info_data["original_name"] == "info_test.txt"
        assert info_data["file_size"] > 0
        assert info_data["mime_type"] == "text/plain"

    @pytest.mark.asyncio
    async def test_list_user_files(self, client: AsyncClient):
        """测试获取用户文件列表"""
        headers = await self.create_and_login_user(client)
        for i in range(3):
            await client.post(
                "/api/v1/files/upload",
                files={
                    "file": (
                        f"test{i}.txt",
                        self.create_test_file(f"Content {i}", f"test{i}.txt"),
                        "text/plain",
                    )
                },
                headers=headers,
            )

        response = await client.get("/api/v1/files/list", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert "files" in data
        assert "total" in data
        assert data["total"] >= 3

    @pytest.mark.asyncio
    async def test_list_user_files_is_scoped_to_current_user(self, client: AsyncClient):
        """用户只能看到自己的文件列表"""
        first_headers = await self.create_and_login_user(
            client, username="fileowner", email="fileowner@example.com"
        )
        second_headers = await self.create_and_login_user(
            client, username="otherfileuser", email="otherfileuser@example.com"
        )

        await client.post(
            "/api/v1/files/upload",
            files={
                "file": (
                    "owner.txt",
                    self.create_test_file("Owner content", "owner.txt"),
                    "text/plain",
                )
            },
            headers=first_headers,
        )

        response = await client.get("/api/v1/files/list", headers=second_headers)

        assert response.status_code == 200
        assert response.json()["total"] == 0

    @pytest.mark.asyncio
    async def test_private_file_download_requires_owner_or_admin(
        self, client: AsyncClient
    ):
        """私有文件不能被其他普通用户下载"""
        owner_headers = await self.create_and_login_user(
            client, username="privateowner", email="privateowner@example.com"
        )
        other_headers = await self.create_and_login_user(
            client, username="privateother", email="privateother@example.com"
        )

        upload_response = await client.post(
            "/api/v1/files/upload",
            files={
                "file": (
                    "private.txt",
                    self.create_test_file("Private content", "private.txt"),
                    "text/plain",
                )
            },
            headers=owner_headers,
        )
        file_id = upload_response.json()["file_info"]["id"]

        anonymous_response = await client.get(f"/api/v1/files/download/{file_id}")
        other_response = await client.get(
            f"/api/v1/files/download/{file_id}", headers=other_headers
        )
        owner_response = await client.get(
            f"/api/v1/files/download/{file_id}", headers=owner_headers
        )

        assert anonymous_response.status_code == 403
        assert other_response.status_code == 403
        assert owner_response.status_code == 200
        assert owner_response.content == b"Private content"

    @pytest.mark.asyncio
    async def test_public_file_can_be_downloaded_anonymously(self, client: AsyncClient):
        """公开文件可被匿名下载"""
        headers = await self.create_and_login_user(
            client, username="publicowner", email="publicowner@example.com"
        )
        upload_response = await client.post(
            "/api/v1/files/upload?is_public=true",
            files={
                "file": (
                    "public.txt",
                    self.create_test_file("Public content", "public.txt"),
                    "text/plain",
                )
            },
            headers=headers,
        )
        file_id = upload_response.json()["file_info"]["id"]

        response = await client.get(f"/api/v1/files/download/{file_id}")

        assert response.status_code == 200
        assert response.content == b"Public content"

    @pytest.mark.asyncio
    async def test_non_owner_cannot_delete_file(self, client: AsyncClient):
        """非属主不能删除他人文件"""
        owner_headers = await self.create_and_login_user(
            client, username="deleteowner", email="deleteowner@example.com"
        )
        other_headers = await self.create_and_login_user(
            client, username="deleteother", email="deleteother@example.com"
        )
        upload_response = await client.post(
            "/api/v1/files/upload",
            files={
                "file": (
                    "delete_denied.txt",
                    self.create_test_file("Delete denied", "delete_denied.txt"),
                    "text/plain",
                )
            },
            headers=owner_headers,
        )
        file_id = upload_response.json()["file_info"]["id"]

        delete_response = await client.delete(
            f"/api/v1/files/{file_id}", headers=other_headers
        )

        assert delete_response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_file(self, client: AsyncClient):
        """测试删除文件"""
        headers = await self.create_and_login_user(client)
        upload_response = await client.post(
            "/api/v1/files/upload",
            files={
                "file": (
                    "delete_test.txt",
                    self.create_test_file("Delete test content", "delete_test.txt"),
                    "text/plain",
                )
            },
            headers=headers,
        )

        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_info"]["id"]

        delete_response = await client.delete(
            f"/api/v1/files/{file_id}", headers=headers
        )
        assert delete_response.status_code == 200
        assert "文件删除成功" in delete_response.json()["message"]

        download_response = await client.get(
            f"/api/v1/files/download/{file_id}", headers=headers
        )
        assert download_response.status_code == 404
