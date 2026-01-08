# 高级功能使用指南

本文档介绍扫码点餐系统的高级功能，包括支付功能、实时通信、厨房显示、会员系统和营收分析。

## 目录

1. [支付功能](#支付功能)
2. [WebSocket实时通信](#websocket实时通信)
3. [厨房显示端](#厨房显示端)
4. [会员积分系统](#会员积分系统)
5. [营收分析报表](#营收分析报表)

---

## 支付功能

### 概述

支付功能API支持多种支付方式，包括微信支付、支付宝、现金支付、信用卡等。

### 启动服务

```bash
# 设置环境变量
eval $(python /workspace/projects/scripts/load_env.py)

# 启动支付API服务 (端口8002)
PYTHONPATH=/workspace/projects/src python -m uvicorn api.payment_api:app --host 0.0.0.0 --port 8002
```

### API接口

#### 1. 获取支付方式列表

```
GET /api/payment/methods
```

**响应示例**:
```json
{
  "methods": [
    {
      "id": "wechat",
      "name": "微信支付",
      "description": "使用微信扫码支付"
    },
    {
      "id": "alipay",
      "name": "支付宝",
      "description": "使用支付宝扫码支付"
    },
    {
      "id": "cash",
      "name": "现金支付",
      "description": "现金支付，由店员确认"
    },
    {
      "id": "credit_card",
      "name": "信用卡",
      "description": "刷卡支付"
    }
  ]
}
```

#### 2. 创建支付订单

```
POST /api/payment/create
```

**请求体**:
```json
{
  "order_id": 1,
  "payment_method": "wechat",
  "customer_phone": "13800138000"
}
```

**响应示例**:
```json
{
  "payment_id": 1,
  "order_id": 1,
  "order_number": "ORD202601081200001234",
  "amount": 76.00,
  "payment_method": "wechat",
  "payment_url": "http://localhost:8000/api/payment/qr/1",
  "qr_code": "pay://fake.wechat.com?payment_id=1&amount=76.0",
  "status": "pending"
}
```

#### 3. 查询支付状态

```
GET /api/payment/{payment_id}/status
```

**响应示例**:
```json
{
  "payment_id": 1,
  "order_id": 1,
  "order_number": "ORD202601081200001234",
  "amount": 76.00,
  "payment_method": "wechat",
  "status": "success",
  "transaction_id": "TXN20260108120000123456",
  "paid_at": "2026-01-08T12:00:00"
}
```

#### 4. 支付回调

```
POST /api/payment/callback
```

**请求体**:
```json
{
  "payment_id": 1,
  "transaction_id": "TXN20260108120000123456",
  "success": true
}
```

**支付成功后自动处理**:
- 更新订单支付状态为"paid"
- 增加会员积分（消费1元 = 1积分）
- 记录积分日志

#### 5. 取消支付

```
POST /api/payment/{payment_id}/cancel
```

### 注意事项

1. 当前支付接口为模拟接口，实际使用时需要对接真实的支付API
2. 微信支付和支付宝需要配置相应的商户号和密钥
3. 现金支付需要店员确认
4. 支付成功后会自动增加会员积分

---

## WebSocket实时通信

### 概述

WebSocket服务支持订单状态和支付状态的实时推送，用于店员端和顾客端的实时更新。

### 启动服务

```bash
PYTHONPATH=/workspace/projects/src python -m uvicorn api.websocket_api:app --host 0.0.0.0 --port 8003
```

### WebSocket连接

#### 1. 店铺连接（店员端）

```
WS /ws/store/{store_id}?connection_id={connection_id}
```

**用途**: 接收新订单和订单状态更新

**消息类型**:
```json
{
  "type": "new_order",
  "order": {
    "id": 1,
    "order_number": "ORD202601081200001234",
    "table_number": "1",
    "order_status": "pending",
    ...
  },
  "timestamp": "2026-01-08T12:00:00"
}
```

```json
{
  "type": "order_status_update",
  "order": {
    "id": 1,
    "order_status": "confirmed",
    ...
  },
  "timestamp": "2026-01-08T12:05:00"
}
```

#### 2. 订单连接（顾客端）

```
WS /ws/order/{order_id}?connection_id={connection_id}
```

**用途**: 接收订单状态和支付状态更新

**消息类型**:
```json
{
  "type": "payment_status_update",
  "payment": {
    "payment_id": 1,
    "status": "success",
    ...
  },
  "timestamp": "2026-01-08T12:00:00"
}
```

#### 3. 心跳保活

客户端每30秒发送心跳：

```json
{
  "type": "ping"
}
```

服务器响应：

```json
{
  "type": "pong",
  "timestamp": "2026-01-08T12:00:00"
}
```

### 使用示例（JavaScript）

```javascript
// 店员端连接
const ws = new WebSocket('ws://localhost:8003/ws/store/1');

ws.onopen = () => {
  console.log('WebSocket连接成功');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('收到消息:', message);

  if (message.type === 'new_order') {
    // 处理新订单
    handleNewOrder(message.order);
  } else if (message.type === 'order_status_update') {
    // 更新订单状态
    updateOrderStatus(message.order);
  }
};

// 心跳保活
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'ping' }));
  }
}, 30000);
```

---

## 厨房显示端

### 概述

厨房显示端是一个实时显示订单的网页界面，用于厨房员工查看和处理订单。

### 访问页面

页面路径: `assets/kitchen_display.html`

### 功能特点

1. **实时更新**: 通过WebSocket接收新订单和状态更新
2. **订单筛选**: 按订单状态筛选（待确认、已确认、准备中、已完成）
3. **店铺切换**: 支持多店铺切换
4. **订单操作**: 快速更新订单状态
5. **新订单提醒**: 新订单有动画提示

### 启动方式

直接在浏览器中打开 `assets/kitchen_display.html`，或部署到Web服务器。

### 配置

页面默认连接的WebSocket地址是 `ws://localhost:8003`，部署时需要修改为实际地址。

```javascript
// 修改WebSocket地址
const wsUrl = `ws://your-domain.com:8003/ws/store/${storeId.value}`;
```

### 界面说明

- **头部**: 显示店铺名称和连接状态
- **控制栏**: 选择店铺、筛选订单状态
- **订单卡片**: 显示订单信息、菜品清单、状态和操作按钮
- **订单状态**:
  - 🟡 待确认
  - 🔵 已确认
  - 🟢 准备中
  - 🔴 已完成
  - 🟠 上菜中

---

## 会员积分系统

### 概述

会员积分系统支持会员注册、积分消费、积分兑换、等级管理等功能。

### 积分规则

- **消费积分**: 消费1元 = 1积分
- **积分兑换**: 可用于兑换优惠券、菜品等
- **会员等级**: 根据积分自动升级
  - 普通会员: 0积分
  - 银卡会员: 1000积分（95折）
  - 金卡会员: 5000积分（9折）
  - 白金会员: 10000积分（85折）

### 启动服务

```bash
PYTHONPATH=/workspace/projects/src python -m uvicorn api.member_api:app --host 0.0.0.0 --port 8004
```

### API接口

#### 1. 注册会员

```
POST /api/member/register
```

**请求体**:
```json
{
  "phone": "13800138000",
  "name": "张三"
}
```

**响应示例**:
```json
{
  "id": 1,
  "phone": "13800138000",
  "name": "张三",
  "level": 1,
  "level_name": "普通会员",
  "points": 0,
  "total_spent": 0,
  "total_orders": 0,
  "discount": 1.0
}
```

#### 2. 查询会员信息

```
GET /api/member/{member_id}
GET /api/member/phone/{phone}
```

#### 3. 查询积分日志

```
GET /api/member/{member_id}/points-logs?skip=0&limit=20
```

**响应示例**:
```json
[
  {
    "id": 1,
    "points": 76,
    "reason": "订单消费: ORD202601081200001234",
    "created_at": "2026-01-08T12:00:00",
    "order_number": "ORD202601081200001234"
  }
]
```

#### 4. 积分兑换

```
POST /api/member/redeem
```

**请求体**:
```json
{
  "member_id": 1,
  "points": 10,
  "reason": "积分兑换测试"
}
```

**响应示例**:
```json
{
  "message": "积分兑换成功",
  "member_id": 1,
  "redeemed_points": 10,
  "remaining_points": 66
}
```

#### 5. 应用会员折扣

```
POST /api/member/apply-discount
```

**请求体**:
```json
{
  "member_id": 1,
  "order_amount": 100.00
}
```

**响应示例**:
```json
{
  "member_id": 1,
  "original_amount": 100.00,
  "discount_amount": 5.00,
  "final_amount": 95.00,
  "discount_rate": 0.95
}
```

#### 6. 获取会员等级列表

```
GET /api/member/levels
```

**响应示例**:
```json
[
  {
    "level": 1,
    "level_name": "普通会员",
    "min_points": 0,
    "discount": 1.0
  },
  {
    "level": 2,
    "level_name": "银卡会员",
    "min_points": 1000,
    "discount": 0.95
  }
]
```

---

## 营收分析报表

### 概述

营收分析系统提供丰富的数据分析功能，包括营收汇总、支付方式统计、菜品销量、订单状态统计等。

### 启动服务

```bash
PYTHONPATH=/workspace/projects/src python -m uvicorn api.analytics_api:app --host 0.0.0.0 --port 8005
```

### API接口

#### 1. 营收汇总

```
GET /api/analytics/revenue-summary?store_id={store_id}&period={period}
```

**参数**:
- `store_id`: 店铺ID（必填）
- `period`: 时间范围 - `today`, `yesterday`, `week`, `month`, `last_month`, `custom`
- `custom_start`: 自定义开始日期 (YYYY-MM-DD)
- `custom_end`: 自定义结束日期 (YYYY-MM-DD)

**响应示例**:
```json
{
  "period": "today",
  "start_date": "2026-01-08",
  "end_date": "2026-01-08",
  "total_orders": 2,
  "total_amount": 152.00,
  "total_discount": 0.00,
  "net_revenue": 152.00,
  "average_order_amount": 76.00
}
```

#### 2. 支付方式统计

```
GET /api/analytics/payment-methods?store_id={store_id}&period={period}
```

**响应示例**:
```json
[
  {
    "payment_method": "wechat",
    "count": 1,
    "amount": 76.00,
    "percentage": 100.00
  }
]
```

#### 3. 菜品销量统计

```
GET /api/analytics/menu-item-sales?store_id={store_id}&period={period}&limit=20
```

**响应示例**:
```json
[
  {
    "menu_item_id": 1,
    "menu_item_name": "宫保鸡丁",
    "quantity": 4,
    "revenue": 152.00
  }
]
```

#### 4. 每小时销量统计

```
GET /api/analytics/hourly-sales?store_id={store_id}&period={period}
```

**响应示例**:
```json
[
  {
    "hour": 12,
    "order_count": 2,
    "revenue": 152.00
  }
]
```

#### 5. 订单状态统计

```
GET /api/analytics/order-status?store_id={store_id}&period={period}
```

**响应示例**:
```json
[
  {
    "order_status": "pending",
    "count": 2,
    "amount": 152.00
  }
]
```

#### 6. 每日营收趋势

```
GET /api/analytics/daily-revenue?store_id={store_id}&days=7
```

**响应示例**:
```json
[
  {
    "date": "2026-01-06",
    "order_count": 0,
    "revenue": 0.00
  },
  {
    "date": "2026-01-08",
    "order_count": 2,
    "revenue": 152.00
  }
]
```

#### 7. 订单排行榜

```
GET /api/analytics/top-orders?store_id={store_id}&period={period}&limit=10
```

**响应示例**:
```json
[
  {
    "order_id": 46,
    "order_number": "ORD202601080832310405",
    "table_id": 21,
    "final_amount": 76.00,
    "order_status": "pending",
    "items_count": 2
  }
]
```

---

## 完整服务启动

### 启动所有服务

```bash
# 设置环境变量
eval $(python /workspace/projects/scripts/load_env.py)

# 顾客端API (端口8000)
PYTHONPATH=/workspace/projects/src python -m uvicorn api.customer_api:app --host 0.0.0.0 --port 8000 > /tmp/customer_api.log 2>&1 &

# 店员端API (端口8001)
PYTHONPATH=/workspace/projects/src python -m uvicorn api.staff_api:app --host 0.0.0.0 --port 8001 > /tmp/staff_api.log 2>&1 &

# 支付API (端口8002)
PYTHONPATH=/workspace/projects/src python -m uvicorn api.payment_api:app --host 0.0.0.0 --port 8002 > /tmp/payment_api.log 2>&1 &

# WebSocket服务 (端口8003)
PYTHONPATH=/workspace/projects/src python -m uvicorn api.websocket_api:app --host 0.0.0.0 --port 8003 > /tmp/websocket_api.log 2>&1 &

# 会员API (端口8004)
PYTHONPATH=/workspace/projects/src python -m uvicorn api.member_api:app --host 0.0.0.0 --port 8004 > /tmp/member_api.log 2>&1 &

# 营收分析API (端口8005)
PYTHONPATH=/workspace/projects/src python -m uvicorn api.analytics_api:app --host 0.0.0.0 --port 8005 > /tmp/analytics_api.log 2>&1 &
```

### 服务端口汇总

| 服务 | 端口 | 说明 |
|------|------|------|
| 顾客端API | 8000 | 顾客扫码点餐 |
| 店员端API | 8001 | 店员订单管理 |
| 支付API | 8002 | 支付功能 |
| WebSocket服务 | 8003 | 实时通信 |
| 会员API | 8004 | 会员管理 |
| 营收分析API | 8005 | 数据分析 |

---

## 测试

运行完整功能测试：

```bash
PYTHONPATH=/workspace/projects/src python /workspace/projects/scripts/test_new_features.py
```

测试内容：
1. WebSocket服务连接
2. 支付功能（创建订单、创建支付、支付回调）
3. 会员功能（注册、查询、积分兑换、折扣计算）
4. 营收分析（营收汇总、支付方式、菜品销量、订单状态、每日趋势）

---

## 注意事项

1. **支付接口**: 当前为模拟接口，实际使用需要对接真实的支付API
2. **WebSocket连接**: 确保客户端支持WebSocket，且防火墙允许连接
3. **会员等级**: 可根据实际需求调整等级规则和折扣比例
4. **数据统计**: 分析数据基于订单表，建议定期归档历史数据
5. **性能优化**: 大数据量时建议使用数据库索引和缓存

---

## 常见问题

### Q1: 支付回调如何处理？

A: 支付回调接口为 `POST /api/payment/callback`，实际使用时需要在支付平台配置回调地址。

### Q2: WebSocket连接断开怎么办？

A: 客户端应实现自动重连机制，服务端会在连接断开时进行清理。

### Q3: 会员积分如何消费？

A: 积分可通过 `POST /api/member/redeem` 接口兑换，具体兑换规则由业务自定义。

### Q4: 营收数据实时吗？

A: 营收分析基于订单表数据，建议每隔一段时间重新查询获取最新数据。

---

## 技术支持

如有问题，请联系技术支持团队。
