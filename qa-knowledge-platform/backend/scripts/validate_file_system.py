#!/usr/bin/env python3
"""
文件上传系统验证脚本
检查文件上传系统的实现是否完整
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))


def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (不存在)")
        return False


def check_directory_structure():
    """检查目录结构"""
    print("📁 检查文件上传系统目录结构...")
    
    base_dir = Path(__file__).parent.parent
    files_module = base_dir / "app" / "modules" / "files"
    
    required_files = [
        (files_module / "__init__.py", "Files模块初始化文件"),
        (files_module / "models.py", "文件数据模型"),
        (files_module / "schemas.py", "文件数据结构"),
        (files_module / "services.py", "文件服务逻辑"),
        (files_module / "api.py", "文件API接口"),
        (files_module / "storage.py", "存储后端服务"),
    ]
    
    all_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist


def check_api_routes():
    """检查API路由注册"""
    print("\n🔗 检查API路由注册...")
    
    router_file = Path(__file__).parent.parent / "app" / "api" / "v1" / "router.py"
    
    if not os.path.exists(router_file):
        print("❌ API路由文件不存在")
        return False
    
    with open(router_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'files_router' in content and 'files' in content:
        print("✅ 文件上传路由已注册")
        return True
    else:
        print("❌ 文件上传路由未正确注册")
        return False


def check_database_models():
    """检查数据库模型"""
    print("\n🗄️ 检查数据库模型...")
    
    models_file = Path(__file__).parent.parent / "app" / "modules" / "files" / "models.py"
    
    if not os.path.exists(models_file):
        print("❌ 文件模型文件不存在")
        return False
    
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_elements = [
        ('class UploadedFile', '文件上传模型'),
        ('class FileType', '文件类型枚举'),
        ('class FileStatus', '文件状态枚举'),
        ('file_path', '文件路径字段'),
        ('file_size', '文件大小字段'),
        ('mime_type', 'MIME类型字段'),
    ]
    
    all_found = True
    for element, description in required_elements:
        if element in content:
            print(f"✅ {description}: {element}")
        else:
            print(f"❌ {description}: {element} (未找到)")
            all_found = False
    
    return all_found


def check_api_endpoints():
    """检查API端点"""
    print("\n🌐 检查API端点...")
    
    api_file = Path(__file__).parent.parent / "app" / "modules" / "files" / "api.py"
    
    if not os.path.exists(api_file):
        print("❌ API文件不存在")
        return False
    
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_endpoints = [
        ('/upload', '单文件上传'),
        ('/upload-multiple', '批量文件上传'),
        ('/download/{file_id}', '文件下载'),
        ('/info/{file_id}', '文件信息'),
        ('/list', '文件列表'),
        ('@router.delete', '文件删除'),
    ]
    
    all_found = True
    for endpoint, description in required_endpoints:
        if endpoint in content:
            print(f"✅ {description}: {endpoint}")
        else:
            print(f"❌ {description}: {endpoint} (未找到)")
            all_found = False
    
    return all_found


def check_file_processing():
    """检查文件处理功能"""
    print("\n🖼️ 检查文件处理功能...")
    
    services_file = Path(__file__).parent.parent / "app" / "modules" / "files" / "services.py"
    
    if not os.path.exists(services_file):
        print("❌ 服务文件不存在")
        return False
    
    with open(services_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_features = [
        ('validate_file', '文件验证'),
        ('save_file', '文件保存'),
        ('_process_image', '图片处理'),
        ('thumbnail', '缩略图生成'),
        ('compress', '图片压缩'),
        ('delete_file', '文件删除'),
        ('get_user_files', '用户文件列表'),
    ]
    
    all_found = True
    for feature, description in required_features:
        if feature in content:
            print(f"✅ {description}: {feature}")
        else:
            print(f"❌ {description}: {feature} (未找到)")
            all_found = False
    
    return all_found


def check_configuration():
    """检查配置"""
    print("\n⚙️ 检查配置...")
    
    config_file = Path(__file__).parent.parent / "app" / "core" / "config.py"
    
    if not os.path.exists(config_file):
        print("❌ 配置文件不存在")
        return False
    
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_configs = [
        ('UPLOAD_DIR', '上传目录配置'),
        ('MAX_FILE_SIZE', '最大文件大小配置'),
        ('ALLOWED_FILE_TYPES', '允许的文件类型配置'),
        ('USE_CLOUD_STORAGE', '云存储配置'),
    ]
    
    all_found = True
    for config, description in required_configs:
        if config in content:
            print(f"✅ {description}: {config}")
        else:
            print(f"❌ {description}: {config} (未找到)")
            all_found = False
    
    return all_found


def check_migration():
    """检查数据库迁移"""
    print("\n🗃️ 检查数据库迁移...")
    
    migration_file = Path(__file__).parent.parent / "alembic" / "versions" / "add_file_upload_tables.py"
    
    if check_file_exists(migration_file, "文件上传表迁移"):
        with open(migration_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'uploaded_files' in content and 'op.create_table' in content:
            print("✅ 迁移文件包含文件上传表创建")
            return True
        else:
            print("❌ 迁移文件内容不完整")
            return False
    
    return False


def main():
    """主函数"""
    print("=" * 60)
    print("🔍 QA测试知识协作平台 - 文件上传系统验证")
    print("=" * 60)
    
    checks = [
        ("目录结构", check_directory_structure),
        ("API路由", check_api_routes),
        ("数据库模型", check_database_models),
        ("API端点", check_api_endpoints),
        ("文件处理", check_file_processing),
        ("配置", check_configuration),
        ("数据库迁移", check_migration),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}检查失败: {str(e)}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📊 验证结果汇总:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:15} {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 文件上传系统实现完整！")
        return True
    else:
        print("⚠️ 文件上传系统实现不完整，请检查失败项。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)