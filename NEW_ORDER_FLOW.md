# 新的两步订单流程实现总结

## 需求说明
顾客下单流程改为两步：
1. **确认下单**：顾客提交订单（不选择支付方式），厨师可以开始制作
2. **确认支付**：顾客选择支付方式（马上支付或柜台支付），确认支付

## 流程设计

### 原流程
```
顾客选择桌号 → 添加菜品 → 选择支付方式 → 提交订单 → 厨师收到
```

### 新流程
```
顾客选择桌号 → 添加菜品 → 确认下单 → 厨师收到并制作 → 选择支付方式 → 确认支付
```

## 后端修改

### 1. 修改订单创建逻辑（restaurant_api.py）

#### CreateOrderRequest 模型
```python
class CreateOrderRequest(BaseModel):
    """创建订单请求（第一步：确认下单）"""
    table_id: int
    items: List[OrderItemRequest]
    # payment_method 将在第二步支付时设置，这里不需要
```

#### OrderResponse 模型
```python
class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    order_number: str  # 新增
    store_id: int
    table_id: int
    table_number: str
    total_amount: float
    payment_method: str
    payment_status: str  # 新增
    status: str
    created_at: str
    items: List[OrderItemResponse]
```

#### create_order 函数
- 修改为异步函数：`async def create_order(...)`
- 订单创建时不处理支付：
  - `payment_method=""`（空字符串）
  - `payment_status="unpaid"`
  - `order_status="pending"`
- 广播新订单到厨师端

### 2. 添加确认支付接口（restaurant_api.py）

#### ConfirmPaymentRequest 模型
```python
class ConfirmPaymentRequest(BaseModel):
    """确认支付请求（第二步：确认支付）"""
    payment_method: str = Field(..., description="支付方式：immediate(马上支付) 或 counter(柜台支付)")
```

#### confirm_payment 函数
```python
@app.post("/api/orders/{order_id}/confirm-payment")
async def confirm_payment(order_id: int, req: ConfirmPaymentRequest):
    """
    确认支付（第二步）
    顾客选择支付方式后调用此接口
    """
    # 根据支付方式设置支付状态
    if req.payment_method == "immediate":
        order.payment_status = "paid"  # 马上支付：标记为已支付
    elif req.payment_method == "counter":
        order.payment_status = "unpaid"  # 柜台支付：保持未支付状态
    
    # 广播支付状态更新到厨师端
    await manager.broadcast_payment_status(order_id, order_data)
```

### 3. 添加WebSocket广播方法

#### broadcast_payment_status 方法
```python
async def broadcast_payment_status(self, order_id: int, payment_data: dict):
    """广播支付状态更新"""
    message = {
        "type": "payment_status_update",
        "payment": payment_data,
        "timestamp": datetime.now().isoformat()
    }
    
    # 推送到店铺
    if "store_id" in payment_data:
        await self.broadcast_to_store(payment_data["store_id"], message)
    
    # 推送到订单
    await self.broadcast_to_order(order_id, message)
```

## 前端修改

### 1. 修改购物车弹窗结构

#### 原结构
- 步骤1：确认订单信息
- 步骤2：选择支付方式
- 点击"立即支付"或"确认下单"提交订单

#### 新结构
- 步骤1：确认订单信息
- 点击"确认下单"提交订单
- 弹出支付弹窗（新增）
- 选择支付方式
- 点击"立即支付"或"确认支付（餐后柜台）"确认支付

### 2. 修改数据属性

```javascript
data() {
    return {
        ...
        showCartStep1: false,
        showPaymentModal: false,  // 改为支付弹窗（原showCartStep2）
        currentOrder: null,
        paymentMethod: '',
        ...
    };
}
```

### 3. 修改方法

#### submitOrder 方法（第一步：确认下单）
```javascript
async submitOrder() {
    // 构造订单数据（不含支付方式）
    const orderData = {
        table_id: this.selectedTable.id,
        items: this.cart.map(item => ({
            menu_item_id: item.id,
            quantity: item.qty,
            special_instructions: ''
        }))
    };
    
    // 提交订单
    const response = await axios.post('/api/orders/', orderData);
    
    // 保存当前订单信息
    this.currentOrder = {
        ...response.data,
        order_id: response.data.order_number || response.data.id,
        created_at: response.data.created_at
    };
    
    // 清空购物车
    this.cart = [];
    
    // 关闭购物车弹窗，显示支付弹窗
    this.showCartStep1 = false;
    this.showPaymentModal = true;
    
    this.$message.success(`订单提交成功！订单号：${this.currentOrder.order_id}`);
}
```

#### confirmPayment 方法（第二步：确认支付）
```javascript
async confirmPayment() {
    // 调用确认支付接口
    const response = await axios.post(`/api/orders/${this.currentOrder.id}/confirm-payment`, {
        payment_method: this.paymentMethod
    });
    
    // 更新当前订单信息
    this.currentOrder.payment_method = response.data.payment_method;
    this.currentOrder.payment_status = response.data.payment_status;
    
    // 关闭支付弹窗
    this.closePaymentModal();
    
    const paymentText = this.paymentMethod === 'immediate' ? '支付成功' : '已选择餐后柜台支付';
    this.$message.success(`${paymentText}！订单号：${this.currentOrder.order_id}`);
}
```

## 测试结果

```
============================================================
新的两步订单流程测试
第一步：确认下单 → 厨师开始制作
第二步：确认支付 → 选择支付方式
============================================================

WebSocket连接成功

第一步：提交订单（不选择支付方式）
✓ 订单提交成功！
  订单ID: 62
  订单号: ORD202601090841187861
  支付方式: 未选择
  支付状态: unpaid
  订单状态: pending

✓✓✓ 收到消息 1: new_order
  厨师端收到新订单通知

第二步：确认支付（选择counter支付）
✓ 确认支付成功！
  订单ID: 62
  支付方式: counter
  支付状态: unpaid

✓✓✓ 收到消息 2: payment_status_update
  厨师端收到支付状态更新

============================================================
测试结果总结
============================================================
第一步（提交订单）: ✓ 成功
第二步（确认支付）: ✓ 成功

✓✓✓ 新的两步订单流程测试通过！
```

## 订单状态流转

### 订单创建（第一步）
- `order_status`: `pending`（待制作）
- `payment_status`: `unpaid`（未支付）
- `payment_method`: `""`（未选择）
- 厨师端收到新订单通知，可以开始制作

### 确认支付（第二步）

#### 马上支付（immediate）
- `order_status`: `pending`（保持待制作状态）
- `payment_status`: `paid`（已支付）
- `payment_method`: `immediate`（马上支付）
- 厨师端收到支付状态更新

#### 柜台支付（counter）
- `order_status`: `pending`（保持待制作状态）
- `payment_status`: `unpaid`（保持未支付状态）
- `payment_method`: `counter`（柜台支付）
- 厨师端收到支付状态更新
- 顾客餐后到收银台支付

## API接口列表

### 1. 创建订单（第一步）
```
POST /api/orders/
Content-Type: application/json

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
```

**响应**：
```json
{
  "id": 62,
  "order_number": "ORD202601090841187861",
  "store_id": 2,
  "table_id": 55,
  "table_number": "8",
  "total_amount": 108.0,
  "payment_method": "",
  "payment_status": "unpaid",
  "status": "pending",
  "created_at": "2026-01-09T08:41:18.845553+08:00",
  "items": [...]
}
```

### 2. 确认支付（第二步）
```
POST /api/orders/{order_id}/confirm-payment
Content-Type: application/json

{
  "payment_method": "counter"
}
```

**响应**：
```json
{
  "message": "支付确认成功",
  "order_id": 62,
  "payment_method": "counter",
  "payment_status": "unpaid"
}
```

## WebSocket消息类型

### 1. 新订单通知
```json
{
  "type": "new_order",
  "order": {
    "id": 62,
    "order_number": "ORD202601090841187861",
    "store_id": 2,
    "table_id": 55,
    "table_number": "8",
    "total_amount": 108.0,
    "payment_method": "",
    "payment_status": "unpaid",
    "status": "pending",
    "created_at": "2026-01-09T08:41:18.845553+08:00",
    "items": [...]
  },
  "timestamp": "2026-01-09T08:41:18.931294"
}
```

### 2. 支付状态更新
```json
{
  "type": "payment_status_update",
  "payment": {
    "id": 62,
    "order_number": "ORD202601090841187861",
    "store_id": 2,
    "table_id": 55,
    "total_amount": 108.0,
    "payment_method": "counter",
    "payment_status": "unpaid",
    "status": "pending",
    "created_at": "2026-01-09T08:41:18.845553+08:00"
  },
  "timestamp": "2026-01-09T08:41:20.991493"
}
```

## 优势

1. **提升用户体验**：顾客可以先下单，让厨师开始制作，不需要等待支付完成
2. **灵活支付选择**：顾客可以在下单后选择支付方式，更方便
3. **实时状态同步**：订单状态和支付状态实时同步到厨师端
4. **支持多种支付方式**：支持马上支付和柜台支付两种方式
5. **厨师不受支付影响**：厨师可以在顾客选择支付方式前就开始制作菜品

## 注意事项

1. **订单创建时不扣库存**：当前实现中，订单创建时会扣减库存。如果需要，可以修改为确认支付时才扣库存。
2. **支付状态追踪**：柜台支付时，需要收银员在收银系统中确认收款，然后更新支付状态为 `paid`。
3. **订单取消**：如果顾客在下单后但确认支付前取消订单，需要释放已扣减的库存。

## 后续优化建议

1. **添加支付超时机制**：如果顾客长时间不确认支付，可以提示或自动取消订单
2. **添加支付方式提示**：在支付弹窗中显示不同支付方式的说明和注意事项
3. **添加订单倒计时**：显示订单提交时间，提醒顾客及时支付
4. **优化厨师端界面**：在厨师端显示支付状态，方便判断订单是否已支付
5. **添加支付记录**：记录支付时间和方式，便于财务对账
