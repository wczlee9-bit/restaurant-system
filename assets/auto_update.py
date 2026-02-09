#!/usr/bin/env python3
"""
服务器代码更新脚本
自动修改需要的代码
"""

import re
import sys

def update_restaurant_api():
    """更新后端API文件"""
    print("1. 更新 src/api/restaurant_api.py...")

    with open('src/api/restaurant_api.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 修改订单创建时的状态（pending → preparing）
    content = re.sub(
        r'order_status="pending".*?厨师可以开始制作',
        'order_status="preparing"  # 直接进入制作流程',
        content
    )
    content = re.sub(
        r'status="pending".*?厨师可以开始制作',
        'status="preparing"  # 直接进入制作流程',
        content
    )

    # 2. 修改订单项状态
    content = content.replace('status="pending"', 'status="preparing"')

    # 3. 更新状态流转逻辑
    # 订单状态流转
    content = re.sub(
        r"'pending': \['confirmed', 'cancelled'\]",
        "'pending': ['preparing', 'cancelled']",
        content
    )
    content = re.sub(
        r"'confirmed': \['preparing', 'cancelled'\]",
        "'confirmed': ['preparing']",
        content

    # 订单项状态流转
    content = re.sub(
        r"'pending': \['preparing'\]",
        "'pending': ['preparing', 'cancelled']",
        content
    )
    content = re.sub(
        r"'preparing': \['ready'\]",
        "'preparing': ['ready', 'cancelled']",
        content
    )

    # 4. 在菜品状态更新后添加金额计算逻辑
    # 查找 order_item.status = new_status 这一行
    pattern = r'(order_item\.status = new_status\n\s+db\.commit\(\))'
    replacement = r'''\1

        # 如果菜品被取消，重新计算订单金额
        if new_status == 'cancelled':
            # 查询该订单的所有菜品
            all_items = db.query(OrderItems).filter(OrderItems.order_id == order_id).all()
            # 只计算未取消的菜品金额
            new_total_amount = sum(item.subtotal for item in all_items if item.status != 'cancelled')
            # 更新订单金额
            order = db.query(Orders).filter(Orders.id == order_id).first()
            if order:
                order.total_amount = new_total_amount
                order.final_amount = new_total_amount  # 同时更新实付金额
                db.commit()
                logger.info(f"订单 {order.order_number} 取消菜品，金额重新计算为 {new_total_amount}")'''

    content = re.sub(pattern, replacement, content)

    # 5. 更新订单完成条件
    # 查找"检查是否所有菜品都已上菜"的部分
    pattern = r"(# 检查是否所有菜品都已上菜.*?order\.order_status = 'completed')"
    replacement = r'''# 检查是否所有菜品都已上菜或取消
        all_items = db.query(OrderItems).filter(OrderItems.order_id == order_id).all()
        all_finished = all(item.status in ['served', 'cancelled'] for item in all_items)

        if all_finished:
            # 更新订单状态为 completed，但不设置支付状态
            order = db.query(Orders).filter(Orders.id == order_id).first()
            if order and order.order_status != 'completed':
                order.order_status = 'completed'
                db.commit()
                logger.info(f"订单 {order.order_number} 所有菜品已处理（上菜或取消），订单状态更新为 completed")'''

    content = re.sub(pattern, replacement, content)

    with open('src/api/restaurant_api.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("   ✅ src/api/restaurant_api.py 更新完成")


def update_staff_workflow():
    """更新工作人员端HTML文件"""
    print("2. 更新 assets/staff_workflow.html...")

    with open('assets/staff_workflow.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 添加cancelled状态样式
    styles = ".order-item.served { border-left-color: #67c23a; background: #f0f9eb; opacity: 0.6; }"
    cancelled_style = ".order-item.cancelled { border-left-color: #909399; background: #f5f5f5; opacity: 0.4; text-decoration: line-through; }"
    content = content.replace(styles, styles + '\n' + cancelled_style)

    # 2. 添加厨师取消按钮
    # 在完成制作按钮后添加取消按钮
    finish_button = '''<el-button type="success" size="small"
                                           @click="finishCooking(order.id, item.id)"
                                           v-for="item in order.items"
                                           :key="'finish-'+item.id"
                                           v-show="item.item_status === 'preparing'">
                                    完成制作 {{ item.menu_item_name }}
                                </el-button>'''

    cancel_button = '''<el-button type="danger" size="small"
                                           @click="cancelItem(order.id, item.id)"
                                           v-for="item in order.items"
                                           :key="'cancel-'+item.id"
                                           v-show="item.item_status === 'preparing' || item.item_status === 'pending'">
                                    ❌ 缺货取消 {{ item.menu_item_name }}
                                </el-button>'''

    content = content.replace(finish_button, finish_button + '\n' + cancel_button)

    # 3. 添加传菜员通知按钮
    print_order = '''<el-button type="primary" size="small"
                                           @click="printWaiterOrder(order)"
                                           style="margin-right: 10px;">
                                    🖨️ 打印订单
                                </el-button>'''

    notify_button = '''<el-button type="primary" size="small"
                                           @click="printWaiterOrder(order)"
                                           style="margin-right: 10px;">
                                    🖨️ 打印订单
                                </el-button>
                                <el-button type="warning" size="small"
                                           @click="showCancelledItems(order)"
                                           v-if="hasCancelledItems(order)">
                                    ⚠️ 已取消菜品
                                </el-button>'''

    content = content.replace(print_order, notify_button)

    # 4. 添加 JavaScript 方法
    # 查找 allItemsServed 方法
    all_items_served = '''allItemsServed(order) {
                    return order.items.every(item => item.item_status === 'served');
                },'''

    new_methods = '''allItemsServed(order) {
                    return order.items.every(item => item.item_status === 'served');
                },

                hasCancelledItems(order) {
                    return order.items.some(item => item.item_status === 'cancelled');
                },

                showCancelledItems(order) {
                    const cancelledItems = order.items.filter(item => item.item_status === 'cancelled');
                    const itemsList = cancelledItems.map(item => `• ${item.menu_item_name} (x${item.quantity})`).join('\\n');
                    this.$alert(`以下菜品已取消，请通知顾客：\\n\\n${itemsList}`, '已取消菜品', {
                        confirmButtonText: '已通知',
                        type: 'warning'
                    });
                },'''

    content = content.replace(all_items_served, new_methods)

    # 5. 添加 cancelItem 方法
    finish_cooking = '''async finishCooking(orderId, itemId) {
                    try {
                        await axios.patch(`/restaurant/api/orders/${orderId}/items/${itemId}/status`, {
                            item_status: 'ready'
                        });
                        this.$message.success('完成制作');
                        this.loadOrders();
                    } catch (error) {
                        this.$message.error('操作失败: ' + (error.response?.data?.detail || error.message));
                    }
                },'''

    cancel_item = '''async finishCooking(orderId, itemId) {
                    try {
                        await axios.patch(`/restaurant/api/orders/${orderId}/items/${itemId}/status`, {
                            item_status: 'ready'
                        });
                        this.$message.success('完成制作');
                        this.loadOrders();
                    } catch (error) {
                        this.$message.error('操作失败: ' + (error.response?.data?.detail || error.message));
                    }
                },

                async cancelItem(orderId, itemId) {
                    try {
                        await this.$confirm('确定要取消这道菜吗？取消后将通知传菜员和顾客。', '取消菜品', {
                            confirmButtonText: '确定取消',
                            cancelButtonText: '再想想',
                            type: 'warning'
                        });

                        await axios.patch(`/restaurant/api/orders/${orderId}/items/${itemId}/status`, {
                            item_status: 'cancelled'
                        });
                        this.$message.success('菜品已取消');
                        this.loadOrders();
                    } catch (error) {
                        if (error !== 'cancel') {
                            this.$message.error('操作失败: ' + (error.response?.data?.detail || error.message));
                        }
                    }
                },'''

    content = content.replace(finish_cooking, cancel_item)

    # 6. 更新状态文本映射
    status_text = '''const textMap = {
                        'pending': '待制作',
                        'preparing': '制作中',
                        'ready': '待传菜',
                        'served': '已上菜'
                    };'''

    new_status_text = '''const textMap = {
                        'pending': '待制作',
                        'preparing': '制作中',
                        'ready': '待传菜',
                        'served': '已上菜',
                        'cancelled': '已取消'
                    };'''

    content = content.replace(status_text, new_status_text)

    with open('assets/staff_workflow.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("   ✅ assets/staff_workflow.html 更新完成")


def update_order_detail():
    """更新订单详情页面"""
    print("3. 更新 frontend/customer/order/order-detail.html...")

    try:
        with open('frontend/customer/order/order-detail.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. 修改菜品状态文本
        status_map = '''const statusMap = {
                'pending': '待制作',
                'preparing': '制作中',
                'ready': '待传菜',
                'serving': '上菜中',
                'served': '已上菜'
            };'''

        new_status_map = '''const statusMap = {
                'pending': '待制作',
                'preparing': '制作中',
                'ready': '待传菜',
                'serving': '上菜中',
                'served': '已上菜',
                'cancelled': '已取消（缺货）'
            };'''

        content = content.replace(status_map, new_status_map)

        # 2. 修改渲染菜品的方法，添加cancelled样式
        render_pattern = r'''<div class="order-item">\s*<div class="order-item-name">\$\{item\.menu_item_name\}</div>\s*<div class="order-item-qty">x\$\{item\.quantity\}</div>\s*<div class="order-item-price">¥\$\{item\.subtotal\.toFixed\(2\)\}</div>\s*</div>'''

        new_render = '''<div class="order-item" style="${item.item_status === 'cancelled' ? 'text-decoration: line-through; opacity: 0.5; color: #999;' : ''}">\
                        <div class="order-item-name">${item.menu_item_name}</div>\
                        <div class="order-item-qty">x${item.quantity}</div>\
                        <div class="order-item-price">¥${item.subtotal.toFixed(2)}</div>\
                    </div>'''

        # 使用更精确的替换
        content = re.sub(
            r'''<div class="order-item">\n\s+<div class="order-item-name">\$\{item\.menu_item_name\}</div>\n\s+<div class="order-item-qty">x\$\{item\.quantity\}</div>\n\s+<div class="order-item-price">¥\$\{item\.subtotal\.toFixed\(2\)\}</div>\n\s+</div>''',
            new_render,
            content,
            flags=re.MULTILINE
        )

        with open('frontend/customer/order/order-detail.html', 'w', encoding='utf-8') as f:
            f.write(content)

        print("   ✅ frontend/customer/order/order-detail.html 更新完成")
    except FileNotFoundError:
        print("   ⚠️  文件不存在，跳过")


def update_database():
    """更新数据库"""
    print("4. 更新数据库...")

    # 创建SQL脚本
    sql = """-- 更新订单状态
UPDATE orders SET order_status = 'preparing' WHERE order_status = 'pending';
-- 更新订单项状态
UPDATE order_items SET status = 'preparing' WHERE status = 'pending';
-- 显示结果
SELECT order_status, COUNT(*) FROM orders GROUP BY order_status;
SELECT status, COUNT(*) FROM order_items GROUP BY status;
"""

    with open('/tmp/update_db.sql', 'w') as f:
        f.write(sql)

    import os
    os.system('sudo -u postgres psql -d restaurant_system < /tmp/update_db.sql')

    print("   ✅ 数据库更新完成")


def restart_service():
    """重启后端服务"""
    print("5. 重启后端服务...")

    import os
    os.system('pkill -f "uvicorn.*restaurant_api"')
    os.system('sleep 2')
    os.system('cd /var/www/restaurant-system && nohup python3 -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000 > /var/log/restaurant_api.log 2>&1 &')
    os.system('sleep 3')

    print("   ✅ 后端服务重启完成")


if __name__ == '__main__':
    import os
    os.chdir('/var/www/restaurant-system')

    print("=" * 50)
    print("  开始更新代码...")
    print("=" * 50)
    print()

    try:
        update_restaurant_api()
        update_staff_workflow()
        update_order_detail()
        update_database()
        restart_service()

        print()
        print("=" * 50)
        print("  更新完成！")
        print("=" * 50)
        print()
        print("请强制刷新浏览器缓存：Ctrl+F5")
        print("然后测试新功能：")
        print("  - 创建新订单（状态应为preparing）")
        print("  - 厨师取消菜品")
        print("  - 传菜员查看通知")
        print("  - 顾客查看订单详情")
        print("  - 收银员支付")
        print()

    except Exception as e:
        print(f"❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
