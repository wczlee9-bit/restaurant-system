#!/bin/bash

echo "======================================"
echo "  手动更新脚本"
echo "======================================"
echo ""

cd /var/www/restaurant-system

echo "1. 备份原文件..."
cp src/api/restaurant_api.py src/api/restaurant_api.py.backup_$(date +%Y%m%d_%H%M%S)
cp assets/staff_workflow.html assets/staff_workflow.html.backup_$(date +%Y%m%d_%H%M%S)
echo "✅ 备份完成"
echo ""

echo "2. 修改订单创建逻辑（pending → preparing）..."
# 查找并替换
sed -i 's/order_status="pending".*厨师可以开始制作/order_status="preparing"  # 直接进入制作流程/' src/api/restaurant_api.py
sed -i 's/status="pending"/status="preparing"/g' src/api/restaurant_api.py
echo "✅ 订单创建逻辑修改完成"
echo ""

echo "3. 添加菜品取消功能到状态流转..."
# 需要检查是否已经有cancelled状态
if grep -q "'preparing': \['ready'" src/api/restaurant_api.py; then
    sed -i "s/'preparing': \['ready'/'preparing': ['ready', 'cancelled']/" src/api/restaurant_api.py
fi
if grep -q "'pending': \['confirmed'" src/api/restaurant_api.py; then
    sed -i "s/'pending': \['confirmed'/'pending': ['preparing', 'cancelled']/" src/api/restaurant_api.py
fi
echo "✅ 状态流转修改完成"
echo ""

echo "4. 添加菜品取消后的金额计算逻辑..."
# 需要在order_item.status更新后添加金额计算
# 这个比较复杂，需要手动添加Python代码
echo "⚠️ 需要手动添加金额计算逻辑"
echo ""

echo "5. 添加订单完成条件（支持cancelled状态）..."
# 检查是否需要更新订单完成逻辑
echo "⚠️ 需要手动更新订单完成逻辑"
echo ""

echo "6. 添加前端厨师取消按钮..."
# 这个需要手动添加HTML
echo "⚠️ 需要手动添加厨师取消按钮"
echo ""

echo "======================================"
echo "  需要手动完成以下操作："
echo "======================================"
echo ""
echo "1. 在 src/api/restaurant_api.py 的 update_order_item_status 函数中添加："
echo "   - 如果菜品状态变为 cancelled，重新计算订单金额"
echo "   - 更新订单完成条件（支持cancelled状态）"
echo ""
echo "2. 在 assets/staff_workflow.html 中添加："
echo "   - 厨师端取消按钮"
echo "   - cancelItem 方法"
echo "   - 传菜员通知功能"
echo ""
echo "3. 在 frontend/customer/order/order-detail.html 中添加："
echo "   - 显示已取消菜品（灰色删除线）"
echo ""
echo "详细修改内容请查看：assets/手动修改指南.md"
echo ""
