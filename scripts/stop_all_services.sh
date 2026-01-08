#!/bin/bash
# 停止餐饮系统所有服务

echo "========================================="
echo "⏹️  停止餐饮点餐系统所有服务"
echo "========================================="
echo ""

# 停止API服务
if [ -f logs/api.pid ]; then
    API_PID=$(cat logs/api.pid)
    if ps -p $API_PID > /dev/null; then
        echo "🛑 停止API服务 (PID: $API_PID)..."
        kill $API_PID
        echo "✅ API服务已停止"
    else
        echo "⚠️  API服务进程不存在"
    fi
    rm -f logs/api.pid
fi

# 停止WebSocket服务
if [ -f logs/websocket.pid ]; then
    WS_PID=$(cat logs/websocket.pid)
    if ps -p $WS_PID > /dev/null; then
        echo "🛑 停止WebSocket服务 (PID: $WS_PID)..."
        kill $WS_PID
        echo "✅ WebSocket服务已停止"
    else
        echo "⚠️  WebSocket服务进程不存在"
    fi
    rm -f logs/websocket.pid
fi

# 停止HTTP服务
if [ -f logs/http.pid ]; then
    HTTP_PID=$(cat logs/http.pid)
    if ps -p $HTTP_PID > /dev/null; then
        echo "🛑 停止HTTP服务 (PID: $HTTP_PID)..."
        kill $HTTP_PID
        echo "✅ HTTP服务已停止"
    else
        echo "⚠️  HTTP服务进程不存在"
    fi
    rm -f logs/http.pid
fi

# 强制关闭所有相关端口
echo ""
echo "🔍 检查并关闭占用端口的进程..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8001 | xargs kill -9 2>/dev/null
lsof -ti:8080 | xargs kill -9 2>/dev/null

echo ""
echo "========================================="
echo "✅ 所有服务已停止"
echo "========================================="
echo ""
