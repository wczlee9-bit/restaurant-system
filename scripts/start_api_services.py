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

print("\n所有API服务已启动:")
print("  - 顾客端API: http://localhost:8000")
print("  - 店员端API: http://localhost:8001")
print("\n按 Ctrl+C 停止所有服务")

try:
    # 保持运行
    customer_process.wait()
    staff_process.wait()
except KeyboardInterrupt:
    print("\n正在停止服务...")
    customer_process.terminate()
    staff_process.terminate()
    customer_process.wait()
    staff_process.wait()
    print("服务已停止")
