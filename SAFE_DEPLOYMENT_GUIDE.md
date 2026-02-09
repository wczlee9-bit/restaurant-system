# 安全添加支付和小票 API 到腾讯云

## ⚠️ 重要：这只会添加新 API，不会修改任何现有功能

---

## 📋 步骤1：备份现有文件（必做！）

```bash
cd /var/www/restaurant-system
cp src/api/restaurant_api.py src/api/restaurant_api.py.backup_$(date +%Y%m%d_%H%M%S)
```

如果出现问题，可以随时恢复：
```bash
cp src/api/restaurant_api.py.backup_* src/api/restaurant_api.py
```

---

## 📋 步骤2：检查文件末尾是否已有新 API

```bash
cd /var/www/restaurant-system

# 检查是否已有 process-payment API
grep -n "process-payment" src/api/restaurant_api.py

# 检查是否已有 receipt API
grep -n "get_order_receipt" src/api/restaurant_api.py
```

**情况A**：如果两个命令都输出了行号
- ✅ 说明新 API 已经存在，无需添加
- 直接跳到"步骤5：重启服务"

**情况B**：如果命令没有输出
- ❌ 说明新 API 不存在，需要添加
- 继续执行"步骤3"

---

## 📋 步骤3：查看文件末尾结构

```bash
cd /var/www/restaurant-system
tail -20 src/api/restaurant_api.py
```

**你会看到类似这样的内容**：

情况1：文件末尾是 `if __name__ == "__main__":`
```python
        return receipt_data
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

情况2：文件末尾没有 `if __name__ == "__main__":`
```python
        return receipt_data
    finally:
        db.close()
```

---

## 📋 步骤4：添加新 API

### 方式1：自动添加（推荐）

```bash
cd /var/www/restaurant-system

# 创建临时文件保存新 API
cat > /tmp/new_apis.txt << 'EOF'


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

EOF

# 检查文件末尾是否有 "if __name__"
if grep -q "if __name__" src/api/restaurant_api.py; then
    # 情况1：在 if __name__ 之前插入
    sed -i '/^if __name__/e cat /tmp/new_apis.txt' src/api/restaurant_api.py
else
    # 情况2：直接追加到文件末尾
    cat /tmp/new_apis.txt >> src/api/restaurant_api.py
fi

# 验证添加成功
grep -n "process-payment\|get_order_receipt" src/api/restaurant_api.py
```

### 方式2：手动添加（如果上面的命令有问题）

```bash
cd /var/www/restaurant-system
nano src/api/restaurant_api.py
```

跳到文件末尾（`Ctrl+End`），在 `if __name__ == "__main__":` 之前粘贴新 API 代码。

---

## 📋 步骤5：验证代码语法

```bash
cd /var/www/restaurant-system
python -m py_compile src/api/restaurant_api.py
```

✅ **如果没有输出**：说明代码语法正确
❌ **如果有错误**：恢复备份文件
```bash
cp src/api/restaurant_api.py.backup_* src/api/restaurant_api.py
```

---

## 📋 步骤6：重启后端服务

```bash
cd /var/www/restaurant-system

# 1. 查找当前运行的进程
ps aux | grep restaurant_api

# 2. 记录 PID（假设是 12345）
# 3. 停止旧服务
kill <PID>
# 或
pkill -f "python.*restaurant_api"

# 4. 等待 2 秒
sleep 2

# 5. 启动新服务
nohup python -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &

# 6. 验证服务启动
ps aux | grep restaurant_api
```

✅ **如果看到进程**：说明启动成功
❌ **如果没有进程**：查看日志
```bash
tail -50 logs/api.log
```

---

## 📋 步骤7：测试新功能（不影响现有功能）

### 7.1 测试现有功能（确保没破坏）

```bash
# 测试现有的订单列表 API
curl http://localhost:8000/api/orders/

# 测试现有的店铺信息 API
curl http://localhost:8000/api/store
```

✅ **如果两个都正常**：说明现有功能没有被破坏

### 7.2 测试新功能

```bash
# 测试支付 API（替换 <order_id> 为实际订单 ID）
curl -X POST http://localhost:8000/api/orders/<order_id>/process-payment

# 测试小票 API
curl http://localhost:8000/api/orders/<order_id>/receipt
```

---

## 📋 步骤8：前端测试

1. 清除浏览器缓存（`Ctrl+Shift+Delete`）
2. 访问工作人员端：`http://115.191.1.219/restaurant/staff_workflow.html`
3. 测试收银员的"处理支付"和"打印小票"功能

---

## 🔄 回滚方案（如果有问题）

如果任何步骤出现问题，立即执行：

```bash
cd /var/www/restaurant-system

# 1. 停止服务
pkill -f "python.*restaurant_api"

# 2. 恢复备份
cp src/api/restaurant_api.py.backup_* src/api/restaurant_api.py

# 3. 重启服务
nohup python -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &

# 4. 验证服务
ps aux | grep restaurant_api
```

---

## ✅ 安全检查清单

在执行每个步骤后确认：

- [ ] 步骤1：备份文件已创建
- [ ] 步骤2：确认新 API 不存在
- [ ] 步骤3：了解文件结构
- [ ] 步骤4：代码已添加
- [ ] 步骤5：代码语法检查通过
- [ ] 步骤6：服务已重启
- [ ] 步骤7：现有功能测试通过
- [ ] 步骤7：新功能测试通过
- [ ] 步骤8：前端测试通过

---

**这个方法的优势**：
- ✅ 只在文件末尾添加新代码
- ✅ 不修改任何现有功能
- ✅ 每步都有验证
- ✅ 随时可以回滚
- ✅ 测试现有功能确保安全

**预计时间**：10-15 分钟
