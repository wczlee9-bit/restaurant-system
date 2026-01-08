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

# 启动顾客端API (端口8000)
print("启动顾客端API服务 (端口8000)...")
customer_process = subprocess.Popen(
    ['python', '-m', 'uvicorn', 'api.customer_api:app', '--host', '0.0.0.0', '--port', '8000'],
    cwd='/workspace/projects/src'
)

# 等待服务启动
time.sleep(3)

# 启动店员端API (端口8001)
print("启动店员端API服务 (端口8001)...")
staff_process = subprocess.Popen(
    ['python', '-m', 'uvicorn', 'api.staff_api:app', '--host', '0.0.0.0', '--port', '8001'],
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

print("\n所有API服务已启动:")
print("  - 顾客端API: http://localhost:8000")
print("  - 店员端API: http://localhost:8001")
print("  - 会员API: http://localhost:8004")
print("  - 总公司管理API: http://localhost:8006")
print("\n按 Ctrl+C 停止所有服务")

try:
    # 保持运行
    customer_process.wait()
    staff_process.wait()
    member_process.wait()
    headquarters_process.wait()
except KeyboardInterrupt:
    print("\n正在停止服务...")
    customer_process.terminate()
    staff_process.terminate()
    member_process.terminate()
    headquarters_process.terminate()
    customer_process.wait()
    staff_process.wait()
    member_process.wait()
    headquarters_process.wait()
    print("服务已停止")
