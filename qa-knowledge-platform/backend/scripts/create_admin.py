#!/usr/bin/env python3
"""
创建管理员用户脚本
"""

import asyncio
import sys
import os
from pathlib import Path
import getpass

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.modules.users.models import User, Team, UserRole
import uuid
import bcrypt


async def create_admin_user():
    """创建管理员用户"""
    print("🔧 创建管理员用户")
    
    # 获取用户输入
    username = input("请输入用户名 (默认: admin): ").strip() or "admin"
    email = input("请输入邮箱: ").strip()
    
    if not email:
        print("❌ 邮箱不能为空")
        return False
    
    password = getpass.getpass("请输入密码: ")
    if len(password) < 6:
        print("❌ 密码长度至少6位")
        return False
    
    nickname = input("请输入昵称 (可选): ").strip() or username
    
    async with AsyncSessionLocal() as session:
        try:
            # 检查用户名是否已存在
            result = await session.execute(
                select(User).where(User.username == username)
            )
            if result.scalar_one_or_none():
                print(f"❌ 用户名 '{username}' 已存在")
                return False
            
            # 检查邮箱是否已存在
            result = await session.execute(
                select(User).where(User.email == email)
            )
            if result.scalar_one_or_none():
                print(f"❌ 邮箱 '{email}' 已存在")
                return False
            
            # 获取默认团队
            result = await session.execute(select(Team).limit(1))
            default_team = result.scalar_one_or_none()
            
            # 创建密码哈希
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # 创建管理员用户
            admin_user = User(
                id=uuid.uuid4(),
                username=username,
                email=email,
                password_hash=password_hash,
                nickname=nickname,
                bio="系统管理员",
                role=UserRole.SUPER_ADMIN,
                team_id=default_team.id if default_team else None,
                skills={
                    "测试类型": ["功能测试", "性能测试", "自动化测试"],
                    "管理经验": ["团队管理", "项目管理", "质量管理"]
                },
                is_active=True,
                is_verified=True
            )
            
            session.add(admin_user)
            await session.commit()
            
            print("✅ 管理员用户创建成功")
            print(f"   用户名: {username}")
            print(f"   邮箱: {email}")
            print(f"   昵称: {nickname}")
            print(f"   角色: 超级管理员")
            
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"❌ 创建管理员用户失败: {e}")
            return False


async def list_admin_users():
    """列出所有管理员用户"""
    print("\n📋 当前管理员用户列表:")
    
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(User).where(
                    User.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN])
                ).order_by(User.created_at)
            )
            admin_users = result.scalars().all()
            
            if not admin_users:
                print("   暂无管理员用户")
                return
            
            for user in admin_users:
                role_name = "超级管理员" if user.role == UserRole.SUPER_ADMIN else "管理员"
                status = "✅ 活跃" if user.is_active else "❌ 禁用"
                print(f"   - {user.username} ({user.email}) - {role_name} - {status}")
                
        except Exception as e:
            print(f"❌ 获取管理员列表失败: {e}")


async def main():
    """主函数"""
    print("👤 QA测试知识协作平台 - 管理员用户管理")
    
    while True:
        print("\n请选择操作:")
        print("1. 创建管理员用户")
        print("2. 查看管理员列表")
        print("3. 退出")
        
        choice = input("\n请输入选项 (1-3): ").strip()
        
        if choice == "1":
            await create_admin_user()
        elif choice == "2":
            await list_admin_users()
        elif choice == "3":
            print("👋 再见!")
            break
        else:
            print("❌ 无效选项，请重新选择")


if __name__ == "__main__":
    asyncio.run(main())