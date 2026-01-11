#!/bin/bash
# Render 启动脚本
cd /opt/render/project/src
uvicorn main:app --host 0.0.0.0 --port 8000
