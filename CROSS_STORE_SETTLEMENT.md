# 跨店铺结算与第三方积分互通系统

## 功能概述

本系统实现了完整的跨店铺积分结算和第三方积分互通功能，支持：
- **跨店铺结算**：会员在一个店铺消费时使用另一个店铺的积分
- **第三方积分互通**：与第三方公司（如星巴克、肯德基等）进行积分兑换
- **1:1 积分核销**：按照消费金额 1:1 生成积分
- **结算统计**：自动追踪积分流转，支持对账和报表

---

## 核心功能

### 1. 跨店铺结算系统

**功能说明**：
- 支持会员在不同店铺之间使用积分
- 自动记录积分来源和去向
- 支持 1:1 或自定义汇率结算
- 追踪结算状态（待结算、已完成、已取消）

**数据表**：`store_point_settlements`

**字段说明**：
- `source_store_id`：积分来源店铺 ID
- `target_store_id`：积分目标店铺 ID（消费店铺）
- `member_id`：会员 ID
- `points`：积分数量
- `settlement_rate`：结算汇率（默认 1.0，即 1:1）
- `settlement_amount`：结算金额
- `status`：结算状态（pending, completed, cancelled）
- `settlement_date`：结算日期

**使用场景**：
```
场景：会员张三在店铺 A（火锅店）消费，想使用店铺 B（奶茶店）的积分

操作：
1. 会员张三有店铺 B 的积分 1000 分
2. 在店铺 A 消费 200 元
3. 使用店铺 B 的 200 积分支付
4. 系统创建跨店铺结算记录
5. 店铺 B 需要向店铺 A 结算 200 元（或积分）
```

---

### 2. 第三方积分互通系统

**功能说明**：
- 管理与第三方公司的积分合作协议
- 支持双向、单向积分互通
- 定义积分兑换比例和限额
- 自动记录兑换日志

**数据表**：
- `third_party_point_agreements`：第三方积分协议表
- `point_exchange_logs`：积分兑换日志表

**协议类型**：
- `bidirectional`：双向互通（积分可以互相兑换）
- `inbound`：只进（第三方积分 → 本方积分）
- `outbound`：只出（本方积分 → 第三方积分）

**字段说明**：
- `third_party_name`：第三方公司名称（如"星巴克咖啡"）
- `agreement_type`：协议类型
- `exchange_rate`：积分兑换比例（1 第三方积分 = X 本方积分）
- `max_points_per_day`：每日最大兑换积分数（可选）
- `max_points_per_order`：单笔订单最大兑换积分数（可选）
- `settlement_cycle`：结算周期（daily, weekly, monthly）
- `settlement_balance`：结算余额
- `status`：状态（active, suspended, terminated）

**使用场景**：
```
场景：与星巴克咖啡建立积分合作协议

配置：
- 第三方公司名称：星巴克咖啡
- 协议类型：双向互通
- 兑换比例：0.8（1 星巴克积分 = 0.8 本方积分）
- 每日限额：1000 积分
- 单笔订单限额：200 积分

兑换示例：
1. 会员使用 100 星巴克积分兑换本方积分 → 获得 80 本方积分
2. 会员使用 100 本方积分兑换星巴克积分 → 获得 125 星巴克积分
```

---

### 3. 积分兑换流程

#### 3.1 会员积分生成（1:1 核销）

**规则**：
- 会员消费金额（元）= 生成积分数
- 消费 1 元 = 1 积分
- 支付成功后自动增加积分

**示例**：
```
订单金额：100 元
支付成功后：会员积分 + 100
```

#### 3.2 会员积分使用

**规则**：
- 积分可以用于抵扣消费金额
- 1 积分 = 1 元
- 支持跨店铺使用积分
- 支持使用第三方积分

**示例**：
```
订单金额：100 元
使用本方积分：50 积分 → 抵扣 50 元
使用店铺 B 积分：30 积分 → 抵扣 30 元
使用星巴克积分：20 积分（兑换比例 0.8）→ 抵扣 16 元
实付金额：4 元
```

---

## API 接口文档

### 基础信息

- **API Base URL**：`/api/settlement`
- **端口**：8003（独立服务）

### 接口列表

#### 1. 跨店铺结算接口

##### 1.1 创建跨店铺结算
```
POST /api/settlement/store
```

**请求体**：
```json
{
  "source_store_id": 2,
  "target_store_id": 1,
  "member_id": 1,
  "points": 100,
  "order_id": 123,
  "settlement_rate": 1.0,
  "remarks": "跨店铺结算"
}
```

**响应**：
```json
{
  "id": 1,
  "source_store_id": 2,
  "target_store_id": 1,
  "member_id": 1,
  "points": 100,
  "settlement_date": "2026-01-08T22:00:00",
  "status": "pending",
  "settlement_amount": 100.0,
  "source_store_name": "奶茶店",
  "target_store_name": "火锅店",
  "member_name": "张三",
  "member_phone": "13800138000"
}
```

##### 1.2 获取结算详情
```
GET /api/settlement/store/{settlement_id}
```

##### 1.3 获取结算列表
```
GET /api/settlement/store/list
```

**查询参数**：
- `source_store_id`：来源店铺 ID
- `target_store_id`：目标店铺 ID
- `member_id`：会员 ID
- `status`：结算状态
- `date_from`：开始日期 (YYYY-MM-DD)
- `date_to`：结束日期 (YYYY-MM-DD)
- `page`：页码（默认 1）
- `page_size`：每页数量（默认 20）

---

#### 2. 第三方积分协议接口

##### 2.1 创建第三方协议
```
POST /api/settlement/third-party-agreements
```

**请求体**：
```json
{
  "store_id": 1,
  "third_party_name": "星巴克咖啡",
  "agreement_type": "bidirectional",
  "exchange_rate": 0.8,
  "max_points_per_day": 1000,
  "max_points_per_order": 200,
  "settlement_cycle": "daily",
  "valid_from": "2026-01-01",
  "valid_until": "2026-12-31",
  "contact_person": "李四",
  "contact_phone": "13900139000",
  "remarks": "星巴克积分合作协议"
}
```

**响应**：
```json
{
  "message": "第三方积分协议创建成功",
  "agreement_id": 1,
  "agreement": {
    "id": 1,
    "store_id": 1,
    "store_name": "火锅店",
    "third_party_name": "星巴克咖啡",
    "agreement_type": "bidirectional",
    "exchange_rate": 0.8,
    "status": "active",
    "created_at": "2026-01-08T22:00:00"
  }
}
```

##### 2.2 获取协议列表
```
GET /api/settlement/third-party-agreements
```

**查询参数**：
- `store_id`：店铺 ID
- `status`：状态
- `agreement_type`：协议类型

##### 2.3 获取协议详情
```
GET /api/settlement/third-party-agreements/{agreement_id}
```

---

#### 3. 积分兑换接口

##### 3.1 积分兑换
```
POST /api/settlement/exchange-points
```

**请求体**：
```json
{
  "member_id": 1,
  "store_id": 1,
  "agreement_id": 1,
  "exchange_type": "inbound",
  "points": 100,
  "order_id": 123,
  "remarks": "星巴克积分兑换"
}
```

**响应**：
```json
{
  "id": 1,
  "member_id": 1,
  "store_id": 1,
  "agreement_id": 1,
  "exchange_type": "inbound",
  "source_points": 100,
  "target_points": 80,
  "exchange_rate": 0.8,
  "status": "success",
  "created_at": "2026-01-08T22:00:00",
  "member_name": "张三",
  "store_name": "火锅店",
  "agreement_name": "星巴克咖啡"
}
```

##### 3.2 获取兑换日志
```
GET /api/settlement/exchange-logs
```

**查询参数**：
- `agreement_id`：协议 ID
- `member_id`：会员 ID
- `store_id`：店铺 ID
- `exchange_type`：兑换类型
- `status`：状态
- `page`：页码
- `page_size`：每页数量

---

#### 4. 统计接口

##### 4.1 获取结算统计
```
GET /api/settlement/statistics
```

**查询参数**：
- `store_id`：店铺 ID
- `date_from`：开始日期
- `date_to`：结束日期

**响应**：
```json
{
  "cross_store_settlements": {
    "total_settlements": 10,
    "pending_settlements": 2,
    "completed_settlements": 8,
    "total_points": 1000,
    "total_amount": 1000.0
  },
  "third_party_exchanges": {
    "total_exchanges": 50,
    "success_exchanges": 48,
    "failed_exchanges": 2,
    "total_inbound_points": 800,
    "total_outbound_points": 600,
    "net_points": 200
  },
  "agreements": {
    "total_agreements": 3,
    "active_agreements": 2
  },
  "summary": {
    "store_id": null,
    "date_from": null,
    "date_to": null
  }
}
```

---

## 管理界面

### 访问地址

- **跨店铺结算管理页面**：`/assets/settlement_management.html`

### 功能模块

1. **跨店铺结算**
   - 创建跨店铺结算
   - 查看结算记录列表
   - 支持按店铺、会员、状态筛选

2. **第三方协议**
   - 创建第三方积分合作协议
   - 查看协议列表和详情
   - 支持按店铺、状态、类型筛选

3. **积分兑换**
   - 执行积分兑换操作
   - 查看兑换日志
   - 支持按协议、会员、状态筛选

---

## 使用流程

### 场景 1：跨店铺结算

**步骤**：

1. **创建跨店铺结算**
   - 访问 `/assets/settlement_management.html`
   - 选择"跨店铺结算"标签页
   - 填写表单：
     - 积分来源店铺：店铺 B（积分拥有者）
     - 积分目标店铺：店铺 A（消费店铺）
     - 会员手机号：13800138000
     - 积分数量：100
     - 结算汇率：1.0（默认 1:1）
   - 点击"创建结算"

2. **系统自动处理**
   - 验证会员积分是否足够
   - 扣除会员 100 积分
   - 创建结算记录（状态：pending）
   - 记录积分日志

3. **后续结算**
   - 店铺 B 向店铺 A 结算 100 元（或积分）
   - 更新结算状态为 completed
   - 更新结算完成时间

---

### 场景 2：第三方积分兑换

**步骤**：

1. **创建第三方协议**
   - 访问 `/assets/settlement_management.html`
   - 选择"第三方协议"标签页
   - 填写表单：
     - 本店铺：火锅店
     - 第三方公司名称：星巴克咖啡
     - 协议类型：双向互通
     - 积分兑换比例：0.8
     - 每日限额：1000
     - 单笔订单限额：200
   - 点击"创建协议"

2. **执行积分兑换**
   - 访问 `/assets/settlement_management.html`
   - 选择"积分兑换"标签页
   - 填写表单：
     - 第三方协议：星巴克咖啡
     - 会员手机号：13800138000
     - 兑换类型：第三方积分 → 本方积分
     - 积分数量：100
   - 点击"执行兑换"

3. **系统自动处理**
   - 验证协议是否有效
   - 检查每日/单笔限额
   - 计算目标积分：100 × 0.8 = 80
   - 增加会员 80 积分
   - 创建兑换日志（状态：success）
   - 更新协议结算余额

---

## 数据库表结构

### 1. store_point_settlements（跨店铺结算表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键 |
| source_store_id | int | 积分来源店铺 ID |
| target_store_id | int | 积分目标店铺 ID |
| member_id | int | 会员 ID |
| points | int | 积分数量 |
| settlement_date | datetime | 结算日期 |
| status | string | 结算状态（pending, completed, cancelled） |
| order_id | int | 关联订单 ID |
| point_log_id | int | 关联积分日志 ID |
| settlement_rate | float | 结算汇率 |
| settlement_amount | float | 结算金额 |
| completed_at | datetime | 完成时间 |
| remarks | text | 备注 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 2. third_party_point_agreements（第三方积分协议表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键 |
| store_id | int | 本店铺 ID |
| company_id | int | 第三方公司 ID（内部） |
| third_party_name | string | 第三方公司名称 |
| third_party_store_id | string | 第三方店铺 ID（外部） |
| agreement_type | string | 协议类型（bidirectional, inbound, outbound） |
| exchange_rate | float | 积分兑换比例 |
| max_points_per_day | int | 每日最大兑换积分数 |
| max_points_per_order | int | 单笔订单最大兑换积分数 |
| settlement_cycle | string | 结算周期（daily, weekly, monthly） |
| status | string | 状态（active, suspended, terminated） |
| valid_from | date | 生效日期 |
| valid_until | date | 到期日期 |
| api_endpoint | string | 第三方 API 地址 |
| api_key | string | 第三方 API 密钥 |
| settlement_balance | float | 结算余额 |
| last_settlement_date | datetime | 上次结算日期 |
| contact_person | string | 联系人 |
| contact_phone | string | 联系电话 |
| remarks | text | 备注 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 3. point_exchange_logs（积分兑换日志表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | int | 主键 |
| member_id | int | 会员 ID |
| store_id | int | 店铺 ID |
| agreement_id | int | 第三方协议 ID |
| exchange_type | string | 兑换类型（inbound, outbound） |
| source_points | int | 源积分数量 |
| target_points | int | 目标积分数量 |
| exchange_rate | float | 兑换比例 |
| order_id | int | 关联订单 ID |
| third_party_order_no | string | 第三方订单号 |
| status | string | 状态（pending, success, failed, cancelled） |
| error_message | text | 错误信息 |
| completed_at | datetime | 完成时间 |
| remarks | text | 备注 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

---

## 部署说明

### 1. 数据库迁移

运行迁移脚本创建新表：
```bash
python scripts/migrate_to_cross_store_settlement.py
```

### 2. 启动结算 API 服务

```bash
python -m src.api.settlement_api
```

服务将在端口 8003 启动。

### 3. 访问管理界面

访问 `/assets/settlement_management.html` 进行跨店铺结算和第三方积分管理。

---

## 常见问题

### Q1：跨店铺结算如何实现资金流转？

**A**：跨店铺结算主要记录积分的使用情况，实际资金结算需要线下或通过其他渠道完成：
1. 店铺 B（积分来源）需要向店铺 A（消费店铺）结算对应金额
2. 可以定期（如每月）进行对账和结算
3. 结算完成后，更新结算状态为 completed

### Q2：第三方积分兑换如何保证数据一致性？

**A**：系统采用以下机制保证一致性：
1. 验证协议有效期和限额
2. 使用数据库事务确保原子性
3. 记录详细的兑换日志
4. 支持结算余额追踪
5. 提供统计报表便于对账

### Q3：如何处理兑换失败的情况？

**A**：系统提供完整的错误处理机制：
1. 兑换失败时记录错误信息
2. 不扣除会员积分（只检查，不扣除）
3. 状态标记为 failed
4. 管理员可以查看错误日志并重试

### Q4：积分汇率如何设置？

**A**：支持两种方式设置汇率：
1. **跨店铺结算**：`settlement_rate` 字段，默认 1.0（1:1）
2. **第三方兑换**：`exchange_rate` 字段，例如 0.8（1 第三方积分 = 0.8 本方积分）

### Q5：如何防止积分滥用？

**A**：系统提供多种限制机制：
1. 每日最大兑换限额
2. 单笔订单最大兑换限额
3. 协议有效期限制
4. 协议状态控制（可暂停、终止）
5. 详细的审计日志

---

## 更新日志

### v1.0.0 (2026-01-08)

**新增功能**：
- 跨店铺结算系统
- 第三方积分协议管理
- 积分兑换功能
- 结算统计报表
- 管理界面

**技术实现**：
- 新增 3 个数据表
- 新增 12 个 API 接口
- 新增管理界面页面
- 数据库迁移脚本

---

## 联系方式

如有问题或建议，请联系开发团队。
