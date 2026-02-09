# 支付和小票功能部署指南

## 📋 步骤1：在腾讯云服务器上添加新 API 代码

### 1.1 备份原文件
```bash
cd /var/www/restaurant-system
cp src/api/restaurant_api.py src/api/restaurant_api.py.backup
```

### 1.2 编辑 restaurant_api.py
```bash
nano src/api/restaurant_api.py
# 或使用 vi
vi src/api/restaurant_api.py
```

### 1.3 添加代码

**在文件末尾的 `if __name__ == "__main__":` 之前，添加以下代码：**

```python
# ============ 收银员支付处理 API ============
@app.post("/api/orders/{order_id}/process-payment")
async def process_payment(order_id: int, req: dict = None):
    """
    收银员处理支付（柜台支付）
    将柜台支付的订单标记为已支付
    """
    db = get_session()
    try:
        order = db.query(Orders).filter(Orders.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")

        # 检查订单是否已支付
        if order.payment_status == "paid":
            raise HTTPException(status_code=400, detail="订单已支付")

        # 更新支付状态
        order.payment_status = "paid"
        order.payment_method = order.payment_method or "counter"
        order.payment_time = datetime.now()

        # 更新订单状态为已完成
        order.order_status = "completed"

        db.commit()

        # 广播支付状态更新
        try:
            payment_data = {
                "id": order.id,
                "order_number": order.order_number,
                "store_id": order.store_id,
                "table_id": order.table_id,
                "total_amount": float(order.total_amount),
                "payment_status": "paid",
                "payment_method": order.payment_method,
                "payment_time": order.payment_time.isoformat() if order.payment_time else ""
            }
            await manager.broadcast_payment_status(order_id, payment_data)
        except Exception as ws_error:
            logger.error(f"WebSocket通知失败: {str(ws_error)}")

        return {"message": "支付处理成功", "order_status": "completed", "payment_status": "paid"}
    finally:
        db.close()


# ============ 打印小票 API ============
@app.get("/api/orders/{order_id}/receipt")
def get_order_receipt(order_id: int):
    """获取订单小票数据"""
    db = get_session()
    try:
        order = db.query(Orders).filter(Orders.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")

        # 获取桌号
        table = db.query(Tables).filter(Tables.id == order.table_id).first()
        table_number = table.table_number if table else ""

        # 获取订单项
        items = []
        for oi in order.order_items:
            items.append({
                "name": oi.menu_item_name,
                "quantity": oi.quantity,
                "price": float(oi.menu_item_price),
                "subtotal": float(oi.subtotal)
            })

        # 构建小票数据
        receipt_data = {
            "order_number": order.order_number,
            "table_number": table_number,
            "items": items,
            "total_amount": float(order.total_amount),
            "payment_method": order.payment_method or "现金",
            "payment_status": order.payment_status,
            "payment_time": order.payment_time.isoformat() if order.payment_time else "",
            "created_at": order.created_at.isoformat() if order.created_at else "",
            "store_name": "美味餐厅",
            "address": "北京市朝阳区xxx路xxx号",
            "phone": "010-12345678"
        }

        return receipt_data
    finally:
        db.close()
```

### 1.4 保存文件
- 如果使用 nano：按 `Ctrl+X`，然后按 `Y`，再按 `Enter`
- 如果使用 vi：按 `Esc`，输入 `:wq`，按 `Enter`

---

## 📋 步骤2：重启后端服务

### 2.1 找到并停止当前服务
```bash
# 查找运行中的进程
ps aux | grep restaurant_api

# 停止服务（使用上面查到的 PID）
kill <PID>
# 或者
pkill -f "python.*restaurant_api"
```

### 2.2 启动服务
```bash
cd /var/www/restaurant-system
nohup python -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
```

### 2.3 验证服务启动
```bash
# 检查进程是否运行
ps aux | grep restaurant_api

# 查看日志
tail -f logs/api.log
```

### 2.4 测试 API 是否可用
```bash
curl http://localhost:8000/api/orders/1/receipt
```

---

## 📋 步骤3：测试柜台支付功能

### 3.1 创建测试订单
```bash
# 先创建一个测试订单（如果没有的话）
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": 1,
    "table_id": 1,
    "items": [{"dish_id": 1, "quantity": 2}]
  }'
```

### 3.2 测试支付 API
```bash
# 替换 <order_id> 为实际的订单 ID
curl -X POST http://localhost:8000/api/orders/<order_id>/process-payment
```

### 3.3 验证支付结果
```bash
# 检查订单状态
curl http://localhost:8000/api/orders/<order_id>
```

**预期返回**：
```json
{
  "message": "支付处理成功",
  "order_status": "completed",
  "payment_status": "paid"
}
```

---

## 📋 步骤4：测试小票打印功能

### 4.1 获取小票数据
```bash
# 替换 <order_id> 为实际的订单 ID
curl http://localhost:8000/api/orders/<order_id>/receipt
```

### 4.2 验证小票数据
**预期返回**：
```json
{
  "order_number": "ORD20250209001",
  "table_number": "1",
  "items": [
    {
      "name": "宫保鸡丁",
      "quantity": 2,
      "price": 38.0,
      "subtotal": 76.0
    }
  ],
  "total_amount": 76.0,
  "payment_method": "counter",
  "payment_status": "paid",
  "payment_time": "2025-02-09T12:30:00",
  "created_at": "2025-02-09T12:00:00",
  "store_name": "美味餐厅",
  "address": "北京市朝阳区xxx路xxx号",
  "phone": "010-12345678"
}
```

---

## 📋 步骤5：前端功能测试

### 5.1 清除浏览器缓存
- 按 `Ctrl+Shift+Delete`
- 清除缓存和 Cookie
- 或使用 `Ctrl+F5` 强制刷新

### 5.2 打开工作人员端
访问：`http://115.191.1.219/restaurant/staff_workflow.html`

### 5.3 测试支付功能
1. 切换到"收银员"角色
2. 找到一个待支付订单（`payment_status === 'unpaid'`）
3. 点击"处理支付"按钮
4. 验证提示消息：`支付处理成功`
5. 验证订单从列表中消失

### 5.4 测试打印小票
1. 找到一个已支付的订单
2. 点击"打印小票"按钮
3. 验证小票窗口是否打开
4. 验证小票内容是否正确
5. 测试浏览器打印功能

---

## 🔍 常见问题排查

### 问题1：服务启动失败
**症状**：启动后没有进程运行
**解决方案**：
```bash
# 查看错误日志
cat logs/api.log

# 检查语法错误
python -m py_compile src/api/restaurant_api.py
```

### 问题2：API 返回 404
**症状**：访问新 API 返回 404
**解决方案**：
- 确认代码已添加到文件
- 确认服务已重启
- 检查 API 路径是否正确

### 问题3：数据库错误
**症状**：API 返回 500，日志显示数据库错误
**解决方案**：
- 检查数据库连接
- 确认 Orders、Tables 模型存在
- 确认订单 ID 存在

### 问题4：前端按钮无响应
**症状**：点击按钮没有反应
**解决方案**：
- 清除浏览器缓存
- 检查浏览器控制台错误
- 验证 API 路径是否正确

---

## ✅ 完成检查清单

完成部署后，请确认以下项目：

- [ ] 代码已添加到 restaurant_api.py
- [ ] 原文件已备份
- [ ] 服务已重启
- [ ] 服务进程正在运行
- [ ] process-payment API 可以访问
- [ ] receipt API 可以访问
- [ ] 支付功能测试通过
- [ ] 小票打印测试通过
- [ ] 前端按钮正常工作
- [ ] 没有错误日志

---

## 📊 测试记录

| 测试项 | 结果 | 备注 |
|--------|------|------|
| 服务启动 | ⬜ | |
| process-payment API | ⬜ | |
| receipt API | ⬜ | |
| 前端支付按钮 | ⬜ | |
| 前端打印按钮 | ⬜ | |
| 小票窗口显示 | ⬜ | |
| 浏览器打印 | ⬜ | |

---

**文档创建时间**：2025年2月9日
**预计部署时间**：15-20 分钟
