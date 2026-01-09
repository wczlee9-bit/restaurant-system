#!/usr/bin/env python3
"""
启动所有API服务
"""
import subprocess
import time
import sys
import os

# 设置环境变量
os.system('eval $(python /workspace/projects/scripts/load_env.py)')

# 启动餐饮系统完整API (端口8000)
print("启动餐饮系统完整API服务 (端口8000)...")
restaurant_process = subprocess.Popen(
    ['python', '-m', 'uvicorn', 'api.restaurant_api:app', '--host', '0.0.0.0', '--port', '8000'],
    cwd='/workspace/projects/src'
)

# 等待服务启动
time.sleep(3)

# 启动会员API (端口8004)
print("启动会员API服务 (端口8004)...")
member_process = subprocess.Popen(
    ['python', '-m', 'uvicorn', 'api.member_api:app', '--host', '0.0.0.0', '--port', '8004'],
    cwd='/workspace/projects/src'
)

# 等待服务启动
time.sleep(3)

# 启动总公司管理API (端口8006)
print("启动总公司管理API服务 (端口8006)...")
headquarters_process = subprocess.Popen(
    ['python', '-m', 'uvicorn', 'api.headquarters_api:app', '--host', '0.0.0.0', '--port', '8006'],
    cwd='/workspace/projects/src'
)

# 等待服务启动
time.sleep(3)

# 启动餐饮系统增强API (端口8007) - 新增菜品图片、会员二维码、优惠系统
print("启动餐饮系统增强API服务 (端口8007)...")
enhanced_process = subprocess.Popen(
    ['python', '-m', 'uvicorn', 'api.restaurant_enhanced_api:app', '--host', '0.0.0.0', '--port', '8007'],
    cwd='/workspace/projects/src'
)

# 等待服务启动
time.sleep(3)

print("\n所有API服务已启动:")
print("  - 餐饮系统API: http://localhost:8000")
print("  - 会员API: http://localhost:8004")
print("  - 总公司管理API: http://localhost:8006")
print("  - 餐饮系统增强API: http://localhost:8007 (菜品图片、会员二维码、优惠系统)")
print("\n按 Ctrl+C 停止所有服务")

try:
    # 保持运行
    restaurant_process.wait()
    member_process.wait()
    headquarters_process.wait()
    enhanced_process.wait()
except KeyboardInterrupt:
    print("\n正在停止服务...")
    restaurant_process.terminate()
    member_process.terminate()
    headquarters_process.terminate()
    enhanced_process.terminate()
    restaurant_process.wait()
    member_process.wait()
    headquarters_process.wait()
    enhanced_process.wait()
    print("服务已停止")
