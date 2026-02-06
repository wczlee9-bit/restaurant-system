# 腾讯云部署日志 - 多店铺扫码点餐系统

## 部署环境
- **服务器**: 腾讯云 Ubuntu 服务器
- **工作目录**: `/opt/restaurant-system`
- **Python 版本**: 3.10
- **数据库**: PostgreSQL 14

---

## 一、初始部署步骤

### 1.1 安装依赖
```bash
# 进入虚拟环境
cd /opt/restaurant-system
source venv/bin/activate

# 安装依赖
pip install -r requirements-minimal.txt
```

**问题1**: numpy 2.4.0 不兼容 Python 3.10
```bash
# 解决方案：修改 requirements-minimal.txt，限制 numpy 版本
# 添加: numpy<2.0.0
pip install --force-reinstall numpy
```

### 1.2 配置数据库
```bash
# 创建 .env 文件
cat > .env << 'EOF'
PGDATABASE_URL=postgresql://restaurant_user:restaurant123@localhost:5432/restaurant_system
EOF
```

**问题2**: 数据库密码认证失败
```sql
-- 解决方案：重置密码
ALTER USER restaurant_user WITH PASSWORD 'restaurant123';
```

### 1.3 初始化数据库
```bash
python -m src.storage.database.init_db
```

**问题3**: 初始化测试数据时报错 'status' is an invalid keyword argument for Tables
```bash
# 解决方案：编辑 src/storage/database/init_db.py
# 删除第 183 行的 status="available" 参数
```

**初始化结果**:
- ✅ 4 个菜单分类（热菜、凉菜、主食、饮品）
- ✅ 18 个菜品
- ✅ 10 个桌位

---

## 二、后端服务启动

### 2.1 启动命令
```bash
# 后台启动服务
nohup python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &

# 查看日志
tail -f server.log
```

### 2.2 启动日志关键信息
```
✓ Diagnostic routes included
✓ Simple init routes included
Restaurant API routes registered at /api
✓ Database tables created successfully
✓ Test data initialized successfully
✓ Database contains 18 menu items
Restaurant API started successfully!
```

---

## 三、API 功能测试

### 3.1 健康检查 ✅
```bash
curl http://localhost:8000/health
# 返回: {"status":"healthy","service":"restaurant-system"}
```

### 3.2 菜单管理 ✅
```bash
# 查询菜品列表
curl http://localhost:8000/api/menu-items/
# 返回: 18 个菜品（宫保鸡丁、鱼香肉丝、红烧肉等）

# 查询分类列表
curl http://localhost:8000/api/menu-categories/
# 返回: 4 个分类（热菜、凉菜、主食、饮品）
```

### 3.3 桌位管理 ✅
```bash
# 查询桌位列表
curl http://localhost:8000/api/tables/
# 返回: 10 个桌位（1-10号桌，座位数2-10人）
```

### 3.4 订单管理 ✅

#### 创建订单
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "table_id": 1,
    "items": [{"menu_item_id": 1, "quantity": 2}],
    "dining_type": "dine_in"
  }'
# 返回: 订单号 ORD202602070036301790，总价 ¥76.00
```

#### 订单状态流转
```bash
# 状态流转规则: pending → confirmed → preparing → ready → serving → completed

# 1. pending → confirmed
curl -X PATCH http://localhost:8000/api/orders/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'

# 2. confirmed → preparing
curl -X PATCH http://localhost:8000/api/orders/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "preparing"}'

# 3. preparing → ready
curl -X PATCH http://localhost:8000/api/orders/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "ready"}'

# 4. ready → serving
curl -X PATCH http://localhost:8000/api/orders/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "serving"}'

# 5. serving → completed
curl -X PATCH http://localhost:8000/api/orders/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

**测试结果**: ✅ 所有状态流转成功

---

## 四、会员 API 问题修复

### 4.1 问题描述
```bash
curl http://localhost:8000/api/members/
# 返回: {"detail":"Not Found"}
```

### 4.2 问题分析
- 原 `member_api.py` 使用 FastAPI 应用，路由前缀为 `/api/member`
- 使用 `app.mount("/api/member", ...)` 挂载会导致路径重复
- 日志中没有显示 "Member API routes registered"

### 4.3 解决方案

#### 步骤1: 创建 member_router.py
**文件**: `src/api/member_router.py`
- 使用 APIRouter 替代 FastAPI
- 设置正确的前缀: `prefix="/api/member"`
- 包含所有会员管理功能:
  - 注册会员
  - 查询会员信息
  - 积分兑换
  - 折扣计算
  - 订单查询

#### 步骤2: 修改 main.py
**文件**: `src/main.py`
```python
# 注册会员 API 路由
try:
    from api.member_router import router as member_router
    app.include_router(member_router)
    logger.info("Member API routes registered at /api/member")
except ImportError as e:
    logger.warning(f"Failed to import member_router: {e}")
```

### 4.4 待验证
需要重启服务后测试:
```bash
curl http://localhost:8000/api/member/levels
curl -X POST http://localhost:8000/api/member/register \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000", "name": "张三"}'
```

---

## 五、明天待完成任务

### 5.1 重启服务并测试会员 API
```bash
# 进入项目目录
cd /opt/restaurant-system

# 拉取最新代码
git pull

# 杀掉 uvicorn 进程
killall uvicorn

# 重新启动服务
nohup python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &

# 查看启动日志
tail -f server.log

# 确认看到: Member API routes registered at /api/member

# 测试会员 API
curl http://localhost:8000/api/member/levels
```

### 5.2 继续测试其他功能
- 支付功能测试
- 营收统计测试

### 5.3 配置公网访问
- 配置腾讯云防火墙/安全组
- 开放 8000 端口
- 测试外网访问

### 5.4 前端测试
- 配置前端连接后端 API
- 测试扫码点餐流程

---

## 六、常用命令

### 查看服务状态
```bash
# 查看进程
ps aux | grep uvicorn

# 查看日志
tail -f server.log

# 健康检查
curl http://localhost:8000/health
```

### 重启服务
```bash
# 杀掉进程
killall uvicorn

# 启动服务
nohup python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &
```

### 数据库操作
```bash
# 连接数据库
psql -U restaurant_user -d restaurant_system

# 查看表
\dt

# 退出
\q
```

---

## 七、文件修改记录

### 修改的文件
1. `requirements-minimal.txt` - 添加 `numpy<2.0.0`
2. `.env` - 新增，配置数据库连接
3. `src/storage/database/init_db.py` - 删除第 183 行 `status="available"`
4. `src/main.py` - 注册会员 API 路由

### 新增的文件
1. `src/api/member_router.py` - 会员 API Router

---

## 八、测试进度总结

| 序号 | 业务功能 | 状态 | 测试时间 |
|------|---------|------|---------|
| 1 | 健康检查 | ✅ 通过 | 2026-02-07 00:45 |
| 2 | 菜单管理（18个菜品） | ✅ 通过 | 2026-02-07 00:45 |
| 3 | 菜单分类（4个分类） | ✅ 通过 | 2026-02-07 00:45 |
| 4 | 桌位管理（10个桌位） | ✅ 通过 | 2026-02-07 00:45 |
| 5 | 订单创建 | ✅ 通过 | 2026-02-07 00:36 |
| 6 | 订单查询 | ✅ 通过 | 2026-02-07 00:36 |
| 7 | 订单状态流转 | ✅ 通过 | 2026-02-07 00:37 |
| 8 | 会员管理 | ⏳ 待重启服务测试 | - |

---

## 九、重要信息

### 数据库连接
- **主机**: localhost
- **端口**: 5432
- **数据库**: restaurant_system
- **用户**: restaurant_user
- **密码**: restaurant123

### 服务信息
- **后端地址**: http://0.0.0.0:8000
- **本地测试**: http://localhost:8000
- **健康检查**: http://localhost:8000/health

### 测试数据
- **菜品数量**: 18 个
- **分类数量**: 4 个
- **桌位数量**: 10 个（2-10人座）
- **公司**: 测试餐饮公司 (id=15)
- **店铺**: 美味餐厅 (id=15)

---

**部署日期**: 2026-02-07
**最后更新**: 2026-02-07 00:50
