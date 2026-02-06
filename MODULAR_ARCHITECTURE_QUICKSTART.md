# 🚀 模块化架构快速开始指南

## 📋 概述

本指南帮助您快速了解和使用新的模块化架构。

## 🎯 什么是模块化架构？

模块化架构是一种将系统划分为独立、可插拔模块的设计方式。

**主要优势**：
- ✅ **松耦合**：模块间通过接口通信，不直接依赖具体实现
- ✅ **易维护**：每个模块独立，修改一个模块不影响其他模块
- ✅ **可扩展**：轻松添加新模块，不影响现有功能
- ✅ **可测试**：每个模块可以独立测试
- ✅ **可升级**：可以独立升级某个模块，无需重启整个系统

## 🏗️ 架构概览

```
┌────────────────────────────────────────────┐
│         FastAPI Application                │
│              main.py                       │
└────────────┬───────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────┐
│       ModuleRegistry (模块注册器)          │
│                                            │
│  • 注册模块                                │
│  • 拓扑排序                                │
│  • 依赖注入                                │
│  • 生命周期管理                            │
└────────────┬───────────────────────────────┘
             │
    ┌────────┼────────┬────────┬────────┐
    │        │        │        │        │
    ▼        ▼        ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ Order│ │ Menu │ │ User │ │Stock │ │Member│
│Module│ │Module│ │Module│ │Module│ │Module│
└───┬──┘ └───┬──┘ └───┬──┘ └───┬──┘ └───┬──┘
    │        │        │        │        │
    └────────┼────────┴────────┼────────┘
             │                 │
             ▼                 ▼
    ┌──────────────────────────────┐
    │   Service Interfaces         │
    │   (服务接口定义)             │
    └──────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │   Database                   │
    │   (通过接口访问)             │
    └──────────────────────────────┘
```

## 📁 项目结构

```
restaurant/
├── core/                          # 核心框架
│   ├── module_base.py            # 模块基类和注册器
│   └── service_interfaces.py     # 服务接口定义
├── modules/                       # 业务模块
│   └── legacy/                   # 遗留模块（现有代码封装）
│       ├── base_module.py        # 遗留模块适配器
│       ├── order_module.py       # 订单模块
│       ├── menu_module.py        # 菜单模块
│       ├── user_module.py        # 用户模块
│       ├── stock_module.py       # 库存模块
│       ├── member_module.py      # 会员模块
│       ├── payment_module.py     # 支付模块
│       ├── stats_module.py       # 统计模块
│       ├── receipt_module.py     # 小票模块
│       ├── websocket_module.py   # WebSocket 模块
│       ├── workflow_module.py    # 工作流模块
│       └── permission_module.py  # 权限模块
├── config/                        # 配置文件
│   └── modules.json              # 模块配置
├── src/                           # 源代码
│   ├── api/                      # API 路由
│   │   ├── order_flow_api.py
│   │   ├── restaurant_api.py
│   │   └── ...
│   ├── storage/                  # 数据库层
│   │   └── database/
│   ├── module_loader.py          # 模块加载器
│   └── main.py                   # 应用入口
├── test_module_loader.py          # 测试脚本
├── modular_app.py                 # 模块化应用入口
└── requirements.txt               # 依赖包
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置模块

编辑 `config/modules.json`：

```json
{
  "modules": [
    {
      "name": "LegacyOrderModule",
      "module": "modules.legacy.order_module",
      "enabled": true,
      "priority": 1
    }
  ],
  "legacy_mode": true,
  "fallback_to_traditional": true
}
```

### 3. 测试模块加载

```bash
# 运行测试脚本
python test_module_loader.py
```

预期输出：
```
============================================================
测试模块加载器
============================================================

[1] 加载模块配置...
✅ 配置加载成功，共 11 个模块

[2] 加载所有模块...
✅ 模块加载成功

[3] 初始化所有模块...
✅ 所有模块初始化成功

[4] 已加载模块列表:
  ✅ LegacyOrderModule v1.0.0
  ✅ LegacyMenuModule v1.0.0
  ...

[5] 执行健康检查...
整体状态: healthy

[6] 获取所有路由...
✅ 共 11 个路由

✅ 模块加载器测试通过！
```

### 4. 启动应用

```bash
# 使用传统方式启动（向后兼容）
python -m uvicorn src.main:app --reload

# 或使用模块化方式启动
python -m uvicorn modular_app:app --reload
```

访问：http://localhost:8000

## 🔧 模块配置

### 启用/禁用模块

编辑 `config/modules.json`：

```json
{
  "modules": [
    {
      "name": "LegacyOrderModule",
      "enabled": true   // 改为 false 禁用
    }
  ]
}
```

### 模块加载顺序

通过 `priority` 控制加载顺序（数值越小越先加载）：

```json
{
  "modules": [
    {
      "name": "LegacyMenuModule",
      "priority": 1    // 最先加载
    },
    {
      "name": "LegacyOrderModule",
      "priority": 2    // 其次加载（依赖 MenuModule）
    }
  ]
}
```

### 模块依赖

模块可以声明依赖关系：

```python
class OrderModule(BaseModule):
    def dependencies(self) -> List[str]:
        return ["MenuModule", "UserModule"]
```

系统会自动按依赖顺序初始化模块。

## 📖 创建新模块

### 步骤 1：创建模块类

```python
# modules/custom/custom_module.py
from core.module_base import BaseModule
from fastapi import APIRouter
from typing import List

class CustomModule(BaseModule):
    @property
    def name(self) -> str:
        return "CustomModule"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, dependencies):
        print("CustomModule initialized")
    
    def get_routes(self) -> List:
        router = APIRouter(prefix="/api/custom", tags=["Custom"])
        
        @router.get("/")
        def hello():
            return {"message": "Hello from CustomModule"}
        
        return [router]
```

### 步骤 2：注册模块

编辑 `config/modules.json`：

```json
{
  "modules": [
    {
      "name": "CustomModule",
      "module": "modules.custom.custom_module",
      "enabled": true,
      "priority": 10
    }
  ]
}
```

### 步骤 3：创建模块实例

```python
# modules/custom/custom_module.py
# ... (上面的代码)

# 创建模块实例
module_instance = CustomModule()
```

### 步骤 4：测试

```bash
python test_module_loader.py
```

访问：http://localhost:8000/api/custom/

## 🔍 模块健康检查

### 检查所有模块状态

```python
from src.module_loader import get_global_registry

registry = get_global_registry()
health = registry.health_check()
print(health)
```

### 检查单个模块状态

```python
from src.module_loader import get_global_registry

registry = get_global_registry()
module = registry.get_module("OrderModule")
print(module.health_check())
```

## 🎯 最佳实践

### 1. 使用接口通信

不要直接依赖其他模块的具体实现，而是使用接口：

```python
# ✅ 好的做法
from core.service_interfaces import IMenuService

def initialize(self, dependencies):
    self.menu_service = dependencies["MenuModule"].service
    item = self.menu_service.get_item(item_id)

# ❌ 不好的做法
from modules.menu.menu_service import MenuServiceImpl

def initialize(self, dependencies):
    self.menu_service = dependencies["MenuModule"].service  # 具体实现
```

### 2. 模块单一职责

每个模块只负责一个业务领域：

```
✅ OrderModule - 只负责订单
✅ MenuModule - 只负责菜单
❌ OrderMenuModule - 混合职责
```

### 3. 依赖最小化

尽量减少模块间的依赖：

```python
# ✅ 依赖少
def dependencies(self) -> List[str]:
    return ["MenuModule"]

# ❌ 依赖多
def dependencies(self) -> List[str]:
    return ["MenuModule", "UserModule", "StockModule", "PaymentModule"]
```

### 4. 错误处理

妥善处理模块初始化错误：

```python
def initialize(self, dependencies):
    try:
        self.service = SomeService()
    except Exception as e:
        logger.error(f"Failed to initialize {self.name}: {e}")
        raise
```

## 📚 相关文档

- **架构设计**: `ARCHITECTURE_COMPARISON.md`
- **合并计划**: `GITEE_MERGE_PLAN.md`
- **推送指南**: `PUSH_TO_GITEE_GUIDE.md`
- **完成报告**: `GITEE_COMPLETION_REPORT.md`

## 🆘 常见问题

### Q1: 如何禁用某个模块？

A: 编辑 `config/modules.json`，将该模块的 `enabled` 设为 `false`。

### Q2: 如何添加新模块？

A: 参考"创建新模块"章节，创建模块类并注册到配置文件。

### Q3: 模块加载失败怎么办？

A: 检查：
1. 模块路径是否正确
2. 模块是否实现了 `BaseModule` 接口
3. 依赖模块是否存在
4. 查看日志了解详细错误

### Q4: 如何调试模块？

A:
1. 运行 `test_module_loader.py` 查看加载状态
2. 检查模块日志
3. 使用健康检查接口

### Q5: 模块化架构会影响性能吗？

A: 影响很小。模块初始化只在启动时执行一次，运行时几乎无开销。

## 🎉 下一步

1. **阅读完整文档**: 了解更多架构细节
2. **尝试创建模块**: 练习创建自己的模块
3. **渐进式重构**: 将现有代码逐步重构为模块
4. **部署到生产**: 使用新的模块化架构部署系统

---

**祝您使用愉快！** 🚀
