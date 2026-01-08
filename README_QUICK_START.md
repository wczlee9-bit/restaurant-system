# 🍽️ 多店铺扫码点餐系统 - 快速启动指南

## 📋 前提条件

- Python 3.8+
- 已安装项目依赖（requirements.txt）
- PostgreSQL 数据库已配置
- 测试数据已初始化

## 🚀 快速启动

### 步骤1: 初始化测试数据（首次运行）

```bash
cd /workspace/projects
python scripts/init_test_data.py
```

### 步骤2: 启动API服务

```bash
# 方式1: 使用启动脚本（推荐）
python scripts/start_restaurant_api.py

# 方式2: 直接运行
python -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后，你会看到类似以下输出：
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 步骤3: 打开测试系统

在浏览器中打开以下文件：
```
assets/restaurant_test_system.html
```

或者使用本地服务器：
```bash
cd /workspace/projects/assets
python -m http.server 8080
```

然后访问: http://localhost:8080/restaurant_test_system.html

## 📱 功能模块说明

### 1. 顾客端（扫码点餐）

**功能：**
- 选择桌号
- 浏览菜品（按分类筛选）
- 加入购物车
- 提交订单并支付
- 会员积分累计

**使用流程：**
1. 点击空闲桌号
2. 浏览菜品，点击"加入购物车"
3. 点击"去结算"查看购物车
4. 选择支付方式
5. 点击"确认支付并下单"

### 2. 订单管理

**功能：**
- 查看所有订单
- 按状态和桌号筛选
- 更新订单状态
- 打印订单小票

**订单状态流转：**
```
pending (待确认) → confirmed (已确认) → preparing (制作中) 
    → ready (待传菜) → serving (上菜中) → completed (已完成)
                            ↓
                      cancelled (已取消)
```

### 3. 厨房制作

**功能：**
- 查看待制作订单
- 更新单个菜品状态
- 打印制作单

**菜品状态流转：**
```
pending (待制作) → preparing (制作中) → ready (待传菜)
```

### 4. 传菜管理

**功能：**
- 查看待传菜订单
- 打印传菜单
- **逐一确认上菜**（在顾客面前确认）

**重要提示：**
- 上菜员在顾客面前，每上一道菜，点击"确认上菜"按钮
- 已上菜的菜品会显示删除线
- 全部上完后点击"全部上菜完成"

### 5. 菜品管理

**功能：**
- 添加/编辑/删除菜品
- 设置推荐菜品
- 上下架管理
- 库存管理

### 6. 桌号管理

**功能：**
- 添加/编辑/删除桌号
- 生成桌号二维码
- 查看桌号状态

## 🔗 API接口说明

### 基础信息

- **Base URL:** `http://localhost:8000`
- **API文档:** `http://localhost:8000/docs`
- **健康检查:** `GET /health`

### 主要接口

#### 店铺信息
```
GET /api/store
```

#### 菜品分类
```
GET /api/menu-categories/
```

#### 菜品管理
```
GET    /api/menu-items/
POST   /api/menu-items/
PATCH  /api/menu-items/{item_id}
DELETE /api/menu-items/{item_id}
```

#### 桌号管理
```
GET    /api/tables/
POST   /api/tables/
PATCH  /api/tables/{table_id}
DELETE /api/tables/{table_id}
POST   /api/tables/generate-qr
```

#### 订单管理
```
GET    /api/orders/
POST   /api/orders/
GET    /api/orders/{order_id}
PATCH  /api/orders/{order_id}/status
PATCH  /api/orders/{order_id}/items/{item_id}/status
```

## 🧪 全流程测试

### 测试用例1: 完整下单流程

1. **顾客端**
   - 选择桌号1
   - 添加"宫保鸡丁"和"白米饭"到购物车
   - 选择微信支付，输入手机号13800138000
   - 点击"确认支付并下单"

2. **订单管理**
   - 查看订单，状态应为"待确认"
   - 点击"确认订单"

3. **厨房制作**
   - 查看订单，点击"开始制作"
   - 制作完成后点击"制作完成"

4. **传菜管理**
   - 点击"打印传菜单"
   - 在顾客面前，逐一点击"确认上菜"
   - 点击"全部上菜完成"

5. **订单管理**
   - 验证订单状态为"已完成"
   - 点击"打印"查看小票

### 测试用例2: 多支付方式测试

分别测试以下支付方式：
- 微信支付
- 支付宝
- 信用卡
- 借记卡
- 现金

### 测试用例3: 菜品管理测试

1. 添加新菜品"鱼香肉丝"
2. 设置为推荐菜品
3. 设置库存为50
4. 下单购买
5. 验证库存减少

### 测试用例4: 多桌号并发测试

同时在多个桌号下单，验证状态更新互不影响。

## 🖨️ 小票打印

### 订单小票
包含：店铺信息、订单号、桌号、时间、支付方式、订单明细、总金额

### 传菜单
包含：桌号、订单号、待传菜品列表

### 打印方法
1. 点击"打印"或"打印传菜单"按钮
2. 在预览窗口中查看内容
3. 点击"打印"，选择小票打印机

## 📊 修改建议

基于测试过程中发现的问题，以下是一些建议：

### 1. 实时通信
- 添加WebSocket实现订单状态实时推送
- 新订单到来时语音提示

### 2. 会员功能增强
- 显示会员积分和等级
- 显示折扣优惠金额
- 提供积分查询页面

### 3. 订单备注
- 允许顾客添加订单备注
- 备注在小票和制作单中显示

### 4. 库存预警
- 库存低于阈值时提示
- 自动下架库存为0的菜品

### 5. 报表统计
- 添加营收统计页面
- 菜品销量排行
- 高峰时段分析

## 🐛 常见问题

### 问题1: API连接失败

**原因：** 后端服务未启动或端口被占用

**解决：**
```bash
# 检查服务是否运行
curl http://localhost:8000/health

# 查看端口占用
lsof -i :8000

# 修改API地址
# 在测试系统页面"系统设置"中修改API地址
```

### 问题2: 数据未显示

**原因：** 测试数据未初始化

**解决：**
```bash
python scripts/init_test_data.py
```

### 问题3: 打印功能异常

**原因：** 浏览器打印设置问题

**解决：**
- 确保已安装小票打印机驱动
- 在打印预览中选择正确的打印机
- 调整页面边距和缩放比例

## 📞 技术支持

如有问题，请检查：
1. 后端服务是否正常运行
2. API地址配置是否正确
3. 数据库连接是否正常
4. 浏览器控制台是否有错误信息

## 📝 项目结构

```
/workspace/projects/
├── src/
│   ├── api/
│   │   └── restaurant_api.py      # 餐饮系统API
│   └── storage/
│       └── database/
│           └── shared/
│               └── model.py       # 数据模型
├── scripts/
│   ├── init_test_data.py          # 初始化测试数据
│   └── start_restaurant_api.py    # 启动脚本
├── assets/
│   ├── restaurant_test_system.html # 测试系统页面
│   └── README_TEST_SYSTEM.md       # 测试系统说明
└── README_QUICK_START.md            # 本文件
```

---

**祝使用愉快！** 🎉
