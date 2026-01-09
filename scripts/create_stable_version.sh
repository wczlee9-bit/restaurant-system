#!/bin/bash
#
# 创建稳定版本备份
#

VERSION="v1.1.0-new-flow"
BACKUP_DIR="/tmp/restaurant_system_backup_${VERSION}"
DATE=$(date +%Y%m%d_%H%M%S)

echo "=========================================================="
echo "创建餐饮系统稳定版本备份 - ${VERSION}"
echo "备份目录: ${BACKUP_DIR}"
echo "=========================================================="
echo ""

# 创建备份目录
mkdir -p "${BACKUP_DIR}"

# 备份关键文件
echo "备份关键文件..."

# 1. 后端API
echo "  - restaurant_api.py"
cp src/api/restaurant_api.py "${BACKUP_DIR}/"

# 2. 前端页面
echo "  - customer_order_v3.html"
cp assets/customer_order_v3.html "${BACKUP_DIR}/"

echo "  - kitchen_display.html"
cp assets/kitchen_display.html "${BACKUP_DIR}/"

echo "  - staff_workflow.html"
cp assets/staff_workflow.html "${BACKUP_DIR}/"

# 3. 配置文件
echo "  - netlify.toml"
if [ -f netlify.toml ]; then
    cp netlify.toml "${BACKUP_DIR}/"
fi

# 4. 文档
echo "  - NEW_ORDER_FLOW.md"
if [ -f NEW_ORDER_FLOW.md ]; then
    cp NEW_ORDER_FLOW.md "${BACKUP_DIR}/"
fi

echo "  - VERSION_CHANGELOG.md"
if [ -f VERSION_CHANGELOG.md ]; then
    cp VERSION_CHANGELOG.md "${BACKUP_DIR}/"
fi

# 5. 测试脚本
echo "  - test_new_flow.py"
if [ -f test_new_flow.py ]; then
    cp test_new_flow.py "${BACKUP_DIR}/"
fi

# 创建版本信息文件
cat > "${BACKUP_DIR}/VERSION_INFO.txt" << EOF
========================================================
餐饮系统稳定版本信息
========================================================
版本号: ${VERSION}
创建时间: ${DATE}
主要功能: 新的两步订单流程（确认下单→确认支付）

========================================================
v1.1.0 修改内容
========================================================

1. 后端API (src/api/restaurant_api.py)
   - 修改 CreateOrderRequest 模型：移除 payment_method 字段
   - 修改 OrderResponse 模型：添加 order_number 和 payment_status 字段
   - 修改 create_order 函数：
     * 改为异步函数
     * 订单创建时不处理支付
     * 添加WebSocket广播通知
   - 新增 ConfirmPaymentRequest 模型
   - 新增 confirm_payment 函数：确认支付接口
   - 新增 broadcast_payment_status 方法：广播支付状态更新

2. 前端页面 (assets/customer_order_v3.html)
   - 修改购物车弹窗结构：
     * 步骤1：确认订单信息
     * 新增支付弹窗：选择支付方式
   - 修改 data() 部分：将 showCartStep2 改为 showPaymentModal
   - 修改 submitOrder 方法：只提交订单，不处理支付
   - 新增 confirmPayment 方法：确认支付
   - 修改按钮逻辑：确认下单后显示支付弹窗

========================================================
v1.0.0 修改内容（参考）
========================================================

1. 后端API (src/api/restaurant_api.py)
   - 整合WebSocket连接管理器（ConnectionManager）
   - 添加WebSocket路由端点（店铺、订单、桌号）
   - 修改订单创建函数为异步，添加WebSocket通知
   - 修改订单状态更新函数为异步，添加WebSocket通知

2. 前端页面 (assets/kitchen_display.html, assets/staff_workflow.html)
   - 修复WebSocket连接URL

========================================================
v1.1.0 功能说明
========================================================

新的两步订单流程：

第一步：确认下单
- 顾客提交订单（不选择支付方式）
- 厨师端实时收到新订单通知
- 厨师可以开始制作菜品
- 订单状态：pending
- 支付状态：unpaid

第二步：确认支付
- 顾客选择支付方式（马上支付或柜台支付）
- 支付状态实时更新到厨师端
- 马上支付：payment_status = paid
- 柜台支付：payment_status = unpaid（餐后到收银台支付）

========================================================
v1.1.0 测试结果
========================================================

第一步（提交订单）: ✓ 成功
第二步（确认支付）: ✓ 成功
WebSocket通知: ✓ 成功
订单流程测试: ✓ 通过

========================================================
部署说明
========================================================

后端服务:
  cd /workspace/projects/src
  python -m uvicorn api.restaurant_api:app --host 0.0.0.0 --port 8000

前端部署:
  使用拖拽部署方式将assets/目录上传到Netlify

验证步骤:
  1. 顾客端选择桌号并添加菜品
  2. 顾客点击"确认下单"，厨师端收到新订单
  3. 厨师开始制作菜品
  4. 顾客选择支付方式并确认支付
  5. 厨师端收到支付状态更新

========================================================
API接口列表
========================================================

1. 创建订单（第一步）
   POST /api/orders/
   {
     "table_id": 55,
     "items": [
       {
         "menu_item_id": 1,
         "quantity": 2,
         "special_instructions": "少放辣"
       }
     ]
   }

2. 确认支付（第二步）
   POST /api/orders/{order_id}/confirm-payment
   {
     "payment_method": "counter"
   }

========================================================
WebSocket消息类型
========================================================

1. 新订单通知
   {
     "type": "new_order",
     "order": {...},
     "timestamp": "2026-01-09T08:41:18.931294"
   }

2. 支付状态更新
   {
     "type": "payment_status_update",
     "payment": {...},
     "timestamp": "2026-01-09T08:41:20.991493"
   }

========================================================
优势
========================================================

1. 提升用户体验：顾客可以先下单，让厨师开始制作
2. 灵活支付选择：顾客可以在下单后选择支付方式
3. 实时状态同步：订单状态和支付状态实时同步
4. 厨师不受支付影响：厨师可以在顾客选择支付方式前开始制作

========================================================
注意事项
========================================================

1. 订单创建时会扣减库存
2. 柜台支付需要收银员在收银系统中确认收款
3. 如需在确认支付时才扣库存，需要进一步修改

========================================================
恢复方法
========================================================

  cp ${BACKUP_DIR}/restaurant_api.py src/api/
  cp ${BACKUP_DIR}/*.html assets/

========================================================
EOF

echo ""
echo "=========================================================="
echo "备份完成！"
echo "备份目录: ${BACKUP_DIR}"
echo ""
echo "恢复方法:"
echo "  cp ${BACKUP_DIR}/restaurant_api.py src/api/"
echo "  cp ${BACKUP_DIR}/*.html assets/"
echo "=========================================================="
