# 🚀 腾讯云系统模块化迁移与合并方案

## 📋 目标概述

1. ✅ 将腾讯云上已部署的系统升级为模块化架构
2. ✅ 与沙盒中开发的模块化架构合并
3. ✅ 使用 Gitee 作为代码托管平台
4. ✅ 部署到腾讯云服务器

---

## 🔄 迁移流程总览

```
步骤1：备份腾讯云现有系统
    ↓
步骤2：在本地创建模块化封装
    ↓
步骤3：合并沙盒的新模块化架构
    ↓
步骤4：推送到 Gitee
    ↓
步骤5：从 Gitee 部署到腾讯云
```

---

## 📝 详细步骤

### 步骤1：备份腾讯云现有系统

```bash
# SSH 连接到腾讯云服务器
ssh root@129.226.196.76

# 进入项目目录
cd /opt/restaurant-system

# 备份现有代码
tar -czf /tmp/restaurant-system-backup-$(date +%Y%m%d).tar.gz .

# 备份数据库
pg_dump restaurant_db > /tmp/restaurant-db-backup-$(date +%Y%m%d).sql

# 备份配置文件
cp config/agent_llm_config.json /tmp/config-backup.json

# 验证备份
ls -lh /tmp/restaurant-system-backup-*.tar.gz
ls -lh /tmp/restaurant-db-backup-*.sql

echo "备份完成！"
```

### 步骤2：创建 Gitee 仓库

#### 2.1 登录 Gitee
访问：https://gitee.com/

#### 2.2 创建新仓库
- 仓库名称：restaurant-system
- 仓库介绍：多店铺扫码点餐系统 - 模块化架构
- 可见性：私有（推荐）或公开
- 初始化仓库：勾选 README、.gitignore

#### 2.3 获取仓库地址
```
https://gitee.com/your-username/restaurant-system.git
```

### 步骤3：在本地创建模块化封装

#### 3.1 克隆沙盒代码到本地

```bash
# 在本地机器执行
cd ~/workspace
git clone https://gitee.com/your-username/restaurant-system.git
cd restaurant-system

# 如果从沙盒复制代码
# 使用 scp 或 rsync 将沙盒代码复制到本地
```

#### 3.2 创建模块化结构

```bash
# 创建模块目录结构
mkdir -p core modules/old_system

# 复制模块化框架
cp -r /workspace/projects/core/* core/
cp -r /workspace/projects/modules/* modules/

# 创建现有系统的模块封装
```

#### 3.3 创建现有系统的模块封装

创建 `modules/old_system/menu_module.py`：

```python
"""
现有系统菜单模块封装
将现有的 menu_routes.py 封装为模块
"""

from typing import List
from fastapi import APIRouter
import sys
import os

# 添加 backend_extensions 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend_extensions/src'))

from core.module_base import BaseModule
from routes.menu_routes import router as menu_router


class OldMenuModule(BaseModule):
    """
    现有系统的菜单模块封装
    """
    
    @property
    def name(self) -> str:
        return "OldMenuModule"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "现有系统的菜单模块（模块化封装）"
    
    def dependencies(self) -> List[str]:
        return []
    
    def initialize(self, dependencies):
        """初始化模块"""
        # 添加路由
        self.router = menu_router
        print(f"{self.name} initialized")
    
    def get_routes(self):
        """返回路由列表"""
        return [self.router]
```

创建 `modules/old_system/order_module.py`：

```python
"""
现有系统订单模块封装
将现有的 order_routes.py 封装为模块
"""

from typing import List
from fastapi import APIRouter
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend_extensions/src'))

from core.module_base import BaseModule
from routes.order_routes import router as order_router


class OldOrderModule(BaseModule):
    """
    现有系统的订单模块封装
    """
    
    @property
    def name(self) -> str:
        return "OldOrderModule"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def dependencies(self) -> List[str]:
        return ["OldMenuModule"]  # 依赖菜单模块
    
    def initialize(self, dependencies):
        """初始化模块"""
        self.router = order_router
        print(f"{self.name} initialized")
    
    def get_routes(self):
        """返回路由列表"""
        return [self.router]
```

类似地创建其他模块：
- `modules/old_system/auth_module.py`
- `modules/old_system/stock_module.py`
- `modules/old_system/member_module.py`
- `modules/old_system/stats_module.py`
- `modules/old_system/receipt_module.py`
- `modules/old_system/websocket_module.py`

#### 3.4 创建模块化主入口

创建 `modular_main.py`：

```python
"""
模块化主入口
整合现有系统和新的模块化架构
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend_extensions/src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from core.module_base import registry

# 导入现有系统模块
from modules.old_system.menu_module import OldMenuModule
from modules.old_system.order_module import OldOrderModule
from modules.old_system.auth_module import OldAuthModule
from modules.old_system.stock_module import OldStockModule
from modules.old_system.member_module import OldMemberModule
from modules.old_system.stats_module import OldStatsModule
from modules.old_system.receipt_module import OldReceiptModule
from modules.old_system.websocket_module import OldWebSocketModule

# 导入新的模块化模块（如果有的话）
# from modules.new.order_module import OrderModule
# from modules.new.menu_module import MenuModule

# 创建应用
app = FastAPI(
    title="餐厅管理系统",
    description="多店铺扫码点餐系统 - 模块化架构",
    version="2.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册现有系统模块
registry.register(OldMenuModule())
registry.register(OldUserModule())
registry.register(OldAuthModule())
registry.register(OldOrderModule())
registry.register(OldStockModule())
registry.register(OldMemberModule())
registry.register(OldStatsModule())
registry.register(OldReceiptModule())
registry.register(OldWebSocketModule())

# 注册新的模块化模块（逐步迁移）
# registry.register(NewMenuModule())
# registry.register(NewOrderModule())

# 初始化所有模块
print("正在初始化模块...")
registry.initialize_all()
print("模块初始化完成")

# 注册所有路由
print("正在注册路由...")
for router in registry.get_all_routes():
    app.include_router(router)
print("路由注册完成")

@app.get("/")
def root():
    return {
        "message": "餐厅管理系统",
        "version": "2.0.0",
        "architecture": "Modular (Migrated)"
    }

@app.get("/health")
def health():
    """健康检查"""
    return registry.health_check()

@app.get("/modules")
def list_modules():
    """列出所有模块"""
    modules = registry.get_all_modules()
    return {
        "count": len(modules),
        "modules": [
            {
                "name": name,
                "version": module.version,
                "description": module.description
            }
            for name, module in modules.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### 步骤4：测试模块化封装

```bash
# 在本地测试
cd ~/workspace/restaurant-system
export PYTHONPATH=$(pwd)/src:$(pwd)/backend_extensions/src:$PYTHONPATH
python3 modular_main.py

# 访问测试
curl http://localhost:8001/health
curl http://localhost:8001/modules
curl http://localhost:8001/api/menu/?store_id=1
```

### 步骤5：推送到 Gitee

```bash
# 配置 Git
cd ~/workspace/restaurant-system
git init
git remote add origin https://gitee.com/your-username/restaurant-system.git

# 添加所有文件
git add .

# 提交
git commit -m "feat: 模块化架构迁移 - 整合现有系统和新架构"

# 推送到 Gitee
git push -u origin main
```

### 步骤6：从 Gitee 部署到腾讯云

#### 6.1 在腾讯云服务器上拉取代码

```bash
# SSH 连接到腾讯云
ssh root@129.226.196.76

# 进入项目目录
cd /opt/restaurant-system

# 备份当前代码
cp -r . ../restaurant-system.backup.$(date +%Y%m%d)

# 拉取 Gitee 代码
git remote set-url origin https://gitee.com/your-username/restaurant-system.git
git pull origin main
```

#### 6.2 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
npm run build
cd ..

cd admin
npm install
npm run build
cd ..
```

#### 6.3 停止旧服务

```bash
# 停止现有服务
pkill -f "uvicorn"
systemctl stop restaurant-system

# 等待进程停止
sleep 5
```

#### 6.4 启动新服务

```bash
# 启动模块化服务
cd /opt/restaurant-system
export PYTHONPATH=/opt/restaurant-system/src:/opt/restaurant-system/backend_extensions/src:$PYTHONPATH
nohup python3 modular_main.py > /tmp/app.log 2>&1 &

# 或者使用 systemd
# systemctl start restaurant-system
```

#### 6.5 验证部署

```bash
# 检查服务状态
ps aux | grep uvicorn

# 查看日志
tail -20 /tmp/app.log

# 健康检查
curl http://localhost:8001/health

# 检查模块
curl http://localhost:8001/modules

# 检查 API
curl http://localhost:8001/api/menu/?store_id=1
```

---

## 🔄 逐步迁移策略

### 阶段1：模块化封装（当前阶段）

**目标**：将现有系统封装为模块，保持功能不变

```
现有系统
    ↓
封装为模块
    ↓
保持现有功能
```

**工作**：
- ✅ 创建模块化框架
- ✅ 封装现有功能为模块
- ✅ 测试验证
- ✅ 部署到腾讯云

### 阶段2：功能迁移（后续阶段）

**目标**：逐步将功能迁移到新的模块化实现

```
现有模块（封装）
    ↓
新模块（重新实现）
    ↓
逐步替换
```

**工作**：
1. 创建新的 MenuModule（重新实现）
2. 替换 OldMenuModule
3. 测试验证
4. 部署

### 阶段3：完全迁移（最终阶段）

**目标**：完全使用新的模块化架构

```
新模块（重新实现）
    ↓
移除旧模块
    ↓
完全模块化
```

**工作**：
1. 所有功能都使用新模块
2. 移除 Old* 模块
3. 测试验证
4. 部署

---

## 📋 Gitee 配置清单

### 1. 仓库设置

- 仓库名称：restaurant-system
- 仓库描述：多店铺扫码点餐系统 - 模块化架构
- 可见性：私有
- 语言：Python
- 许可证：MIT

### 2. 分支策略

- main：主分支（稳定版本）
- dev：开发分支（新功能开发）
- feature-*：功能分支（功能开发）
- hotfix-*：修复分支（紧急修复）

### 3. .gitignore 配置

已创建，包含：
- Python 缓存
- 数据库文件
- 日志文件
- 配置文件（敏感信息）

---

## 🔍 验证清单

### 迁移前

- [ ] 腾讯云系统已备份
- [ ] 数据库已备份
- [ ] Gitee 仓库已创建
- [ ] 本地开发环境已准备

### 迁移中

- [ ] 模块化封装完成
- [ ] 本地测试通过
- [ ] 代码已推送到 Gitee

### 迁移后

- [ ] 代码已拉取到腾讯云
- [ ] 依赖已安装
- [ ] 服务已启动
- [ ] 健康检查通过
- [ ] API 正常工作
- [ ] 前端正常访问
- [ ] 管理后台正常访问

---

## 🚨 回滚方案

如果迁移失败，快速回滚：

```bash
# SSH 连接到腾讯云
ssh root@129.226.196.76

# 停止服务
pkill -f "uvicorn"

# 恢复备份
cd /opt
rm -rf restaurant-system
mv restaurant-system.backup.20250206 restaurant-system

# 重启服务
cd /opt/restaurant-system
export PYTHONPATH=/opt/restaurant-system/src:$PYTHONPATH
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 > /tmp/app.log 2>&1 &

# 验证
curl http://localhost:8001/health
```

---

## 📊 迁移时间表

| 阶段 | 任务 | 时间 | 状态 |
|------|------|------|------|
| 阶段1 | 备份现有系统 | 30分钟 | ⏳ 待执行 |
| 阶段2 | 创建 Gitee 仓库 | 10分钟 | ⏳ 待执行 |
| 阶段3 | 模块化封装 | 2-3小时 | ⏳ 待执行 |
| 阶段4 | 本地测试 | 1小时 | ⏳ 待执行 |
| 阶段5 | 推送到 Gitee | 20分钟 | ⏳ 待执行 |
| 阶段6 | 部署到腾讯云 | 1小时 | ⏳ 待执行 |
| 阶段7 | 验证部署 | 30分钟 | ⏳ 待执行 |
| **总计** | | **5-6小时** | |

---

## 📞 支持

如有问题，请联系：
- 开发团队：Coze Coding
- 文档：查看项目文档目录

---

**文档版本**：1.0.0  
**创建时间**：2025-02-06  
**维护者**：Coze Coding
