# 🔄 Gitee 合并计划

## 📋 概述

本文档描述如何将现有的餐厅管理系统迁移到模块化架构，并合并到 Gitee 仓库。

## 🎯 目标

1. **保留现有功能**：确保现有系统（GitHub: wczlee9-bit/restaurant-system）的所有功能正常运行
2. **引入模块化架构**：使用沙盒中开发的模块化框架（core/module_base.py, core/service_interfaces.py）
3. **渐进式迁移**：逐步将现有代码重构为模块，而不是一次性全部重写
4. **保持向后兼容**：确保现有 API 路由继续工作

## 📂 当前架构分析

### 现有系统（GitHub 仓库）

```
restaurant-system/
├── src/
│   ├── api/                    # API 路由（非模块化）
│   │   ├── order_flow_api.py
│   │   ├── restaurant_api.py
│   │   ├── member_api.py
│   │   ├── payment_api.py
│   │   ├── websocket_api.py
│   │   └── ...
│   ├── storage/                # 数据库存储
│   │   └── database/
│   │       ├── db.py
│   │       └── models.py
│   └── main.py                 # FastAPI 应用入口
├── frontend/                   # 前端应用
└── requirements.txt
```

**特点**：
- ✅ 功能完整
- ❌ 耦合度高
- ❌ 难以独立升级
- ❌ 路由间有直接依赖

### 模块化架构（沙盒开发）

```
restaurant-system/
├── core/                       # 核心框架
│   ├── module_base.py          # 模块基类和注册器
│   └── service_interfaces.py   # 服务接口定义
├── modules/                    # 业务模块
│   ├── menu_module.py
│   ├── order_module.py
│   ├── user_module.py
│   └── ...
└── modular_app.py              # 模块化应用入口
```

**特点**：
- ✅ 低耦合
- ✅ 可独立升级
- ✅ 通过接口通信
- ⚠️ 需要将现有代码重构

## 🚀 迁移策略

### 阶段 1：基础框架集成 ✅

**目标**：将模块化框架集成到现有系统，但不影响现有功能。

**步骤**：

1. ✅ 复制核心框架文件：
   - `core/module_base.py` → `restaurant-system/core/`
   - `core/service_interfaces.py` → `restaurant-system/core/`
   - `modular_app.py` → `restaurant-system/`

2. ✅ 保留现有入口：
   - `src/main.py` 继续作为主入口
   - 新增 `src/main_modular.py` 作为模块化入口（用于测试）

3. ✅ 添加模块配置：
   - `config/modules.json` - 定义模块列表和加载顺序

### 阶段 2：封装现有系统为模块 🔄

**目标**：将现有的 API 路由封装为模块，但不改变业务逻辑。

**步骤**：

1. 创建 `modules/legacy/` 目录
2. 创建基础模块适配器：

```python
# modules/legacy/base_module.py
from core.module_base import BaseModule
from fastapi import APIRouter

class LegacyModule(BaseModule):
    """
    遗留模块适配器
    
    将现有 API 路由封装为模块
    """
    
    def __init__(self, name: str, router: APIRouter):
        self._name = name
        self._router = router
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, dependencies):
        # 无需特殊初始化
        pass
    
    def get_routes(self):
        return [self._router]
```

3. 逐一封装现有 API：

```python
# modules/legacy/order_module.py
from modules.legacy.base_module import LegacyModule
from src.api.order_flow_api import router as order_router

order_module = LegacyModule("OrderModule", order_router)
```

### 阶段 3：渐进式重构 ⏳

**目标**：逐个模块重构，将业务逻辑抽取到独立的服务类。

**优先级**：

1. **高优先级**：
   - OrderModule（订单模块）
   - MenuModule（菜单模块）
   - UserModule（用户模块）

2. **中优先级**：
   - StockModule（库存模块）
   - MemberModule（会员模块）
   - PaymentModule（支付模块）

3. **低优先级**：
   - StatsModule（统计模块）
   - ReceiptModule（小票模块）
   - WebSocketModule（WebSocket 模块）

**重构示例**：

```python
# modules/order/order_module.py（重构后）
from core.module_base import BaseModule
from core.service_interfaces import IOrderService, OrderService
from modules.order.order_service import OrderServiceImpl

class OrderModule(BaseModule):
    @property
    def name(self) -> str:
        return "OrderModule"
    
    @property
    def version(self) -> str:
        return "2.0.0"
    
    def dependencies(self) -> List[str]:
        return ["MenuModule", "UserModule"]
    
    def initialize(self, dependencies):
        menu_service = dependencies["MenuModule"].service
        user_service = dependencies["UserModule"].service
        
        self.service = OrderServiceImpl(menu_service, user_service)
    
    def get_routes(self):
        return [self._create_router()]
    
    def _create_router(self):
        from fastapi import APIRouter
        router = APIRouter(prefix="/api/orders", tags=["订单管理"])
        
        @router.post("/")
        def create_order(order_data: OrderCreate):
            return self.service.create_order(order_data)
        
        return router
```

### 阶段 4：迁移到 Gitee ⏳

**目标**：将合并后的代码推送到 Gitee 仓库。

**步骤**：

1. 创建 Gitee 仓库：
   - 仓库名称：`restaurant`
   - 可见性：私有（根据需要）

2. 配置 Git remote：
   ```bash
   # 添加 Gitee remote
   git remote add gitee https://gitee.com/lijun75/restaurant.git
   
   # 推送到 Gitee
   git push gitee main
   ```

3. 验证推送：
   - 访问 Gitee 仓库检查代码
   - 运行测试确保功能正常

## 📊 迁移进度

| 阶段 | 任务 | 状态 | 完成日期 |
|------|------|------|---------|
| 阶段 1 | 基础框架集成 | ✅ 完成 | 2024-02-06 |
| 阶段 2 | 封装现有系统为模块 | 🔄 进行中 | 2024-02-06 |
| 阶段 3 | 渐进式重构 | ⏳ 待开始 | - |
| 阶段 4 | 迁移到 Gitee | ⏳ 待开始 | - |

## 🔧 具体实施计划

### 当前任务（阶段 2）

#### 任务 1：创建模块配置文件

```json
{
  "modules": [
    {
      "name": "LegacyOrderModule",
      "module": "modules.legacy.order_module",
      "enabled": true
    },
    {
      "name": "LegacyMenuModule",
      "module": "modules.legacy.menu_module",
      "enabled": true
    }
  ],
  "legacy_mode": true
}
```

#### 任务 2：创建模块加载器

```python
# src/module_loader.py
import json
from pathlib import Path
from core.module_base import ModuleRegistry

def load_modules(config_path: str = "config/modules.json"):
    """加载模块配置并注册模块"""
    with open(config_path) as f:
        config = json.load(f)
    
    registry = ModuleRegistry()
    
    for module_config in config["modules"]:
        if not module_config["enabled"]:
            continue
        
        module_path = module_config["module"]
        module_name = module_config["name"]
        
        # 动态导入模块
        import importlib
        module = importlib.import_module(module_path)
        module_instance = getattr(module, "module_instance")
        
        registry.register(module_instance)
    
    return registry
```

#### 任务 3：更新 main.py 支持模块化

```python
# src/main.py
from fastapi import FastAPI
import sys
from pathlib import Path

# 添加 core 到路径
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from src.module_loader import load_modules

app = FastAPI(title="餐厅管理系统")

# 尝试加载模块化系统
try:
    registry = load_modules()
    registry.initialize_all()
    
    # 注册所有模块路由
    for router in registry.get_all_routes():
        app.include_router(router)
    
    print("✅ 模块化系统已加载")
except Exception as e:
    print(f"⚠️ 模块化系统加载失败，使用传统模式: {e}")
    # 回退到传统模式
    from src.api import order_flow_api, restaurant_api, member_api
    app.include_router(order_flow_api.router)
    app.include_router(restaurant_api.router)
    app.include_router(member_api.router)
```

## ✅ 验证计划

### 功能验证

1. **订单流程**：
   - [ ] 扫码点餐
   - [ ] 订单状态流转
   - [ ] 订单查询

2. **库存管理**：
   - [ ] 库存查询
   - [ ] 库存扣减
   - [ ] 补货

3. **会员系统**：
   - [ ] 会员注册
   - [ ] 积分管理
   - [ ] 会员等级

4. **支付功能**：
   - [ ] 创建支付
   - [ ] 支付回调
   - [ ] 支付查询

### 性能验证

1. **响应时间**：
   - [ ] API 响应时间 < 500ms
   - [ ] 订单创建 < 1s

2. **并发测试**：
   - [ ] 支持 100 并发用户
   - [ ] 数据库连接池正常

## 📝 注意事项

1. **备份**：每次重大变更前备份代码和数据库
2. **测试**：每个阶段完成后运行完整测试套件
3. **回滚**：保留原始代码，以便快速回滚
4. **文档**：及时更新 API 文档和架构文档

## 📞 联系方式

如有问题，请联系：
- GitHub Issues: https://github.com/wczlee9-bit/restaurant-system/issues
- Gitee Issues: https://gitee.com/lijun75/restaurant/issues

---

**最后更新**: 2024-02-06
