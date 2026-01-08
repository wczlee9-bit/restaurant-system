# 系统权限、支付方式扩展与小票打印功能文档

## 概述

本文档描述了扫码点餐系统新增的三个核心功能：
1. 系统权限管理（管理员、总公司、店长、店员四种角色）
2. 支付方式扩展（支持现金、借记卡、信用卡、支付宝、微信、其他）
3. 小票打印功能（支持自定义模板和功能区设置）

---

## 一、系统权限管理

### 1.1 角色定义

系统包含四种基础角色，每种角色拥有不同的权限：

#### 管理员 (Admin)
- **描述**: 系统超级管理员，拥有所有权限
- **权限数**: 39个
- **核心权限**:
  - `all:access` - 全部权限
  - 公司管理：创建、读取、更新、删除
  - 店铺管理：创建、读取、更新、删除
  - 菜单管理：创建、读取、更新、删除
  - 订单管理：创建、读取、更新、删除
  - 支付管理：创建、读取、更新、删除
  - 会员管理：创建、读取、更新、删除
  - 员工管理：创建、读取、更新、删除
  - 库存管理：创建、读取、更新、删除
  - 报表：读取、导出
  - 角色/用户管理
  - 小票：打印、配置

#### 总公司 (Company)
- **描述**: 总公司角色，可以管理旗下所有店铺
- **权限数**: 22个
- **核心权限**:
  - 店铺管理：创建、读取、更新
  - 菜单管理：创建、读取、更新
  - 订单管理：读取、更新
  - 支付管理：读取、更新
  - 会员管理：读取、更新
  - 员工管理：创建、读取、更新、删除
  - 库存管理：读取、更新
  - 报表：读取、导出
  - 小票：打印、配置

#### 店长 (Store Manager)
- **描述**: 店铺管理员，管理本店的所有业务
- **权限数**: 18个
- **核心权限**:
  - 店铺管理：读取、更新
  - 菜单管理：读取、更新
  - 订单管理：创建、读取、更新
  - 支付管理：读取、更新
  - 会员管理：读取、更新
  - 员工管理：读取、更新
  - 库存管理：读取、更新
  - 报表：读取
  - 小票：打印、配置

#### 店员 (Staff)
- **描述**: 普通店员，处理订单和基本业务
- **权限数**: 7个
- **核心权限**:
  - 订单管理：创建、读取、更新
  - 支付管理：读取
  - 会员管理：读取
  - 库存管理：读取
  - 小票：打印

### 1.2 API 接口

#### 初始化系统角色
```
POST /api/permission/init-roles
```
- 功能：初始化4个基础角色，如果角色已存在则更新权限
- 返回：初始化/更新的角色数量

#### 获取所有角色
```
GET /api/permission/roles
```
- 功能：获取系统中所有角色及其权限
- 返回：角色列表（ID、名称、描述、权限列表）

#### 创建角色
```
POST /api/permission/role
```
- 功能：创建自定义角色
- 参数：
  - `name`: 角色名称
  - `description`: 角色描述
  - `permissions`: 权限列表

#### 分配用户角色
```
POST /api/permission/user-role
```
- 功能：为用户分配角色
- 参数：
  - `user_id`: 用户ID
  - `role_id`: 角色ID
  - `store_id`: 店铺ID（店员角色必填）
- 注意：店员角色会自动在Staff表中创建关联记录

#### 获取用户的所有角色
```
GET /api/permission/user/{user_id}/roles
```
- 功能：获取指定用户的所有角色信息
- 返回：用户角色列表（包含店铺ID）

#### 移除用户角色
```
DELETE /api/permission/user-role/{user_role_id}
```
- 功能：移除用户的指定角色关联

#### 检查用户权限
```
POST /api/permission/check
```
- 功能：检查用户是否有指定权限
- 参数：
  - `user_id`: 用户ID
  - `permission`: 要检查的权限
  - `store_id`: 店铺ID（可选，用于店铺级权限验证）
- 返回：是否有权限

#### 获取用户有权限的店铺列表
```
GET /api/permission/user/{user_id}/stores
```
- 功能：获取用户有权限的店铺列表
- 规则：
  - 管理员：所有店铺
  - 总公司：所有店铺
  - 店长/店员：仅自己所属店铺

### 1.3 权限验证逻辑

系统通过以下规则验证用户权限：

1. **角色继承**: 用户可以有多个角色，任一角色有权限即通过
2. **权限层级**:
   - `all:access`: 拥有所有权限
   - 功能权限：如 `order:read`, `payment:update`
3. **店铺级权限**: 对于需要店铺ID的操作，验证用户是否对该店铺有权限
4. **自动关联**: 店员角色分配时会自动在Staff表中创建记录

---

## 二、支付方式扩展

### 2.1 支持的支付方式

系统支持以下6种支付方式：

1. **微信支付 (wechat)**
   - 描述：使用微信扫码支付
   - 特性：生成支付二维码

2. **支付宝**
   - 描述：使用支付宝扫码支付
   - 特性：生成支付二维码

3. **现金支付**
   - 描述：现金支付，由店员确认
   - 特性：无需支付链接

4. **信用卡 (credit_card)**
   - 描述：刷卡支付
   - 特性：跳转到收银台

5. **借记卡**
   - 描述：借记卡支付
   - 特性：跳转到收银台

6. **其他支付 (other)**
   - 描述：其他支付方式
   - 特性：可自定义支付方式名称

### 2.2 API 接口

#### 创建支付订单
```
POST /api/payment/create
```
- 参数：
  - `order_id`: 订单ID
  - `payment_method`: 支付方式
    - `wechat`, `alipay`, `cash`, `credit_card`, `debit_card`, `other`
  - `customer_phone`: 顾客手机号（可选，用于会员识别）
  - `other_method_name`: 其他支付方式名称（当payment_method为other时必填）

- 返回：
  - 支付ID
  - 订单信息
  - 支付URL/二维码（用于扫码支付）

#### 获取支持的支付方式列表
```
GET /api/payment/methods
```
- 返回：所有支持的支付方式列表（ID、名称、描述、图标）

### 2.3 支付流程

1. 创建支付订单
2. 根据支付方式生成支付信息：
   - 微信/支付宝：生成支付二维码
   - 信用卡/借记卡：跳转到收银台
   - 现金/其他：无需支付链接，店员确认
3. 支付回调处理
4. 更新订单支付状态
5. 增加会员积分（如适用）

---

## 三、小票打印功能

### 3.1 小票功能区配置

小票由多个功能区组成，每个功能区可以独立配置：

#### 默认功能区配置

1. **店铺信息 (header)**
   - 排序：1
   - 内容：店铺名称、地址、电话
   - 模板：
     ```
     {{ store.name }}
     地址: {{ store.address or '暂无' }}
     电话: {{ store.phone or '暂无' }}
     ================================
     ```

2. **订单信息 (order_info)**
   - 排序：2
   - 内容：订单号、桌号、下单时间
   - 模板：
     ```
     订单号: {{ order.order_number }}
     桌号: {{ table.table_number }}
     下单时间: {{ order.created_at.strftime('%Y-%m-%d %H:%M:%S') }}
     --------------------------------
     ```

3. **顾客信息 (customer)**
   - 排序：3
   - 内容：顾客姓名、电话、会员信息
   - 模板：
     ```
     顾客: {{ order.customer_name or '散客' }}
     电话: {{ order.customer_phone or '-' }}
     会员: {{ member_info }}
     --------------------------------
     ```

4. **商品明细**
   - 排序：4
   - 内容：商品名称、数量、金额
   - 模板：
     ```
     商品名称            数量  金额
     {% for item in items %}
     {{ item.menu_item_name.ljust(14) }} {{ item.quantity }}  {{ item.subtotal }}
     {% endfor %}
     --------------------------------
     ```

5. **支付信息 (payment)**
   - 排序：5
   - 内容：商品总额、折扣金额、实付金额、支付方式、支付时间
   - 模板：
     ```
     商品总额:  {{ order.total_amount }}
     折扣金额:  {{ order.discount_amount }}
     实付金额:  {{ order.final_amount }}
     支付方式:  {{ order.payment_method }}
     支付时间:  {{ order.payment_time.strftime('%Y-%m-%d %H:%M:%S') if order.payment_time else '待支付' }}
     ================================
     ```

6. **底部信息 (footer)**
   - 排序：6
   - 内容：感谢语、客服电话
   - 模板：
     ```
     感谢您的光临!
     欢迎再次惠顾!
     客服热线: {{ store.phone or '400-xxx-xxxx' }}
     ```

### 3.2 功能区配置参数

每个功能区支持以下配置：

- `section_type`: 功能区类型
- `section_name`: 功能区名称
- `is_enabled`: 是否启用
- `sort_order`: 排序
- `template`: 自定义模板（Jinja2格式）
- `config`: 附加配置（JSON格式）

### 3.3 API 接口

#### 打印小票
```
POST /api/receipt/print
```
- 参数：
  - `order_id`: 订单ID
  - `printer_name`: 打印机名称（可选）
  - `copy_count`: 打印份数（默认1）
  - `config_id`: 小票配置ID（可选，不传则使用默认配置）

- 返回：
  - 打印状态
  - 小票内容
  - 打印信息

#### 预览小票
```
GET /api/receipt/preview/{order_id}
```
- 功能：预览小票内容，不实际打印
- 返回：小票内容（纯文本格式）

#### 获取默认小票配置
```
GET /api/receipt/default-config
```
- 返回：默认的功能区配置列表

#### 创建小票配置
```
POST /api/receipt/config
```
- 参数：
  - `store_id`: 店铺ID
  - `config_name`: 配置名称
  - `sections`: 功能区配置列表

#### 获取小票配置
```
GET /api/receipt/config/{config_id}
```
- 返回：指定的小票配置详情

#### 获取店铺的小票配置列表
```
GET /api/receipt/store/{store_id}/config
```
- 返回：店铺的所有小票配置

#### 更新小票配置
```
PUT /api/receipt/config/{config_id}
```
- 参数：同创建配置
- 功能：更新指定的小票配置

### 3.4 小票生成逻辑

1. 获取订单、店铺、桌号、订单项信息
2. 获取会员信息（如顾客是会员）
3. 加载小票配置（默认配置或自定义配置）
4. 按排序顺序生成各个功能区
5. 使用Jinja2模板引擎渲染每个功能区
6. 拼接生成完整小票内容
7. 返回小票内容供打印

### 3.5 模板变量

小票模板支持以下变量：

- `order`: 订单对象
  - `order_number`: 订单号
  - `total_amount`: 商品总额
  - `discount_amount`: 折扣金额
  - `final_amount`: 实付金额
  - `payment_method`: 支付方式
  - `payment_time`: 支付时间
  - `customer_name`: 顾客姓名
  - `customer_phone`: 顾客电话
  - `created_at`: 下单时间

- `store`: 店铺对象
  - `name`: 店铺名称
  - `address`: 店铺地址
  - `phone`: 店铺电话

- `table`: 桌号对象
  - `table_number`: 桌号

- `items`: 订单项列表
  - `menu_item_name`: 菜品名称
  - `quantity`: 数量
  - `subtotal`: 小计

- `member_info`: 会员信息字符串

---

## 四、测试

### 4.1 单元测试

运行单元测试：
```bash
cd /workspace/projects
PYTHONPATH=/workspace/projects/src python scripts/test_permissions_unit.py
```

测试内容：
- ✓ 角色权限定义
- ✓ 支付方式定义
- ✓ 小票功能区配置
- ✓ 角色初始化
- ✓ 权限检查逻辑

### 4.2 集成测试

运行集成测试（需要启动所有API服务）：
```bash
cd /workspace/projects
python scripts/test_new_permissions_features.py
```

测试内容：
- 权限管理API
- 扩展支付方式
- 小票打印功能
- 小票配置管理

---

## 五、文件结构

```
src/api/
├── permission_api.py      # 权限管理API
├── payment_api.py         # 支付API（已扩展）
└── receipt_api.py         # 小票打印API（新增）

scripts/
├── test_permissions_unit.py        # 单元测试
└── test_new_permissions_features.py # 集成测试

docs/
└── permissions_receipt_features.md # 本文档
```

---

## 六、使用示例

### 6.1 初始化系统角色

```python
import requests

response = requests.post("http://localhost:8007/api/permission/init-roles")
print(response.json())
# 输出: {"message": "成功初始化/更新 3 个角色", "roles": ["admin", "company", "store_manager", "staff"]}
```

### 6.2 创建借记卡支付

```python
import requests

response = requests.post(
    "http://localhost:8002/api/payment/create",
    json={
        "order_id": 1,
        "payment_method": "debit_card",
        "customer_phone": "13800138000"
    }
)
print(response.json())
```

### 6.3 打印小票

```python
import requests

response = requests.post(
    "http://localhost:8008/api/receipt/print",
    json={
        "order_id": 1,
        "printer_name": "热敏打印机",
        "copy_count": 2
    }
)
print(response.json()['receipt_content'])
```

### 6.4 检查用户权限

```python
import requests

response = requests.post(
    "http://localhost:8007/api/permission/check",
    json={
        "user_id": 1,
        "permission": "order:read",
        "store_id": 1
    }
)
print(response.json())
# 输出: {"has_permission": true, "user_id": 1, "permission": "order:read"}
```

---

## 七、总结

本次更新实现了以下功能：

1. ✅ **系统权限管理**
   - 4种基础角色：管理员、总公司、店长、店员
   - 细粒度权限控制
   - 用户-角色关联管理
   - 权限检查API

2. ✅ **支付方式扩展**
   - 支持6种支付方式：微信、支付宝、现金、信用卡、借记卡、其他
   - 自定义支付方式名称
   - 完整的支付流程

3. ✅ **小票打印功能**
   - 6个默认功能区
   - Jinja2模板引擎支持
   - 自定义小票配置
   - 小票预览和打印

所有功能已经过单元测试验证，可以正常使用。
