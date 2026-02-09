#!/bin/bash

echo "======================================"
echo "  腾讯服务器更新脚本"
echo "  更新时间：$(date)"
echo "======================================"
echo ""

# 进入项目目录
cd /var/www/restaurant-system || exit 1

echo "1. 拉取最新代码..."
git pull origin main
if [ $? -ne 0 ]; then
    echo "❌ 拉取代码失败"
    exit 1
fi
echo "✅ 代码拉取成功"
echo ""

echo "2. 执行数据库更新..."
sudo -u postgres psql -d restaurant_system < assets/update_pending_orders.sql
if [ $? -ne 0 ]; then
    echo "❌ 数据库更新失败"
    exit 1
fi
echo "✅ 数据库更新成功"
echo ""

echo "3. 验证数据库更新..."
sudo -u postgres psql -d restaurant_system -c "SELECT order_status, COUNT(*) FROM orders GROUP BY order_status;"
echo ""

echo "4. 重启后端服务..."
pkill -f "uvicorn.*restaurant_api"
sleep 2

nohup python3 -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000 > /var/log/restaurant_api.log 2>&1 &

sleep 3

if ps aux | grep -v grep | grep "uvicorn.*restaurant_api" > /dev/null; then
    echo "✅ 后端服务启动成功"
else
    echo "❌ 后端服务启动失败，请查看日志："
    tail -n 20 /var/log/restaurant_api.log
    exit 1
fi
echo ""

echo "5. 测试API..."
curl -s http://localhost:8000/api/ | python3 -m json.tool > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ API测试成功"
else
    echo "⚠️ API测试失败，请检查服务状态"
fi
echo ""

echo "======================================"
echo "  更新完成！"
echo "======================================"
echo ""
echo "请执行以下操作："
echo "1. 强制刷新浏览器缓存（Ctrl+F5 或 Cmd+Shift+R）"
echo "2. 测试新功能："
echo "   - 创建新订单（状态应为preparing）"
echo "   - 厨师取消菜品"
echo "   - 传菜员查看已取消菜品"
echo "   - 顾客查看订单详情"
echo "   - 收银员收费"
echo ""
echo "如有问题，请查看日志："
echo "  tail -f /var/log/restaurant_api.log"
echo ""
