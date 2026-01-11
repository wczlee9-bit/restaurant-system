#!/bin/bash
set -e

echo "开始安装依赖..."

# 清理旧的虚拟环境
rm -rf .venv

# 安装 pg8000 数据库驱动（纯 Python，最稳定）
echo "安装 pg8000..."
pip install pg8000==1.31.2 --no-cache-dir

# 安装其他依赖
echo "安装其他依赖..."
pip install -r requirements-prod.txt --no-cache-dir

echo "依赖安装完成！"
