#!/usr/bin/env python
"""
餐饮系统后端服务启动脚本
确保在 Render 环境中正确启动餐饮 API 服务
"""
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("餐饮系统后端服务启动")
print("=" * 60)

# 验证数据库驱动
print("\n验证数据库驱动...")
drivers = ["psycopg2", "psycopg", "pg8000"]
found_driver = False
for driver in drivers:
    try:
        __import__(driver)
        print(f"✓ {driver} 已安装")
        found_driver = True
    except ImportError:
        print(f"✗ {driver} 未安装")

if not found_driver:
    print("\n⚠️  警告：没有找到任何数据库驱动！")
    print("尝试安装 psycopg2-binary...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary==2.9.9"])
        print("✓ psycopg2-binary 安装成功")
    except subprocess.CalledProcessError as e:
        print(f"✗ psycopg2-binary 安装失败: {e}")
        sys.exit(1)

# 导入并启动餐饮 API
print("\n启动 FastAPI 服务...")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.restaurant_api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000))
    )
