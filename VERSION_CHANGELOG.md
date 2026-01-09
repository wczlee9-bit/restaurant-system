# 餐饮系统版本更新日志

## 版本 v1.1.0 - 两步订单流程

### 更新时间
2026-01-09

### 主要功能
实现新的两步订单流程：确认下单 → 确认支付

### 功能描述
- **第一步：确认下单**
  - 顾客提交订单（不选择支付方式）
  - 厨师端实时收到新订单通知
  - 厨师可以开始制作菜品

- **第二步：确认支付**
  - 顾客选择支付方式（马上支付或柜台支付）
  - 支付状态实时更新到厨师端
  - 马上支付：标记为已支付
  - 柜台支付：保持未支付状态，餐后到收银台支付

### 修改的文件

#### 后端文件
1. `src/api/restaurant_api.py`
   - 修改 `CreateOrderRequest` 模型：移除 `payment_method` 字段
   - 修改 `OrderResponse` 模型：添加 `order_number` 和 `payment_status` 字段
   - 修改 `create_order` 函数：
     - 改为异步函数
     - 订单创建时不处理支付
     - 添加WebSocket广播通知
   - 新增 `ConfirmPaymentRequest` 模型
   - 新增 `confirm_payment` 函数：确认支付接口
   - 新增 `broadcast_payment_status` 方法：广播支付状态更新

#### 前端文件
1. `assets/customer_order_v3.html`
   - 修改购物车弹窗结构：
     - 步骤1：确认订单信息
     - 新增支付弹窗：选择支付方式
   - 修改 `data()` 部分：将 `showCartStep2` 改为 `showPaymentModal`
   - 修改 `submitOrder` 方法：只提交订单，不处理支付
   - 新增 `confirmPayment` 方法：确认支付
   - 修改按钮逻辑：确认下单后显示支付弹窗

### 新增API接口
```
POST /api/orders/{order_id}/confirm-payment
```

### WebSocket消息类型
- `new_order`：新订单通知
- `payment_status_update`：支付状态更新

### 测试结果
```
第一步（提交订单）: ✓ 成功
第二步（确认支付）: ✓ 成功
WebSocket通知: ✓ 成功
```

### 优势
1. 提升用户体验：顾客可以先下单，让厨师开始制作
2. 灵活支付选择：顾客可以在下单后选择支付方式
3. 实时状态同步：订单状态和支付状态实时同步
4. 厨师不受支付影响：厨师可以在顾客选择支付方式前开始制作

### 注意事项
1. 订单创建时会扣减库存
2. 柜台支付需要收银员在收银系统中确认收款
3. 如需在确认支付时才扣库存，需要进一步修改

### 版本兼容性
- 与 v1.0.0 兼容
- 数据库模型无变化
- 厨师端和工作人员端无需修改

### 部署说明
1. 后端服务：
   ```bash
   cd /workspace/projects/src
   python -m uvicorn api.restaurant_api:app --host 0.0.0.0 --port 8000
   ```

2. 前端部署：
   - 将更新后的 `customer_order_v3.html` 部署到Netlify
   - 自动适配WebSocket连接

### 文档
- 详细文档：`NEW_ORDER_FLOW.md`
- 测试脚本：`test_new_flow.py`

---

## 版本 v1.0.0 - 订单提交问题修复

### 更新时间
2026-01-08

### 主要功能
修复订单提交后厨师端无法看到订单的问题

### 修改的文件
1. `src/api/restaurant_api.py`：整合WebSocket服务
2. `assets/kitchen_display.html`：修复WebSocket连接
3. `assets/staff_workflow.html`：修复WebSocket连接

### 测试结果
- 订单创建：成功
- WebSocket通知：成功
- 订单流程测试：通过
