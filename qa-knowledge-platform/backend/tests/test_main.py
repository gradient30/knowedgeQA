"""
主应用测试
"""
import pytest
from httpx import AsyncClient


class TestMain:
    """主应用测试类"""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """测试根路径端点"""
        response = await client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "QA测试知识协作平台 API"
        assert data["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """测试健康检查端点"""
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "qa-knowledge-platform-backend"
    
    @pytest.mark.asyncio
    async def test_api_docs(self, client: AsyncClient):
        """测试API文档端点"""
        response = await client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    @pytest.mark.asyncio
    async def test_openapi_json(self, client: AsyncClient):
        """测试OpenAPI JSON端点"""
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert data["info"]["title"] == "QA测试知识协作平台 API"
        assert data["info"]["version"] == "1.0.0"