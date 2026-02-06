# 🏗️ 多店铺扫码点餐系统 - 模块化架构设计

## 📐 架构原则

### 核心原则
1. **高内聚低耦合**：每个模块专注于单一职责
2. **接口驱动**：模块间通过接口通信，而非直接依赖
3. **可插拔设计**：模块可以独立升级、替换
4. **向后兼容**：升级模块不影响其他模块

### 模块化目标
- ✅ 升级订单模块 → 不影响统计模块
- ✅ 升级支付模块 → 不影响库存模块
- ✅ 新增会员功能 → 不影响核心业务
- ✅ 替换数据库 → 只改数据访问层

---

## 📦 模块划分

### 1. 核心业务模块

| 模块名称 | 职责 | 接口 | 依赖 |
|---------|------|------|------|
| **AuthModule** | 认证授权 | `AuthService` | 无 |
| **UserModule** | 用户管理 | `UserService` | AuthModule |
| **MenuModule** | 菜品管理 | `MenuService` | 无 |
| **OrderModule** | 订单管理 | `OrderService` | MenuModule, UserModule |
| **PaymentModule** | 支付处理 | `PaymentService` | OrderModule |
| **StockModule** | 库存管理 | `StockService` | MenuModule |
| **MemberModule** | 会员积分 | `MemberService` | UserModule, OrderModule |
| **StatsModule** | 统计分析 | `StatsService` | OrderModule, MemberModule |
| **ReceiptModule** | 小票打印 | `ReceiptService` | OrderModule |
| **WebSocketModule** | 实时通信 | `WebSocketService` | OrderModule |

### 2. 基础设施模块

| 模块名称 | 职责 | 接口 | 依赖 |
|---------|------|------|------|
| **DatabaseModule** | 数据持久化 | `DatabaseService` | 无 |
| **CacheModule** | 缓存服务 | `CacheService` | 无 |
| **LogModule** | 日志服务 | `LogService` | 无 |
| **ConfigModule** | 配置管理 | `ConfigService` | 无 |

---

## 🔌 模块接口设计

### 模块接口规范

每个模块必须实现以下接口：

```python
# 模块基础接口
class BaseModule:
    """所有模块的基础接口"""
    
    @property
    def name(self) -> str:
        """模块名称"""
        pass
    
    @property
    def version(self) -> str:
        """模块版本"""
        pass
    
    def dependencies(self) -> List[str]:
        """依赖的模块列表"""
        pass
    
    def initialize(self, dependencies: Dict[str, 'BaseModule']):
        """初始化模块"""
        pass
    
    def shutdown(self):
        """关闭模块"""
        pass
```

### 示例：订单模块接口

```python
class OrderModule(BaseModule):
    """订单模块接口"""
    
    @property
    def name(self) -> str:
        return "OrderModule"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def dependencies(self) -> List[str]:
        return ["MenuModule", "UserModule"]
    
    def initialize(self, dependencies: Dict[str, 'BaseModule']):
        self.menu_service = dependencies["MenuModule"].service
        self.user_service = dependencies["UserModule"].service
    
    # 业务接口
    def create_order(self, order_data: OrderCreate) -> Order:
        """创建订单"""
        pass
    
    def get_order(self, order_id: int) -> Order:
        """获取订单"""
        pass
    
    def update_order_status(self, order_id: int, status: str) -> bool:
        """更新订单状态"""
        pass
```

---

## 📂 项目结构

```
/workspace/projects/
├── core/                          # 核心框架
│   ├── module_base.py            # 模块基类
│   ├── module_registry.py        # 模块注册器
│   └── interfaces/               # 接口定义
│       ├── auth_service.py
│       ├── menu_service.py
│       ├── order_service.py
│       └── ...
│
├── modules/                       # 业务模块
│   ├── auth/                     # 认证模块
│   │   ├── __init__.py
│   │   ├── module.py             # 模块实现
│   │   ├── service.py            # 业务服务
│   │   └── routes/               # API 路由
│   │       └── auth_routes.py
│   │
│   ├── menu/                     # 菜单模块
│   │   ├── __init__.py
│   │   ├── module.py
│   │   ├── service.py
│   │   └── routes/
│   │       └── menu_routes.py
│   │
│   ├── order/                    # 订单模块
│   │   ├── __init__.py
│   │   ├── module.py
│   │   ├── service.py
│   │   ├── routes/
│   │   │   └── order_routes.py
│   │   └── events/               # 事件定义
│   │       ├── order_created.py
│   │       └── order_updated.py
│   │
│   ├── payment/                  # 支付模块
│   │   ├── __init__.py
│   │   ├── module.py
│   │   ├── service.py
│   │   └── strategies/           # 支付策略
│   │       ├── wechat_pay.py
│   │       └── alipay.py
│   │
│   ├── stock/                    # 库存模块
│   │   ├── __init__.py
│   │   ├── module.py
│   │   ├── service.py
│   │   └── routes/
│   │       └── stock_routes.py
│   │
│   ├── member/                   # 会员模块
│   │   ├── __init__.py
│   │   ├── module.py
│   │   ├── service.py
│   │   └── routes/
│   │       └── member_routes.py
│   │
│   ├── stats/                    # 统计模块
│   │   ├── __init__.py
│   │   ├── module.py
│   │   ├── service.py
│   │   └── routes/
│   │       └── stats_routes.py
│   │
│   ├── receipt/                  # 小票模块
│   │   ├── __init__.py
│   │   ├── module.py
│   │   ├── service.py
│   │   └── routes/
│   │       └── receipt_routes.py
│   │
│   └── websocket/                # WebSocket 模块
│       ├── __init__.py
│       ├── module.py
│       ├── service.py
│       └── routes/
│           └── websocket_routes.py
│
├── infrastructure/               # 基础设施模块
│   ├── database/
│   │   ├── __init__.py
│   │   ├── module.py
│   │   ├── models.py            # 数据模型
│   │   └── repositories/        # 数据仓库
│   │       ├── base_repository.py
│   │       ├── order_repository.py
│   │       └── menu_repository.py
│   │
│   ├── cache/
│   │   ├── __init__.py
│   │   └── module.py
│   │
│   └── config/
│       ├── __init__.py
│       └── module.py
│
├── events/                       # 事件系统（模块间通信）
│   ├── __init__.py
│   ├── event_bus.py             # 事件总线
│   └── handlers/                # 事件处理器
│       ├── order_created_handler.py
│       └── payment_completed_handler.py
│
├── api/                          # API 聚合层
│   ├── __init__.py
│   ├── main.py                  # FastAPI 应用入口
│   └── router_builder.py        # 路由构建器
│
└── shared/                       # 共享代码
    ├── schemas/                 # 数据模型
    ├── constants/               # 常量定义
    └── utils/                   # 工具函数
```

---

## 🔄 模块间通信

### 方式1：依赖注入

```python
class OrderModule(BaseModule):
    def initialize(self, dependencies: Dict[str, 'BaseModule']):
        self.menu_service = dependencies["MenuModule"].service
        self.user_service = dependencies["UserModule"].service
    
    def create_order(self, order_data):
        # 使用注入的服务
        menu_item = self.menu_service.get_item(order_data.item_id)
        user = self.user_service.get_user(order_data.user_id)
        # ...
```

### 方式2：事件驱动（推荐）

```python
# 订单模块发布事件
class OrderModule(BaseModule):
    def create_order(self, order_data):
        order = Order.create(order_data)
        # 发布订单创建事件
        event_bus.publish("order.created", {
            "order_id": order.id,
            "items": order.items
        })
        return order

# 库存模块订阅事件
class StockModule(BaseModule):
    def initialize(self, dependencies):
        event_bus.subscribe("order.created", self.handle_order_created)
    
    def handle_order_created(self, event_data):
        # 扣减库存
        for item in event_data["items"]:
            self.deduct_stock(item["id"], item["quantity"])
```

---

## 🚀 模块升级流程

### 场景1：升级订单模块

```bash
# 1. 备份原模块
cp -r modules/order modules/order.bak

# 2. 替换新版本
rm -rf modules/order
cp -r new_modules/order modules/order

# 3. 更新模块配置
# 编辑 modules/order/module.py，更新版本号

# 4. 重启服务（可选，支持热更新）
# 或直接部署，其他模块不受影响
```

### 场景2：新增支付方式

```python
# 只需在 payment/strategies/ 下新增文件
# payment/strategies/union_pay.py

class UnionPayStrategy:
    def process_payment(self, amount):
        # 银联支付逻辑
        pass

# 注册新策略
payment_module.register_strategy("union_pay", UnionPayStrategy())
```

### 场景3：替换数据库

```python
# 只需修改 infrastructure/database/module.py
# 其他业务模块无需改动

class DatabaseModule(BaseModule):
    def initialize(self):
        # 从 PostgreSQL 切换到 MySQL
        self.engine = create_engine("mysql://...")
        
        # 或者从 SQL 切换到 NoSQL
        # self.client = MongoClient("mongodb://...")
```

---

## 📋 模块清单

### 已实现的模块

| 模块 | 状态 | 版本 | 说明 |
|------|------|------|------|
| DatabaseModule | ✅ | 1.0.0 | 数据持久化（SQLite） |
| AuthModule | ✅ | 1.0.0 | 认证授权 |
| MenuModule | ✅ | 1.0.0 | 菜品管理 |
| OrderModule | ✅ | 1.0.0 | 订单管理 |
| StockModule | ✅ | 1.0.0 | 库存管理 |
| MemberModule | ✅ | 1.0.0 | 会员积分 |
| StatsModule | ✅ | 1.0.0 | 统计分析 |
| ReceiptModule | ✅ | 1.0.0 | 小票打印 |
| WebSocketModule | ✅ | 1.0.0 | 实时通信 |

### 计划中的模块

| 模块 | 优先级 | 说明 |
|------|--------|------|
| PaymentModule | 高 | 支付处理（微信/支付宝） |
| NotificationModule | 中 | 消息通知（短信/邮件） |
| ReportModule | 中 | 报表生成 |
| PromotionModule | 低 | 促销活动 |
| ReservationModule | 低 | 预约订座 |

---

## 🎯 模块化优势

### 1. 独立开发
- 不同团队可以并行开发不同模块
- 减少代码冲突
- 加快开发速度

### 2. 独立测试
- 每个模块可以独立测试
- 提高测试覆盖率
- 快速定位问题

### 3. 独立部署
- 支持灰度发布
- 按需升级
- 降低风险

### 4. 易于维护
- 问题定位精准
- 代码量可控
- 降低复杂度

---

## 📝 模块开发规范

### 必须遵守的规范

1. **模块独立性**
   - 模块不能直接依赖其他模块的具体实现
   - 只能通过接口通信

2. **版本管理**
   - 每个模块必须有版本号
   - 遵循语义化版本（Semantic Versioning）

3. **接口稳定**
   - 公共接口不能随意修改
   - 如需修改，提供兼容方案

4. **错误处理**
   - 模块内处理异常
   - 通过统一的错误码返回

5. **日志规范**
   - 使用统一的日志格式
   - 包含模块名称

### 模块开发模板

```python
"""
模块名称：XXX模块
模块版本：1.0.0
作者：XXX
说明：XXX模块的功能说明
"""

from core.module_base import BaseModule
from core.interfaces.xxx_service import XXXService

class XXXModule(BaseModule):
    """XXX模块实现"""
    
    @property
    def name(self) -> str:
        return "XXXModule"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def dependencies(self) -> List[str]:
        """依赖的模块"""
        return []
    
    def initialize(self, dependencies: Dict[str, 'BaseModule']):
        """初始化模块"""
        self.service = XXXService()
        print(f"{self.name} v{self.version} initialized")
    
    def shutdown(self):
        """关闭模块"""
        print(f"{self.name} shutdown")
```

---

## 🔍 验证模块独立性

### 检查清单

- [ ] 模块可以独立编译
- [ ] 模块可以独立测试
- [ ] 模块可以独立运行
- [ ] 模块可以独立升级
- [ ] 模块可以独立替换
- [ ] 模块有清晰的接口定义
- [ ] 模块有版本管理
- [ ] 模块有错误处理

---

**文档版本**：1.0.0  
**最后更新**：2025-02-06  
**维护者**：Coze Coding
