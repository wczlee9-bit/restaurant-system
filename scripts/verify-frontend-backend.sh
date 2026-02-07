#!/bin/bash
#
# 前后端连接验证脚本
# 确保前端和后端完美配合
#

echo "=========================================="
echo "  🔍 前后端连接验证"
echo "=========================================="
echo ""

SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

# 1. 检查前端文件
echo "📂 步骤1: 检查前端文件..."
FRONTEND_DIR="/var/www/restaurant-system/frontend"

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "  ❌ 前端目录不存在: $FRONTEND_DIR"
    echo "  请先执行部署脚本"
    exit 1
fi

echo "  ✅ 前端目录存在"
echo "  前端文件清单："
ls -la "$FRONTEND_DIR"
echo ""

# 2. 检查API配置
echo "📝 步骤2: 检查前端API配置..."
API_FILE="$FRONTEND_DIR/common/js/api.js"

if [ ! -f "$API_FILE" ]; then
    echo "  ❌ API配置文件不存在: $API_FILE"
    exit 1
fi

echo "  ✅ API配置文件存在"
echo "  API_BASE配置："
grep "API_BASE" "$API_FILE" | head -1

# 检查API_BASE是否正确配置
if grep -q "API_BASE = '/api'" "$API_FILE"; then
    echo "  ✅ API_BASE配置正确（相对路径）"
elif grep -q "API_BASE = 'http://localhost:8000/api'" "$API_FILE"; then
    echo "  ⚠️  API_BASE使用localhost（仅本地可用）"
else
    echo "  ⚠️  API_BASE配置可能有问题"
fi
echo ""

# 3. 测试后端API直连
echo "🔗 步骤3: 测试后端API直连..."
API_ERRORS=0

# 测试健康检查
echo -n "  测试 http://localhost:8000/api/health ... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health | grep -q "200"; then
    echo "✅"
else
    echo "❌"
    ((API_ERRORS++))
fi

# 测试桌号接口
echo -n "  测试 http://localhost:8000/api/tables ... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/tables | grep -q "200"; then
    echo "✅"
else
    echo "❌"
    ((API_ERRORS++))
fi

# 测试菜单接口
echo -n "  测试 http://localhost:8000/api/menu-items ... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/menu-items | grep -q "200"; then
    echo "✅"
else
    echo "❌"
    ((API_ERRORS++))
fi

if [ $API_ERRORS -eq 0 ]; then
    echo "  ✅ 后端API直连测试全部通过"
else
    echo "  ⚠️  $API_ERRORS 个API测试失败"
    echo "  可能的原因："
    echo "    - 后端服务未运行"
    echo "    - 后端服务不在端口8000"
    echo "    - 数据库连接失败"
fi
echo ""

# 4. 测试Nginx代理
echo "🌐 步骤4: 测试Nginx代理..."

# 检查Nginx是否运行
if systemctl is-active --quiet nginx; then
    echo "  ✅ Nginx服务运行中"
else
    echo "  ⚠️  Nginx服务未运行"
    echo "  请启动Nginx: sudo systemctl start nginx"
fi

# 测试通过Nginx访问API
echo "  通过Nginx访问API（http://localhost/api/）..."

echo -n "    测试 /api/health ... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health | grep -q "200"; then
    echo "✅"
else
    echo "❌"
fi

echo -n "    测试 /api/tables ... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost/api/tables | grep -q "200"; then
    echo "✅"
else
    echo "❌"
fi
echo ""

# 5. 检查前端页面
echo "📱 步骤5: 检查前端页面..."

PAGES=(
    "$FRONTEND_DIR/customer/index.html"
    "$FRONTEND_DIR/customer/menu/index.html"
    "$FRONTEND_DIR/customer/cart/index.html"
    "$FRONTEND_DIR/customer/order/index.html"
    "$FRONTEND_DIR/admin/dashboard/index.html"
)

MISSING_PAGES=0
for page in "${PAGES[@]}"; do
    if [ -f "$page" ]; then
        echo "  ✅ $(basename $(dirname $page))/$(basename $page)"
    else
        echo "  ❌ $(basename $(dirname $page))/$(basename $page) - 缺失"
        ((MISSING_PAGES++))
    fi
done

if [ $MISSING_PAGES -eq 0 ]; then
    echo "  ✅ 所有前端页面完整"
else
    echo "  ⚠️  $MISSING_PAGES 个页面缺失"
fi
echo ""

# 6. 测试WebSocket
echo "🔌 步骤6: 测试WebSocket连接..."

# 检查8001端口
if lsof -i :8001 > /dev/null 2>&1; then
    echo "  ✅ WebSocket服务运行中（端口8001）"
else
    echo "  ⚠️  WebSocket服务未运行（端口8001）"
fi

# 测试WebSocket代理
echo -n "  测试 /ws/ 代理 ... "
# 使用curl测试WebSocket升级请求（会失败但能看到代理正常工作）
if curl -s -o /dev/null -w "%{http_code}" -H "Upgrade: websocket" -H "Connection: Upgrade" http://localhost/ws/test 2>/dev/null | grep -q "400\|426"; then
    echo "✅ 代理正常"
else
    echo "⚠️  代理可能有问题"
fi
echo ""

# 7. 总结
echo "=========================================="
echo "  📊 验证总结"
echo "=========================================="
echo ""

# 计算总体状态
TOTAL_ISSUES=0

# 后端状态
if [ $API_ERRORS -eq 0 ]; then
    echo "✅ 后端API：正常"
else
    echo "❌ 后端API：有问题（$API_ERRORS 个错误）"
    ((TOTAL_ISSUES++))
fi

# Nginx状态
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx：正常运行"
else
    echo "❌ Nginx：未运行"
    ((TOTAL_ISSUES++))
fi

# 前端状态
if [ $MISSING_PAGES -eq 0 ]; then
    echo "✅ 前端文件：完整"
else
    echo "❌ 前端文件：缺失（$MISSING_PAGES 个页面）"
    ((TOTAL_ISSUES++))
fi

echo ""

if [ $TOTAL_ISSUES -eq 0 ]; then
    echo "🎉 前后端完美配合！可以正常使用了！"
else
    echo "⚠️  发现 $TOTAL_ISSUES 个问题，需要解决"
    echo ""
    echo "解决方案："
    echo "  1. 如果后端API失败："
    echo "     - 检查后端服务是否运行：ps aux | grep python"
    echo "     - 检查端口是否占用：lsof -i :8000"
    echo "     - 查看后端日志"
    echo ""
    echo "  2. 如果Nginx失败："
    echo "     - 启动Nginx：sudo systemctl start nginx"
    echo "     - 查看Nginx日志：sudo tail -f /var/log/nginx/error.log"
    echo ""
    echo "  3. 如果前端缺失："
    echo "     - 重新执行部署脚本：bash deploy-frontend-safe.sh"
fi

echo ""
echo "=========================================="
echo "🌐 访问地址："
echo "  顾客端: http://$SERVER_IP/"
echo "  管理端: http://$SERVER_IP/admin/dashboard/index.html"
echo "  API测试: http://$SERVER_IP/api/docs"
echo ""
echo "=========================================="

exit $TOTAL_ISSUES
