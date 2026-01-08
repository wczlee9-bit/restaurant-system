#!/bin/bash
#
# 创建稳定版本备份
#

VERSION="v1.0.0-stable"
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

# 4. 修复总结
echo "  - ORDER_FIX_SUMMARY.md"
if [ -f ORDER_FIX_SUMMARY.md ]; then
    cp ORDER_FIX_SUMMARY.md "${BACKUP_DIR}/"
fi

# 5. 测试脚本
echo "  - test_order_flow.py"
if [ -f test_order_flow.py ]; then
    cp test_order_flow.py "${BACKUP_DIR}/"
fi

# 创建版本信息文件
cat > "${BACKUP_DIR}/VERSION_INFO.txt" << EOF
========================================================
餐饮系统稳定版本信息
========================================================
版本号: ${VERSION}
创建时间: ${DATE}
修复内容: 订单提交WebSocket通知问题

========================================================
修改的文件列表
========================================================
1. src/api/restaurant_api.py
   - 整合WebSocket连接管理器
   - 添加WebSocket路由端点
   - 修改订单创建为异步函数，添加WebSocket通知
   - 修改订单状态更新为异步函数，添加WebSocket通知

2. assets/kitchen_display.html
   - 修复WebSocket连接URL

3. assets/staff_workflow.html
   - 修复WebSocket连接URL

4. assets/customer_order_v3.html
   - 无需修改（已使用正确的WebSocket连接逻辑）

========================================================
测试结果
========================================================
订单创建: ✓ 成功
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
  1. 顾客端选择桌号并下单
  2. 厨师端实时收到新订单通知
  3. 订单状态更新实时同步

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
