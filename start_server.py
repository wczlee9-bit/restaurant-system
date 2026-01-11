#!/usr/bin/env python
"""
餐饮系统后端服务启动脚本
确保在 Render 环境中正确启动餐饮 API 服务
"""
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 导入并启动餐饮 API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.restaurant_api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000))
    )
