# 扫码点餐系统 - 使用指南

## 系统概述

本系统实现了完整的扫码点餐功能，顾客可以通过扫描桌号二维码，在手机上浏览菜单、选择菜品、提交订单。

## 核心功能

### 1. 二维码生成
为每个桌号生成独立的二维码，扫码后跳转到点餐页面。

### 2. H5 点餐页面
响应式设计，支持：
- 浏览店铺信息
- 查看分类菜品
- 添加购物车
- 提交订单
- 查看订单状态

### 3. API 接口
提供完整的 RESTful API 支持点餐流程。

## 文件结构

```
src/
├── tools/
│   └── qrcode_tool.py          # 二维码生成工具
├── api/
│   └── customer_api.py         # 顾客端 API 接口
└── storage/
    └── database/shared/
        └── model.py            # 数据库模型

assets/
└── order.html                 # H5 点餐页面

scripts/
└── test_order_flow.py         # 测试脚本
```

## 快速开始

### 1. 生成二维码

为店铺的所有桌号生成二维码：

```python
from tools.qrcode_tool import generate_store_qrcodes

# 生成店铺ID为2的所有桌号二维码
result = generate_store_qrcodes(store_id=2)
print(result)
```

输出示例：
```json
{
  "success": true,
  "store_id": 2,
  "total": 10,
  "success_count": 10,
  "fail_count": 0,
  "results": [
    {
      "table_id": 11,
      "table_number": "T01",
      "qrcode_url": "https://..."
    }
  ]
}
```

### 2. 启动 API 服务

```bash
# 方式1：直接启动
PYTHONPATH=/workspace/projects/src python -m uvicorn src.api.customer_api:app --host 0.0.0.0 --port 8000

# 方式2：后台启动
PYTHONPATH=/workspace/projects/src python -m uvicorn src.api.customer_api:app --host 0.0.0.0 --port 8000 &
```

服务启动后，访问 http://localhost:8000 查看 API 文档。

### 3. 使用点餐页面

将 `assets/order.html` 部署到 Web 服务器，或直接在浏览器中打开。

URL 参数：
- `store_id`: 店铺ID（必需）
- `table_id`: 桌号ID（必需）
- `table_number`: 桌号显示名称（可选）

示例：
```
http://your-domain.com/order.html?store_id=2&table_id=11&table_number=T01
```

## API 接口文档

### 1. 获取店铺信息

**接口：** `GET /api/customer/shop?store_id=2`

**响应：**
```json
{
  "id": 2,
  "name": "示范餐厅",
  "address": "北京市朝阳区示范路1号",
  "phone": "010-12345678",
  "opening_hours": {"open": "09:00", "close": "22:00"}
}
```

### 2. 获取菜品列表

**接口：** `GET /api/customer/menu?store_id=2`

**响应：**
```json
[
  {
    "id": 1,
    "name": "热菜",
    "description": "热菜系列",
    "sort_order": 1,
    "items": [
      {
        "id": 1,
        "name": "宫保鸡丁",
        "description": "经典川菜，香辣可口",
        "price": 38.0,
        "stock": 100,
        "is_available": true
      }
    ]
  }
]
```

### 3. 创建订单

**接口：** `POST /api/customer/order`

**请求体：**
```json
{
  "store_id": 2,
  "table_id": 11,
  "customer_name": "张三",
  "customer_phone": "13800000000",
  "items": [
    {
      "menu_item_id": 1,
      "quantity": 2
    }
  ],
  "special_instructions": "少辣"
}
```

**响应：**
```json
{
  "id": 100,
  "order_number": "ORD202601072133457959",
  "store_id": 2,
  "table_id": 11,
  "table_number": "T01",
  "total_amount": 76.0,
  "final_amount": 76.0,
  "payment_status": "unpaid",
  "order_status": "pending",
  "created_at": "2024-01-07T21:33:45",
  "items": [...]
}
```

### 4. 查询订单详情

**接口：** `GET /api/customer/order/{order_id}`

**响应：** 同创建订单响应

## 订单状态流转

```
pending (待确认)
  ↓
confirmed (已确认)
  ↓
preparing (准备中)
  ↓
ready (已完成)
  ↓
serving (上菜中)
  ↓
completed (已完成)
```

## 测试

运行完整流程测试：

```bash
PYTHONPATH=/workspace/projects/src python scripts/test_order_flow.py
```

测试步骤：
1. ✅ 获取店铺信息
2. ✅ 获取菜品列表
3. ✅ 创建订单
4. ✅ 查询订单详情

## 实际使用流程

### 顾客端流程

1. **扫码**
   - 顾客扫描桌号上的二维码
   - 跳转到点餐页面

2. **浏览菜单**
   - 查看店铺信息
   - 按分类浏览菜品
   - 查看菜品详情

3. **选择菜品**
   - 点击"+"添加到购物车
   - 调整数量
   - 查看购物车

4. **提交订单**
   - 确认订单信息
   - 提交订单
   - 查看订单状态

5. **等待上菜**
   - 订单状态更新为"准备中"
   - 厨师开始制作
   - 传菜员送菜

### 店员端流程（待开发）

1. 接收订单通知
2. 确认订单
3. 打印小票
4. 传给厨房

### 厨师端流程（待开发）

1. 查看订单列表
2. 开始制作
3. 标记完成
4. 通知传菜员

## 数据库关联

订单创建后：
- `orders` 表：保存订单主信息
- `order_items` 表：保存订单项详情
- `tables` 表：通过 `table_id` 关联桌号

## 注意事项

1. **二维码有效期**
   - 默认1年
   - 可在生成时调整

2. **库存检查**
   - 提交订单时会检查库存
   - 库存不足会提示错误

3. **订单号生成**
   - 格式：`ORD{YYYYMMDDHHmmss}{4位随机数}`
   - 保证唯一性

4. **跨域配置**
   - 生产环境需配置具体的域名
   - 当前允许所有域名（仅用于测试）

## 后续开发计划

### 高优先级
- [ ] 店员管理端
- [ ] 厨房显示端
- [ ] 支付功能集成
- [ ] 订单状态实时更新（WebSocket）

### 中优先级
- [ ] 订单评价功能
- [ ] 菜品图片上传
- [ ] 会员积分系统
- [ ] 优惠券系统

### 低优先级
- [ ] 外卖功能
- [ ] 预约点餐
- [ ] 多语言支持
- [ ] 数据统计报表

## 故障排查

### 问题1：二维码无法生成
**检查：**
- S3 存储是否正常
- 环境变量是否正确配置
- 桌号是否存在

### 问题2：API 接口返回 404
**检查：**
- 服务是否启动
- 端口是否正确
- 请求路径是否正确

### 问题3：订单创建失败
**检查：**
- 菜品库存是否充足
- 桌号是否属于该店铺
- 必填参数是否完整

## 联系支持

如有问题，请查看：
- API 文档：http://localhost:8000/docs
- 数据库设计：`docs/database_design.md`
- 系统架构：`docs/system_architecture.md`
