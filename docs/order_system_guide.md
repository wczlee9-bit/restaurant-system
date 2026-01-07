# 扫码点餐系统使用指南

## 概述

扫码点餐系统是一个完整的多店铺餐饮管理系统，支持顾客扫码点餐、订单管理、库存管理等功能。本文档将详细介绍系统的使用方法。

## 系统架构

### 技术栈
- **后端**: Python + FastAPI
- **前端**: Vue 3 + Element Plus
- **数据库**: PostgreSQL
- **对象存储**: S3
- **大模型**: 豆包大模型（可选，用于智能推荐）

### 核心组件
1. **顾客端API** (端口8000): 顾客扫码点餐相关接口
2. **店员端API** (端口8001): 店员订单管理接口
3. **H5点餐页面**: 顾客使用的移动端网页
4. **二维码生成工具**: 为桌号生成二维码

## 快速开始

### 1. 启动API服务

```bash
# 设置环境变量
eval $(python /workspace/projects/scripts/load_env.py)

# 启动顾客端API (端口8000)
PYTHONPATH=/workspace/projects/src python -m uvicorn api.customer_api:app --host 0.0.0.0 --port 8000

# 启动店员端API (端口8001)
PYTHONPATH=/workspace/projects/src python -m uvicorn api.staff_api:app --host 0.0.0.0 --port 8001
```

或使用启动脚本：

```bash
python /workspace/projects/scripts/start_api_services.py
```

### 2. 生成二维码

```python
from tools.qrcode_tool import QRCodeGenerator

generator = QRCodeGenerator()

# 为单个桌号生成二维码
result = generator.generate_qrcode_for_table(
    table_id=1,
    base_url="http://your-domain.com/order"
)

# 为店铺所有桌号生成二维码
results = generator.generate_qrcodes_for_store(
    store_id=1,
    base_url="http://your-domain.com/order"
)
```

### 3. 顾客扫码点餐

1. 顾客扫描桌号二维码
2. 进入H5点餐页面（`assets/order.html`）
3. 浏览菜品、加入购物车
4. 提交订单

### 4. 店员管理订单

店员通过店员端API进行订单管理：
- 查看订单列表
- 确认订单
- 更新订单状态

## API接口文档

### 顾客端API (端口8000)

#### 1. 获取店铺信息

```
GET /api/customer/shop?store_id={store_id}
```

**响应示例**:
```json
{
  "id": 1,
  "name": "测试餐厅",
  "address": "北京市朝阳区",
  "phone": "010-12345678",
  "opening_hours": {"start": "09:00", "end": "22:00"}
}
```

#### 2. 获取菜品列表

```
GET /api/customer/menu?store_id={store_id}
```

**响应示例**:
```json
[
  {
    "id": 1,
    "name": "热菜",
    "description": "美味的热菜",
    "sort_order": 1,
    "items": [
      {
        "id": 1,
        "name": "宫保鸡丁",
        "description": "经典川菜",
        "price": 38.00,
        "image_url": "https://...",
        "stock": 50,
        "is_available": true,
        "is_recommended": true
      }
    ]
  }
]
```

#### 3. 创建订单

```
POST /api/customer/order
```

**请求体**:
```json
{
  "store_id": 1,
  "table_id": 1,
  "customer_name": "张三",
  "customer_phone": "13800138000",
  "items": [
    {
      "menu_item_id": 1,
      "quantity": 2,
      "special_instructions": "少放辣"
    }
  ],
  "special_instructions": "尽快上菜"
}
```

**响应示例**:
```json
{
  "id": 1,
  "order_number": "ORD202601071200001234",
  "store_id": 1,
  "table_id": 1,
  "table_number": "1",
  "total_amount": 76.00,
  "final_amount": 76.00,
  "payment_status": "unpaid",
  "order_status": "pending",
  "items": [...]
}
```

#### 4. 查询订单详情

```
GET /api/customer/order/{order_id}
```

### 店员端API (端口8001)

#### 1. 获取订单列表

```
GET /api/staff/orders?store_id={store_id}&status={status}&limit={limit}
```

**参数说明**:
- `store_id`: 店铺ID（必填）
- `status`: 订单状态（可选）：pending, confirmed, preparing, ready, serving, completed, cancelled
- `limit`: 返回数量限制（默认50）

**响应示例**:
```json
[
  {
    "id": 1,
    "order_number": "ORD202601071200001234",
    "table_number": "1",
    "total_amount": 76.00,
    "order_status": "pending",
    "items_count": 2
  }
]
```

#### 2. 获取订单详情

```
GET /api/staff/order/{order_id}
```

**响应示例**:
```json
{
  "id": 1,
  "order_number": "ORD202601071200001234",
  "table_number": "1",
  "customer_name": "张三",
  "customer_phone": "13800138000",
  "order_status": "pending",
  "items": [...],
  "status_logs": [...]
}
```

#### 3. 更新订单状态

```
PUT /api/staff/order/status
```

**请求体**:
```json
{
  "order_id": 1,
  "order_status": "confirmed",
  "notes": "订单确认",
  "operator_id": 1
}
```

**状态流转规则**:
- `pending` → `confirmed` 或 `cancelled`
- `confirmed` → `preparing`
- `preparing` → `ready`
- `ready` → `serving`
- `serving` → `completed`

#### 4. 更新订单项状态

```
PUT /api/staff/order-item/status
```

**请求体**:
```json
{
  "order_item_id": 1,
  "status": "ready"
}
```

#### 5. 获取店铺桌号列表

```
GET /api/staff/store/{store_id}/tables
```

**响应示例**:
```json
[
  {
    "id": 1,
    "table_number": "1",
    "table_name": "1号桌",
    "seats": 4,
    "is_active": true,
    "current_order_id": 1,
    "current_order_status": "preparing"
  }
]
```

## H5点餐页面

### 页面功能

1. **店铺信息展示**: 显示店铺名称、地址、营业时间
2. **分类浏览**: 按菜品分类浏览，支持横向滑动
3. **菜品展示**: 显示菜品图片、名称、描述、价格
4. **购物车功能**: 
   - 添加/减少菜品数量
   - 查看购物车总价
   - 显示购物车商品数量
5. **订单提交**: 提交订单并显示订单信息
6. **订单状态**: 实时查看订单状态

### 页面访问

页面路径: `assets/order.html`

URL参数:
- `store_id`: 店铺ID（必填）
- `table_id`: 桌号ID（必填）
- `table_number`: 桌号（可选）

示例URL:
```
http://your-domain.com/order.html?store_id=1&table_id=1&table_number=1
```

## 二维码生成

### 二维码内容格式

```
{base_url}?store_id={store_id}&table_id={table_id}
```

示例:
```
http://your-domain.com/order.html?store_id=1&table_id=1
```

### 二维码存储

二维码图片存储在S3对象存储中，文件命名规则:
```
table_qrcode_store{store_id}_table{table_id}.png
```

### 签名URL

二维码URL使用S3签名URL，有效期默认1小时。

## 数据库表结构

### 核心表

1. **stores**: 店铺表
2. **tables**: 桌号表（包含二维码URL和内容）
3. **menu_categories**: 菜品分类表
4. **menu_items**: 菜品表
5. **orders**: 订单表
6. **order_items**: 订单明细表
7. **order_status_logs**: 订单状态日志表

### 关联关系

- 店铺 (stores) 1 → N 桌号 (tables)
- 店铺 (stores) 1 → N 菜品分类 (menu_categories)
- 店铺 (stores) 1 → N 订单 (orders)
- 桌号 (tables) 1 → N 订单 (orders)
- 订单 (orders) 1 → N 订单明细 (order_items)
- 订单 (orders) 1 → N 订单状态日志 (order_status_logs)

## 订单状态流转

### 状态定义

| 状态 | 说明 |
|------|------|
| pending | 待确认 |
| confirmed | 已确认 |
| preparing | 准备中 |
| ready | 已完成（制作完成）|
| serving | 上菜中 |
| completed | 已完成（用餐完成）|
| cancelled | 已取消 |

### 状态流转图

```
pending → confirmed → preparing → ready → serving → completed
   ↓
cancelled
```

## 测试

### 运行测试

```bash
# 启动API服务（在后台）
eval $(python /workspace/projects/scripts/load_env.py)
PYTHONPATH=/workspace/projects/src python -m uvicorn api.customer_api:app --host 0.0.0.0 --port 8000 > /tmp/customer_api.log 2>&1 &
PYTHONPATH=/workspace/projects/src python -m uvicorn api.staff_api:app --host 0.0.0.0 --port 8001 > /tmp/staff_api.log 2>&1 &

# 等待服务启动
sleep 5

# 运行测试脚本
PYTHONPATH=/workspace/projects/src python /workspace/projects/scripts/test_order_flow.py
```

### 测试内容

1. 创建测试数据（店铺、桌号、菜品等）
2. 生成二维码并上传到S3
3. 测试顾客端API（获取店铺、菜品、创建订单）
4. 测试店员端API（订单管理、状态流转）
5. 验证订单与桌号关联

## 注意事项

1. **环境变量**: 确保已加载环境变量（使用 `load_env.py`）
2. **PYTHONPATH**: 运行Python脚本时需要设置 `PYTHONPATH=/workspace/projects/src`
3. **数据库连接**: 确保数据库连接正常
4. **S3存储**: 确保S3对象存储服务可用
5. **端口占用**: 确保端口8000和8001未被占用

## 故障排查

### API服务无法启动

检查日志:
```bash
tail -100 /tmp/customer_api.log
tail -100 /tmp/staff_api.log
```

常见问题:
- 模块导入错误: 检查PYTHONPATH设置
- 数据库连接失败: 检查环境变量和数据库服务
- 端口被占用: 更换端口或停止占用端口的进程

### 二维码生成失败

- 检查S3存储配置
- 检查桌号ID是否存在
- 检查网络连接

### H5页面无法访问

- 检查API服务是否正常运行
- 检查URL参数是否正确
- 检查CORS配置

## 后续开发建议

1. **支付集成**: 接入微信支付、支付宝等支付方式
2. **实时通信**: 使用WebSocket实现订单状态实时推送
3. **会员系统**: 集成会员积分、优惠券等功能
4. **数据统计**: 添加营收分析、订单统计等报表功能
5. **厨房显示**: 开发厨房显示屏，实时显示订单
6. **移动端APP**: 开发店员和顾客的移动应用

## 联系支持

如有问题，请联系技术支持。
