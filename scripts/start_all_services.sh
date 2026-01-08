#!/bin/bash
# 启动餐饮系统完整服务
# 包括API服务、WebSocket服务和HTTP文件服务

echo "========================================="
echo "🍽️ 餐饮点餐系统 - 完整服务启动"
echo "========================================="
echo ""

# 检查端口是否被占用
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  端口 $1 已被占用，尝试关闭..."
        lsof -ti:$1 | xargs kill -9
        sleep 2
    fi
}

# 检查并关闭占用的端口
check_port 8000  # API服务
check_port 8001  # WebSocket服务
check_port 8080  # HTTP文件服务

echo "📝 启动服务..."
echo ""

# 创建日志目录
mkdir -p logs

# 启动API服务（端口8000）
echo "🚀 启动API服务 (端口8000)..."
cd "$(dirname "$0")"
nohup python -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
API_PID=$!
echo "✅ API服务已启动 (PID: $API_PID)"

# 启动WebSocket服务（端口8001）
echo "🚀 启动WebSocket服务 (端口8001)..."
nohup python -m uvicorn src.api.websocket_api:app --host 0.0.0.0 --port 8001 > logs/websocket.log 2>&1 &
WS_PID=$!
echo "✅ WebSocket服务已启动 (PID: $WS_PID)"

# 启动HTTP文件服务（端口8080）
echo "🚀 启动HTTP文件服务 (端口8080)..."
nohup python -m http.server 8080 --directory assets > logs/http.log 2>&1 &
HTTP_PID=$!
echo "✅ HTTP文件服务已启动 (PID: $HTTP_PID)"

# 保存PID到文件
echo $API_PID > logs/api.pid
echo $WS_PID > logs/websocket.pid
echo $HTTP_PID > logs/http.pid

echo ""
echo "========================================="
echo "✅ 所有服务启动完成！"
echo "========================================="
echo ""
echo "📊 服务状态:"
echo "  - API服务:         http://localhost:8000"
echo "  - API文档:         http://localhost:8000/docs"
echo "  - WebSocket服务:   ws://localhost:8001"
echo "  - 测试页面:        http://localhost:8080"
echo "  - 顾客点餐页面:    http://localhost:8080/customer_order.html"
echo "  - 工作人员端:      http://localhost:8080/staff_workflow.html"
echo "  - 店铺设置:        http://localhost:8080/shop_settings.html"
echo ""
echo "📝 日志文件:"
echo "  - API服务日志:     logs/api.log"
echo "  - WebSocket日志:   logs/websocket.log"
echo "  - HTTP服务日志:    logs/http.log"
echo ""
echo "⏹️  停止服务: ./scripts/stop_all_services.sh"
echo "========================================="
echo ""
