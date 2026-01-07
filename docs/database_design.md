# 扫码点餐系统 - 数据库设计文档

## 系统架构概述

本系统采用多店铺架构，支持开发者、总公司、店长、店员四种角色，实现扫码点餐、支付、会员管理、库存管理等核心功能。

## 数据库设计

### 1. 用户与权限模块

#### users（用户表）
```sql
- id: 主键
- username: 用户名（唯一）
- password: 密码（加密）
- email: 邮箱（唯一）
- phone: 手机号
- name: 真实姓名
- is_active: 是否激活
- created_at: 创建时间
- updated_at: 更新时间
```

#### roles（角色表）
```sql
- id: 主键
- name: 角色名称（developer, company, store_manager, staff）
- description: 角色描述
- permissions: 权限列表（JSON）
- created_at: 创建时间
```

#### user_roles（用户角色关联表）
```sql
- id: 主键
- user_id: 用户ID（外键）
- role_id: 角色ID（外键）
- created_at: 创建时间
```

### 2. 店铺管理模块

#### companies（总公司表）
```sql
- id: 主键
- name: 公司名称
- contact_person: 联系人
- contact_phone: 联系电话
- address: 地址
- is_active: 是否激活
- created_at: 创建时间
- updated_at: 更新时间
```

#### stores（店铺表）
```sql
- id: 主键
- company_id: 所属公司ID（外键）
- name: 店铺名称
- address: 店铺地址
- phone: 联系电话
- manager_id: 店长ID（外键到users）
- is_active: 是否激活
- opening_hours: 营业时间（JSON）
- created_at: 创建时间
- updated_at: 更新时间
```

#### tables（桌号表）
```sql
- id: 主键
- store_id: 店铺ID（外键）
- table_number: 桌号
- table_name: 桌子名称
- qrcode_url: 二维码URL（存储在S3）
- qrcode_content: 二维码内容
- seats: 座位数
- is_active: 是否可用
- created_at: 创建时间
- updated_at: 更新时间
```

#### staff（店员表）
```sql
- id: 主键
- user_id: 用户ID（外键）
- store_id: 店铺ID（外键）
- position: 职位（厨师、服务员、传菜员等）
- is_active: 是否在职
- created_at: 创建时间
- updated_at: 更新时间
```

### 3. 菜品管理模块

#### menu_categories（菜品分类表）
```sql
- id: 主键
- store_id: 店铺ID（外键）
- name: 分类名称
- description: 分类描述
- sort_order: 排序
- is_active: 是否显示
- created_at: 创建时间
- updated_at: 更新时间
```

#### menu_items（菜品表）
```sql
- id: 主键
- store_id: 店铺ID（外键）
- category_id: 分类ID（外键）
- name: 菜品名称
- description: 菜品描述
- price: 价格
- original_price: 原价
- image_url: 菜品图片URL（存储在S3）
- stock: 库存数量
- unit: 单位（份、个、斤等）
- cooking_time: 烹饪时间（分钟）
- is_available: 是否可售
- is_recommended: 是否推荐
- sort_order: 排序
- created_at: 创建时间
- updated_at: 更新时间
```

### 4. 订单模块

#### orders（订单表）
```sql
- id: 主键
- store_id: 店铺ID（外键）
- table_id: 桌号ID（外键）
- order_number: 订单号（唯一）
- customer_name: 顾客姓名（可选）
- customer_phone: 顾客手机号（可选）
- total_amount: 订单总金额
- discount_amount: 折扣金额
- final_amount: 实付金额
- payment_status: 支付状态（unpaid, paid, refunded, partial_refunded）
- payment_method: 支付方式（wechat, alipay, cash, card, other）
- payment_time: 支付时间
- order_status: 订单状态（pending, confirmed, preparing, ready, serving, completed, cancelled）
- special_instructions: 特殊要求
- created_at: 创建时间
- updated_at: 更新时间
```

#### order_items（订单明细表）
```sql
- id: 主键
- order_id: 订单ID（外键）
- menu_item_id: 菜品ID（外键）
- menu_item_name: 菜品名称（快照）
- menu_item_price: 菜品价格（快照）
- quantity: 数量
- subtotal: 小计
- special_instructions: 特殊要求
- status: 状态（pending, preparing, ready, served）
- created_at: 创建时间
```

#### order_status_logs（订单状态变更日志）
```sql
- id: 主键
- order_id: 订单ID（外键）
- from_status: 原状态
- to_status: 新状态
- operator_id: 操作人ID（外键到users）
- operator_name: 操作人姓名
- notes: 备注
- created_at: 创建时间
```

### 5. 支付模块

#### payments（支付表）
```sql
- id: 主键
- order_id: 订单ID（外键）
- payment_method: 支付方式（wechat, alipay, cash, card, other）
- amount: 支付金额
- transaction_id: 交易号
- payment_time: 支付时间
- status: 支付状态（success, failed, pending, refunded）
- refund_amount: 退款金额
- refund_time: 退款时间
- refund_reason: 退款原因
- created_at: 创建时间
```

### 6. 会员管理模块

#### members（会员表）
```sql
- id: 主键
- phone: 手机号（唯一）
- name: 会员姓名
- avatar_url: 头像URL（存储在S3）
- level: 会员等级
- points: 积分
- total_spent: 累计消费金额
- total_orders: 累计订单数
- created_at: 注册时间
- updated_at: 更新时间
```

#### member_level_rules（会员等级规则表）
```sql
- id: 主键
- level: 等级
- level_name: 等级名称
- min_points: 最小积分要求
- discount: 折扣比例
- created_at: 创建时间
```

#### point_logs（积分变动日志）
```sql
- id: 主键
- member_id: 会员ID（外键）
- order_id: 订单ID（外键，可选）
- points: 积分变动（正数为增加，负数为减少）
- reason: 变动原因
- created_at: 创建时间
```

### 7. 库存管理模块

#### inventory（库存表）
```sql
- id: 主键
- store_id: 店铺ID（外键）
- item_name: 物料名称
- category: 物料分类
- unit: 单位
- quantity: 当前库存数量
- min_stock: 最低库存预警
- max_stock: 最大库存
- cost_price: 成本单价
- supplier_id: 供应商ID（外键，可选）
- created_at: 创建时间
- updated_at: 更新时间
```

#### inventory_logs（库存变动日志）
```sql
- id: 主键
- inventory_id: 库存ID（外键）
- operation_type: 操作类型（in, out, adjust）
- quantity: 变动数量
- before_quantity: 变动前数量
- after_quantity: 变动后数量
- reason: 变动原因
- operator_id: 操作人ID（外键）
- created_at: 创建时间
```

#### suppliers（供应商表）
```sql
- id: 主键
- name: 供应商名称
- contact_person: 联系人
- contact_phone: 联系电话
- address: 地址
- created_at: 创建时间
```

#### purchase_orders（采购订单表）
```sql
- id: 主键
- store_id: 店铺ID（外键）
- supplier_id: 供应商ID（外键）
- order_number: 采购单号
- total_amount: 总金额
- status: 状态（pending, confirmed, received, cancelled）
- delivery_date: 交货日期
- created_by: 创建人ID（外键）
- created_at: 创建时间
- updated_at: 更新时间
```

#### purchase_items（采购明细表）
```sql
- id: 主键
- purchase_order_id: 采购订单ID（外键）
- inventory_id: 库存ID（外键）
- item_name: 物料名称
- quantity: 数量
- unit_price: 单价
- subtotal: 小计
- received_quantity: 已收货数量
- created_at: 创建时间
```

### 8. 营收统计模块

#### daily_revenue（每日营收统计表）
```sql
- id: 主键
- store_id: 店铺ID（外键）
- date: 日期
- total_orders: 总订单数
- total_amount: 总金额
- total_discount: 总折扣金额
- total_refund: 总退款金额
- net_revenue: 净营收
- payment_methods: 支付方式统计（JSON）
- peak_hours: 高峰时段（JSON）
- created_at: 创建时间
- updated_at: 更新时间
```

## 索引设计

为提高查询性能，为以下字段添加索引：
- users.username, users.email, users.phone
- orders.order_number, orders.store_id, orders.table_id, orders.created_at
- order_items.order_id, order_items.menu_item_id
- members.phone, members.level
- inventory.store_id, inventory.item_name
- daily_revenue.store_id, daily_revenue.date

## 外键约束

所有外键都设置了 CASCADE 或 RESTRICT 约束，确保数据一致性。
