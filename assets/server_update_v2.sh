#!/bin/bash

echo "======================================"
echo "  服务器更新脚本（完整版）"
echo "======================================"
echo ""

cd /var/www/restaurant-system

echo "步骤 1/7: 备份原文件..."
BACKUP_TIME=$(date +%Y%m%d_%H%M%S)
cp src/api/restaurant_api.py src/api/restaurant_api.py.backup_$BACKUP_TIME
cp assets/staff_workflow.html assets/staff_workflow.html.backup_$BACKUP_TIME
cp frontend/customer/order/order-detail.html frontend/customer/order/order-detail.html.backup_$BACKUP_TIME 2>/dev/null || true
echo "✅ 备份完成"
echo ""

echo "步骤 2/7: 修改订单创建逻辑（pending → preparing）..."
# 修改订单状态
sed -i 's/order_status="pending"  # 厨师可以开始制作/order_status="preparing"  # 直接进入制作流程/' src/api/restaurant_api.py
sed -i 's/status="pending"/status="preparing"/g' src/api/restaurant_api.py
echo "✅ 订单创建逻辑修改完成"
echo ""

echo "步骤 3/7: 更新状态流转逻辑..."
# 修改pending状态流转
sed -i "s/'pending': \['confirmed', 'cancelled'\]/'pending': ['preparing', 'cancelled']/" src/api/restaurant_api.py
# 修改confirmed状态流转
sed -i "s/'confirmed': \['preparing', 'cancelled'\]/'confirmed': ['preparing']/" src/api/restaurant_api.py
# 修改preparing状态流转
sed -i "s/'preparing': \['ready', 'cancelled'\]/'preparing': ['ready', 'cancelled']/" src/api/restaurant_api.py
echo "✅ 状态流转修改完成"
echo ""

echo "步骤 4/7: 修改订单项状态流转（添加cancelled）..."
# 查找订单项状态流转并修改
sed -i "s/'pending': \['preparing'\]/'pending': ['preparing', 'cancelled']/" src/api/restaurant_api.py
sed -i "s/'preparing': \['ready'\]/'preparing': ['ready', 'cancelled']/" src/api/restaurant_api.py
echo "✅ 订单项状态流转修改完成"
echo ""

echo "步骤 5/7: 执行数据库更新..."
# 创建SQL脚本
cat > /tmp/update_pending.sql << 'EOF'
-- 更新订单状态
UPDATE orders SET order_status = 'preparing' WHERE order_status = 'pending';
-- 更新订单项状态
UPDATE order_items SET status = 'preparing' WHERE status = 'pending';
-- 验证更新
SELECT order_status, COUNT(*) FROM orders GROUP BY order_status;
SELECT status, COUNT(*) FROM order_items GROUP BY status;
EOF

sudo -u postgres psql -d restaurant_system < /tmp/update_pending.sql
echo "✅ 数据库更新完成"
echo ""

echo "步骤 6/7: 需要手动添加的功能..."
echo "⚠️ 以下功能需要手动添加（代码已准备好，见下方）："
echo ""
echo "  1. 后端：菜品取消后的金额计算逻辑"
echo "  2. 后端：订单完成条件更新（支持cancelled）"
echo "  3. 前端：厨师取消按钮"
echo "  4. 前端：传菜员通知功能"
echo "  5. 顾客端：显示已取消菜品"
echo ""

echo "======================================"
echo "  基础更新完成！"
echo "======================================"
echo ""
echo "订单状态已从 pending 改为 preparing"
echo "状态流转已添加 cancelled 支持"
echo "数据库已更新"
echo ""
echo "接下来需要手动添加高级功能..."
echo ""
