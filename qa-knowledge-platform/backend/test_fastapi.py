#!/usr/bin/env python3
"""
直接测试FastAPI应用
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from app.main import app

def test_fastapi_auth():
    """测试FastAPI认证端点"""
    print("🔍 测试FastAPI应用...")
    
    client = TestClient(app)
    
    # 测试根端点
    print("测试根端点...")
    response = client.get("/")
    print(f"根端点状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"根端点响应: {response.json()}")
    
    # 测试登录端点
    print("\n测试登录端点...")
    login_data = {
        "email": "admin@qa-platform.com",
        "password": "admin123"
    }
    
    try:
        response = client.post("/api/v1/auth/login", json=login_data)
        print(f"登录状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 登录成功!")
            print(f"用户: {data.get('user', {}).get('username', '')}")
            token = data.get('access_token')
            
            # 测试获取当前用户
            print("\n测试获取当前用户...")
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/v1/auth/me", headers=headers)
            print(f"获取用户状态码: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                print("✅ 获取用户信息成功!")
                print(f"用户名: {user_data.get('username', '')}")
                print(f"邮箱: {user_data.get('email', '')}")
            else:
                print(f"❌ 获取用户信息失败: {response.text}")
                
        else:
            print(f"❌ 登录失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fastapi_auth()