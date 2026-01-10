#!/bin/bash
# 安装 systemd 服务配置

set -e

PROJECT_PATH="/workspace/projects"
SYSTEMD_DIR="/etc/systemd/system"

echo "========================================="
echo "📦 安装 systemd 服务"
echo "========================================="

# 停止旧服务（如果存在）
echo "⏹️  停止旧服务..."
systemctl stop restaurant-api 2>/dev/null || true
systemctl stop restaurant-enhanced-api 2>/dev/null || true
systemctl stop member-api 2>/dev/null || true
systemctl stop headquarters-api 2>/dev/null || true
systemctl stop settlement-api 2>/dev/null || true
systemctl stop websocket-api 2>/dev/null || true

# 复制服务文件
echo "📄 复制服务配置文件..."
cp "${PROJECT_PATH}/systemd/restaurant-api.service" "${SYSTEMD_DIR}/"
cp "${PROJECT_PATH}/systemd/restaurant-enhanced-api.service" "${SYSTEMD_DIR}/"
cp "${PROJECT_PATH}/systemd/member-api.service" "${SYSTEMD_DIR}/"
cp "${PROJECT_PATH}/systemd/headquarters-api.service" "${SYSTEMD_DIR}/"
cp "${PROJECT_PATH}/systemd/settlement-api.service" "${SYSTEMD_DIR}/"
cp "${PROJECT_PATH}/systemd/websocket-api.service" "${SYSTEMD_DIR}/"

# 重新加载 systemd
echo "🔄 重新加载 systemd..."
systemctl daemon-reload

# 创建日志目录
mkdir -p "${PROJECT_PATH}/logs"

# 启用服务（开机自启）
echo "✅ 启用服务..."
systemctl enable restaurant-api
systemctl enable restaurant-enhanced-api
systemctl enable member-api
systemctl enable headquarters-api
systemctl enable settlement-api
systemctl enable websocket-api

# 启动服务
echo "🚀 启动服务..."
systemctl start restaurant-api
systemctl start restaurant-enhanced-api
systemctl start member-api
systemctl start headquarters-api
systemctl start settlement-api
systemctl start websocket-api

# 等待服务启动
sleep 3

# 检查服务状态
echo "========================================="
echo "📊 服务状态"
echo "========================================="
systemctl status restaurant-api --no-pager -l || true
echo ""
systemctl status restaurant-enhanced-api --no-pager -l || true
echo ""
systemctl status member-api --no-pager -l || true
echo ""
systemctl status headquarters-api --no-pager -l || true
echo ""
systemctl status settlement-api --no-pager -l || true
echo ""
systemctl status websocket-api --no-pager -l || true
echo ""

# 检查端口
echo "========================================="
echo "🔌 端口检查"
echo "========================================="
for port in 8000 8001 8004 8006 8007 8008; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "✅ 端口 $port 运行正常"
    else
        echo "❌ 端口 $port 未运行"
    fi
done

echo "========================================="
echo "✅ 安装完成！"
echo "========================================="
echo ""
echo "常用命令:"
echo "  查看服务状态: systemctl status restaurant-api"
echo "  重启服务:     systemctl restart restaurant-api"
echo "  查看日志:     journalctl -u restaurant-api -f"
echo "  停止服务:     systemctl stop restaurant-api"
echo "========================================="
