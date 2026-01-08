# 订单提交问题修复总结

## 问题描述
顾客下单后，厨师端无法看到新订单，导致订单无法处理。

## 问题根因分析

### 1. WebSocket服务分离问题
- 原本WebSocket服务运行在独立的 `websocket_api.py` 中
- 订单创建API在 `restaurant_api.py` 中
- 两个服务运行在不同端口，无法共享连接状态

### 2. WebSocket通知缺失
- `restaurant_api.py` 的订单创建函数中没有调用WebSocket通知
- 订单虽然创建成功，但没有通知到厨师端

### 3. WebSocket端点配置错误
- 工作人员端页面连接的WebSocket端口不正确：
  - `kitchen_display.html`: 连接到 `ws://localhost:8003`
  - `staff_workflow.html`: 连接到 `ws://localhost:8001`
  - 实际WebSocket服务应运行在8000端口

### 4. 异步调用错误
- 原本使用 `loop.run_until_complete()` 在同步函数中调用异步WebSocket方法
- 导致错误："There is no current event loop in thread 'AnyIO worker thread'"

## 修复方案

### 1. 整合WebSocket服务到restaurant_api
- 将 `websocket_api.py` 中的 `ConnectionManager` 类复制到 `restaurant_api.py`
- 添加WebSocket路由端点：
  - `/ws/store/{store_id}` - 店铺连接（厨师端使用）
  - `/ws/order/{order_id}` - 订单连接（顾客端使用）
  - `/ws/table/{table_id}` - 桌号连接（顾客端使用）

### 2. 添加订单创建WebSocket通知
修改 `create_order` 函数：
- 将函数改为异步 `async def create_order(...)`
- 在 `db.commit()` 后添加WebSocket通知：
  ```python
  await manager.broadcast_new_order(order_data)
  ```

### 3. 添加订单状态更新WebSocket通知
修改 `update_order_status` 和 `update_order_item_status` 函数：
- 将函数改为异步
- 在状态更新后调用 `await manager.broadcast_order_status(order_id, order_data)`

### 4. 修复工作人员端WebSocket连接
修改以下文件的WebSocket URL：
- `kitchen_display.html`
- `staff_workflow.html`

统一使用：
```javascript
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsHost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'localhost:8000' 
    : `${window.location.hostname}:8000`;
const wsUrl = `${wsProtocol}//${wsHost}/ws/store/${storeId}`;
```

## 修改的文件

### 后端文件
1. `src/api/restaurant_api.py`
   - 添加WebSocket连接管理器（ConnectionManager）
   - 添加WebSocket路由端点
   - 修改订单创建函数为异步，添加WebSocket通知
   - 修改订单状态更新函数为异步，添加WebSocket通知

### 前端文件
1. `assets/kitchen_display.html`
   - 修改WebSocket连接URL，使用8000端口

2. `assets/staff_workflow.html`
   - 修改WebSocket连接URL，使用8000端口

## 测试结果

### 测试场景：顾客下单 → 厨师接收

```
============================================================
订单流程测试 - 顾客下单 → 厨师接收
============================================================
获取店铺和桌号信息...
店铺ID: 2
桌号ID: 55, 桌号: 8

==================================================
测试WebSocket连接...
==================================================
连接到: ws://localhost:8000/ws/store/2
✓ WebSocket连接成功
✓ 收到消息: {'type': 'connected', 'message': '连接成功', 'store_id': 2, ...}

等待新订单消息...

==================================================
创建测试订单...
==================================================
订单数据: {...}
✓ 订单创建成功！

==================================================
✓✓✓ 收到新订单消息！
==================================================
{
  "type": "new_order",
  "order": {
    "id": 58,
    "order_number": "ORD202601082348473567",
    "store_id": 2,
    "table_id": 55,
    "table_number": "8",
    "total_amount": 108.0,
    "payment_method": "counter",
    "payment_status": "paid",
    "status": "pending",
    "created_at": "2026-01-08T23:48:47.749848+08:00",
    "items": [...]
  },
  "timestamp": "2026-01-08T23:48:47.846463"
}

============================================================
测试结果总结
============================================================
订单创建: ✓ 成功
WebSocket通知: ✓ 成功

✓✓✓ 订单流程测试通过！
```

## 部署说明

### 后端服务
- 确保运行 `restaurant_api.py` 在8000端口：
  ```bash
  cd /workspace/projects/src
  python -m uvicorn api.restaurant_api:app --host 0.0.0.0 --port 8000
  ```

### 前端部署
- 前端HTML文件已更新WebSocket连接逻辑
- 无需额外配置，会自动检测环境并连接到正确的WebSocket端点

### Netlify配置
- 确保 `netlify.toml` 中的API代理指向8000端口
- WebSocket连接通过API代理自动转发

## 验证步骤

1. 启动后端服务
2. 打开顾客端页面选择桌号
3. 添加菜品到购物车并提交订单
4. 打开厨师端页面
5. 验证厨师端是否能实时收到新订单通知

## 注意事项

1. **服务端口**：restaurant_api必须运行在8000端口
2. **WebSocket连接**：工作人员端会自动连接到正确的WebSocket端点
3. **数据库**：确保数据库中有店铺和桌号数据
4. **测试数据**：使用test_order_flow.py进行完整测试

## 后续优化建议

1. 添加WebSocket连接重连机制
2. 添加心跳保活机制
3. 实现WebSocket消息确认机制
4. 添加断线重连后的数据同步
5. 实现更细粒度的角色权限控制（不同角色接收不同类型的订单）
