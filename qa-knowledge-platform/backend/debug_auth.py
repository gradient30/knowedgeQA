#!/usr/bin/env python3
"""
调试认证问题
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.modules.users.services import AuthService
from app.modules.users.schemas import UserLogin
from app.core.database import AsyncSessionLocal

async def test_auth_service():
    """测试认证服务"""
    print("🔍 测试认证服务...")
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthService(session)
        
        # 测试登录
        login_data = UserLogin(
            email="admin@qa-platform.com",
            password="admin123"
        )
        
        try:
            result = await auth_service.authenticate_user(login_data)
            print("✅ 认证服务测试成功!")
            print(f"用户: {result['user'].username}")
            print(f"令牌: {result['access_token'][:50]}...")
            
            # 测试获取当前用户
            token = result['access_token']
            user = await auth_service.get_current_user(token)
            print(f"✅ 获取当前用户成功: {user.username}")
            
        except Exception as e:
            print(f"❌ 认证服务测试失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_auth_service())