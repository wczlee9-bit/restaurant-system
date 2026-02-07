#!/bin/bash
#
# 服务器环境安全检查脚本
# 检查当前配置，确保前端部署不会影响已有后端
#

echo "=========================================="
echo "  🔍 服务器环境安全检查"
echo "=========================================="
echo ""

# 1. 检查当前目录
echo "📍 当前目录："
pwd
echo ""

# 2. 检查后端API服务状态
echo "🔧 检查后端API服务..."
echo ""

# 检查Python进程
echo "正在运行的Python进程："
ps aux | grep python | grep -v grep || echo "  无Python进程"
echo ""

# 检查端口占用
echo "端口占用情况："
for port in 8000 8001 8004 8006 8007; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo "  ✅ 端口 $port：运行中"
        lsof -i :$port | grep LISTEN
    else
        echo "  ⚠️  端口 $port：未运行"
    fi
done
echo ""

# 3. 检查Nginx配置
echo "🌐 检查Nginx配置..."
if command -v nginx &> /dev/null; then
    echo "  ✅ Nginx已安装"
    nginx -v
    echo ""
    echo "  Nginx配置测试："
    nginx -t 2>&1 || echo "  ⚠️  Nginx配置有错误"
else
    echo "  ⚠️  Nginx未安装"
fi
echo ""

# 4. 检查现有Nginx站点配置
echo "📋 现有Nginx站点配置："
if [ -d "/etc/nginx/sites-available" ]; then
    ls -la /etc/nginx/sites-available/ 2>/dev/null || echo "  无站点配置"
fi
echo ""

if [ -d "/etc/nginx/sites-enabled" ]; then
    echo "已启用的站点："
    ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo "  无已启用站点"
fi
echo ""

# 5. 检查前端部署目录
echo "📂 检查前端部署目录..."
FRONTEND_DIR="/var/www/restaurant-system/frontend"
if [ -d "$FRONTEND_DIR" ]; then
    echo "  ✅ 前端目录存在：$FRONTEND_DIR"
    echo "  目录内容："
    ls -la "$FRONTEND_DIR"
else
    echo "  ℹ️  前端目录不存在：$FRONTEND_DIR"
    echo "  需要创建：sudo mkdir -p $FRONTEND_DIR"
fi
echo ""

# 6. 测试后端API连接
echo "🔗 测试后端API连接..."
for endpoint in \
    "http://localhost:8000/api/health" \
    "http://localhost:8000/api/tables" \
    "http://localhost:8001/api/health"; do
    echo -n "  测试 $endpoint ... "
    if curl -s -o /dev/null -w "%{http_code}" "$endpoint" | grep -q "200\|404"; then
        echo "✅ 可访问"
    else
        echo "⚠️  无法访问"
    fi
done
echo ""

# 7. 检查前端API配置
echo "📝 检查前端API配置..."
API_FILE="/www/wwwroot/restaurant-system/frontend/common/js/api.js"
if [ -f "$API_FILE" ]; then
    echo "  API文件存在：$API_FILE"
    echo "  API_BASE配置："
    grep "API_BASE" "$API_FILE" | head -1
else
    echo "  ⚠️  API文件不存在：$API_FILE"
fi
echo ""

# 8. 检查防火墙
echo "🔥 检查防火墙..."
if command -v ufw &> /dev/null; then
    echo "  UFW状态："
    sudo ufw status 2>/dev/null | head -10 || echo "  无法获取UFW状态"
fi
echo ""

# 9. 获取服务器IP
echo "🌐 服务器信息："
echo "  IP地址："
curl -s ifconfig.me 2>/dev/null || echo "  无法获取（可能在局域网）"
echo ""
echo "  主机名："
hostname
echo ""

# 10. 安全性检查
echo "🔒 安全性检查..."
echo "  重要目录权限："
for dir in "/www/wwwroot/restaurant-system" "/var/www/restaurant-system" "/etc/nginx"; do
    if [ -d "$dir" ]; then
        echo "  $dir：$(ls -ld $dir | awk '{print $1, $3, $4}')"
    fi
done
echo ""

echo "=========================================="
echo "  ✅ 检查完成"
echo "=========================================="
echo ""
echo "📋 检查总结："
echo "  - 后端API服务状态：$(ps aux | grep python | grep -v grep > /dev/null && echo '运行中' || echo '未运行')"
echo "  - Nginx状态：$(systemctl is-active nginx 2>/dev/null || echo '未知')"
echo "  - 前端目录：$([ -d "$FRONTEND_DIR" ] && echo '存在' || echo '不存在')"
echo ""
echo "⚠️  部署前请注意："
echo "  1. 后端API服务运行在端口 8000/8001"
echo "  2. 前端将部署到 /var/www/restaurant-system/frontend"
echo "  3. Nginx配置将代理 /api 到 localhost:8000/api"
echo "  4. 不会修改后端代码或配置"
echo ""
echo "=========================================="
