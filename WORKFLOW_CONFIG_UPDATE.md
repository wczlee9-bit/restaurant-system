# ⚙️ 订单流程配置功能 - 开发进度

## 📋 功能概述

实现灵活的订单流程配置，让店铺可以自定义每个角色在每个环节的操作方式：

- ✅ **厨师做菜环节**：可以逐项确认、按订单确认、跳过或忽略
- ✅ **传菜环节**：可以按订单确认、跳过或忽略
- ✅ **每个角色每个环节**：都可以独立配置是否启用以及操作模式

---

## ✅ 已完成工作

### 1. 数据库设计
**文件**: `src/storage/database/shared/model.py`

新增表：`workflow_config`（订单流程配置表）

**字段说明**:
- `store_id`: 店铺ID
- `role`: 角色（kitchen=厨师, waiter=传菜员, cashier=收银员, manager=店长）
- `status`: 订单状态（pending=待确认, preparing=制作中, ready=待传菜, serving=上菜中, completed=已完成）
- `action_mode`: 操作模式
  - `per_item`: 逐项确认（每道菜单独确认）
  - `per_order`: 订单确认（整个订单一起确认）
  - `skip`: 自动跳过（自动流转到下一状态）
  - `ignore`: 忽略不显示（不显示该状态）
- `is_enabled`: 是否启用该环节

### 2. 数据库迁移脚本
**文件**: `scripts/init_workflow_config.py`

- ✅ 创建 `workflow_config` 表
- ✅ 为所有店铺创建默认配置
- ✅ 已执行初始化，5个店铺各创建6条配置

**默认配置**:
| 角色 | 状态 | 操作模式 | 说明 |
|------|------|----------|------|
| 厨师 | pending | per_item | 待确认订单（逐项确认） |
| 厨师 | preparing | per_item | 制作中（逐项确认） |
| 传菜员 | ready | per_order | 待传菜（订单确认） |
| 传菜员 | serving | per_order | 上菜中（订单确认） |
| 收银员 | completed | skip | 订单完成（自动跳过，未启用） |
| 店长 | completed | skip | 订单完成（自动跳过） |

### 3. 后端API接口
**文件**: `src/api/workflow_api.py`

已创建完整的CRUD接口：

- ✅ `GET /api/workflow-config/` - 获取所有配置
- ✅ `GET /api/workflow-config/by-role/{role}` - 获取指定角色的配置
- ✅ `PATCH /api/workflow-config/{config_id}` - 更新单个配置
- ✅ `POST /api/workflow-config/bulk-update` - 批量更新配置
- ✅ `POST /api/workflow-config/reset-defaults` - 重置为默认配置
- ✅ `GET /api/workflow-config/action-mode/{role}/{status}` - 获取操作模式（用于前端判断）

### 4. 店铺设置页面
**文件**: `assets/shop_settings.html`

- ✅ 添加"流程配置"Tab
- ✅ 按角色分组显示配置（厨师、传菜员、收银员、店长）
- ✅ 每个配置项可以设置：
  - 操作模式（下拉选择：逐项确认/订单确认/自动跳过/忽略不显示）
  - 是否启用（开关）
  - 显示操作模式说明
- ✅ 批量保存配置功能
- ✅ 重置为默认配置功能
- ✅ 配置说明提示

---

## 🚧 待完成工作

### 1. 厨师端逻辑修改
**文件**: `assets/staff_workflow.html`

**需要实现**:
- 读取厨师角色的流程配置
- 根据 `action_mode` 显示不同的操作界面：
  - **per_item（逐项确认）**：每道菜一个"制作完成"按钮
  - **per_order（订单确认）**：订单级别一个"订单完成"按钮
  - **skip（自动跳过）**：自动将订单状态从 `pending` 流转到 `ready`
  - **ignore（忽略不显示）**：不显示 `pending` 或 `preparing` 状态的订单

**实现步骤**:
```javascript
// 1. 加载厨师配置
async function loadKitchenConfig() {
    const response = await fetch('http://localhost:8000/api/workflow-config/by-role/kitchen');
    const configs = await response.json();

    // 获取 pending 和 preparing 状态的配置
    const pendingConfig = configs.find(c => c.status === 'pending');
    const preparingConfig = configs.find(c => c.status === 'preparing');

    // 根据配置显示不同的界面
    if (pendingConfig?.action_mode === 'per_item') {
        // 显示每道菜的确认按钮
    } else if (pendingConfig?.action_mode === 'per_order') {
        // 显示订单级别的确认按钮
    } else if (pendingConfig?.action_mode === 'skip' || !pendingConfig?.is_enabled) {
        // 自动跳过，不显示
    }
}
```

### 2. 传菜员端逻辑修改
**文件**: `assets/staff_workflow.html`

**需要实现**:
- 读取传菜员角色的流程配置
- 根据 `action_mode` 显示不同的操作界面：
  - **per_order（订单确认）**：订单级别一个"上菜完成"按钮
  - **skip（自动跳过）**：自动将订单状态从 `ready` 流转到 `completed`
  - **ignore（忽略不显示）**：不显示 `ready` 或 `serving` 状态的订单

### 3. 订单状态自动流转
**文件**: `src/api/restaurant_api.py`

**需要实现**:
- 在创建订单或更新订单状态时，检查配置
- 如果某个状态的配置是 `skip`，自动跳过该状态
- 如果某个状态的配置是 `ignore`，直接跳过该状态

**实现逻辑**:
```python
def auto_skip_status(order_id, role, current_status):
    """根据配置自动跳过状态"""
    config = get_workflow_config(role, current_status)

    if config and config.action_mode == 'skip':
        # 自动流转到下一个状态
        next_status = get_next_status(current_status)
        update_order_status(order_id, next_status)

        # 递归检查下一个状态是否也需要跳过
        auto_skip_status(order_id, role, next_status)
```

### 4. API订单创建逻辑优化
**文件**: `src/api/restaurant_api.py`

**需要实现**:
- 订单创建后，检查厨师 `pending` 状态的配置
- 如果配置为 `skip`，自动将订单流转到 `ready` 状态
- 如果配置为 `ignore`，直接将订单流转到 `serving` 状态

### 5. 测试所有配置模式

**测试场景**:

| 配置场景 | 预期行为 |
|---------|---------|
| 厨师 per_item | 每道菜单独显示"制作完成"按钮 |
| 厨师 per_order | 订单显示"订单完成"按钮，所有菜品一起确认 |
| 厨师 skip | 订单自动从 pending → ready |
| 传菜员 per_order | 订单显示"上菜完成"按钮 |
| 传菜员 skip | 订单自动从 ready → completed |
| ignore 模式 | 对应状态不显示 |

---

## 🎯 配置使用示例

### 示例1：小餐厅（快速模式）
**配置**:
- 厨师 pending: skip
- 厨师 preparing: skip
- 传菜员 ready: skip
- 传菜员 serving: skip

**效果**:
- 订单提交后自动完成，无需任何确认
- 适合快餐厅或简单餐饮场景

### 示例2：标准餐厅（推荐）
**配置**:
- 厨师 pending: per_item（默认）
- 厨师 preparing: per_item（默认）
- 传菜员 ready: per_order（默认）
- 传菜员 serving: per_order（默认）

**效果**:
- 厨师每道菜单独确认
- 传菜员按订单确认
- 适合大多数餐厅

### 示例3：高端餐厅（精细管理）
**配置**:
- 厨师 pending: per_order（订单级确认）
- 厨师 preparing: per_item（逐项确认）
- 传菜员 ready: per_order（订单级确认）
- 传菜员 serving: per_order（订单级确认）

**效果**:
- 厨师先确认订单，再逐道菜确认
- 传菜员按订单确认
- 适合对服务质量要求高的餐厅

---

## 📝 API调用示例

### 获取厨师配置
```bash
curl http://localhost:8000/api/workflow-config/by-role/kitchen
```

**响应**:
```json
[
  {
    "id": 1,
    "status": "pending",
    "action_mode": "per_item",
    "is_enabled": true
  },
  {
    "id": 2,
    "status": "preparing",
    "action_mode": "per_item",
    "is_enabled": true
  }
]
```

### 获取操作模式（前端判断用）
```bash
curl "http://localhost:8000/api/workflow-config/action-mode/kitchen/preparing"
```

**响应**:
```json
{
  "action_mode": "per_item",
  "is_enabled": true
}
```

### 批量更新配置
```bash
curl -X POST http://localhost:8000/api/workflow-config/bulk-update \
  -H "Content-Type: application/json" \
  -d '{
    "configs": [
      {"id": 1, "action_mode": "per_order", "is_enabled": true},
      {"id": 2, "action_mode": "skip", "is_enabled": true}
    ]
  }'
```

---

## 🔧 技术要点

### 1. 配置读取
```javascript
// 读取配置并缓存
const workflowConfigs = ref({});

async function loadWorkflowConfig(role) {
    const response = await fetch(`http://localhost:8000/api/workflow-config/by-role/${role}`);
    workflowConfigs.value[role] = await response.json();
}
```

### 2. 状态判断
```javascript
// 判断某个状态是否需要显示
function shouldShowStatus(role, status) {
    const configs = workflowConfigs.value[role] || [];
    const config = configs.find(c => c.status === status);
    return config && config.is_enabled && config.action_mode !== 'ignore';
}
```

### 3. 操作模式判断
```javascript
// 判断操作模式
function getActionMode(role, status) {
    const configs = workflowConfigs.value[role] || [];
    const config = configs.find(c => c.status === status);
    return config ? config.action_mode : 'skip';
}
```

---

## 📊 数据库表结构

### workflow_config 表
```sql
CREATE TABLE workflow_config (
    id SERIAL PRIMARY KEY,
    store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,              -- 角色
    status VARCHAR(50) NOT NULL,            -- 订单状态
    action_mode VARCHAR(50) NOT NULL,       -- 操作模式
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE, -- 是否启用
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(store_id, role, status)
);
```

---

## 🚀 下一步计划

1. **完成厨师端逻辑修改**（优先级：高）
   - 加载配置
   - 根据 action_mode 显示不同的操作界面
   - 实现逐项确认和订单确认

2. **完成传菜员端逻辑修改**（优先级：高）
   - 加载配置
   - 根据 action_mode 显示不同的操作界面

3. **实现订单自动流转**（优先级：中）
   - 订单创建后检查 pending 状态配置
   - 状态更新时检查下一个状态配置

4. **测试所有配置模式**（优先级：中）
   - 测试 per_item 模式
   - 测试 per_order 模式
   - 测试 skip 模式
   - 测试 ignore 模式

5. **优化用户体验**（优先级：低）
   - 添加配置预览功能
   - 添加配置模板（快速模式、标准模式、精细模式）
   - 添加配置导出/导入功能

---

## 📞 常见问题

### Q: 配置修改后立即生效吗？
A: 是的，前端会在页面刷新后重新加载配置。也可以添加实时监听配置变更的功能。

### Q: 如何快速测试不同的配置模式？
A: 可以在店铺设置的"流程配置"页面直接修改配置并保存，然后创建订单测试效果。

### Q: 配置会影响已创建的订单吗？
A: 不会。配置只影响新创建的订单和待处理的订单。

### Q: 可以针对不同的桌号设置不同的配置吗？
A: 目前不支持。配置是基于店铺的，所有桌号使用相同的配置。如果需要，可以扩展为支持桌号级别的配置。

---

## 📚 相关文档

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 部署指南
- [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) - 部署摘要
- [FEATURE_UPDATE_20240108.md](assets/FEATURE_UPDATE_20240108.md) - 功能更新说明
- [API文档](http://localhost:8000/docs) - 完整API文档

---

**更新时间**: 2024-01-08
**开发状态**: 🚧 进行中（已完成基础功能，待完善前端逻辑）
