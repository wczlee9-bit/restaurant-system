# 🔧 模块升级指南

## 📋 概述

本指南介绍如何在不影响其他模块的情况下，独立升级特定模块。

---

## 🎯 升级原则

### 1. 向后兼容
- 公共接口（API）不能随意修改
- 如需修改，提供过渡期和兼容方案
- 使用语义化版本（SemVer）

### 2. 独立测试
- 升级前在测试环境验证
- 确保模块功能正常
- 确保与其他模块的集成正常

### 3. 灰度发布
- 先在小范围验证
- 逐步扩大使用范围
- 保留回滚方案

---

## 📦 模块升级步骤

### 步骤1：备份原模块

```bash
# 备份当前版本
cd /opt/restaurant-system/modules
cp -r order order.backup.v1.0.0

# 备份数据库（如果涉及数据库变更）
pg_dump restaurant_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 步骤2：准备新版本

```bash
# 解压新版本
unzip order_v2.0.0.zip -d /tmp/

# 查看版本信息
cat /tmp/order/module.py | grep version
# 应该输出: version = "2.0.0"

# 查看依赖变化
cat /tmp/order/module.py | grep dependencies
```

### 步骤3：验证依赖兼容性

```python
# 检查新模块是否与其他模块兼容
# 检查点：
# 1. 依赖的模块版本是否支持
# 2. 公共接口是否变更
# 3. 数据模型是否变更

# 例如：订单模块 v2.0.0 依赖菜单模块 v1.2.0+
# 当前菜单模块版本：v1.1.0
# 结论：需要先升级菜单模块
```

### 步骤4：替换模块

```bash
# 停止服务
systemctl stop restaurant-system

# 替换模块
rm -rf /opt/restaurant-system/modules/order
mv /tmp/order /opt/restaurant-system/modules/

# 更新权限
chown -R appuser:appuser /opt/restaurant-system/modules/order
chmod -R 755 /opt/restaurant-system/modules/order
```

### 步骤5：数据库迁移（如需要）

```bash
# 如果新版本涉及数据库变更
cd /opt/restaurant-system
python3 -m modules.order.migrations.v2_0_0

# 验证迁移
python3 -m modules.order.migrations.verify
```

### 步骤6：启动服务

```bash
# 启动服务
systemctl start restaurant-system

# 检查日志
tail -f /var/log/restaurant-system/app.log

# 检查模块状态
curl http://localhost:8001/api/health
```

### 步骤7：验证功能

```bash
# 1. 检查模块健康状态
curl http://localhost:8001/api/modules/order/health

# 2. 测试核心功能
# 测试创建订单
curl -X POST http://localhost:8001/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{"table_id":1,"store_id":1,"items":[{"item_id":1,"quantity":2}]}'

# 3. 检查依赖模块是否正常
curl http://localhost:8001/api/modules/menu/health
curl http://localhost:8001/api/modules/user/health
```

### 步骤8：监控观察

```bash
# 持续监控 30 分钟
watch -n 10 'curl -s http://localhost:8001/api/health | jq'

# 检查错误日志
tail -f /var/log/restaurant-system/error.log | grep ERROR
```

### 步骤9：完成或回滚

```bash
# 如果升级成功
systemctl enable restaurant-system

# 如果升级失败，回滚
systemctl stop restaurant-system
rm -rf /opt/restaurant-system/modules/order
mv /opt/restaurant-system/modules/order.backup.v1.0.0 \
   /opt/restaurant-system/modules/order
systemctl start restaurant-system
```

---

## 🔄 各模块升级示例

### 示例1：升级订单模块（v1.0.0 → v2.0.0）

**变更内容**：
- 新增订单取消功能
- 优化订单查询性能
- 新增订单状态：`cancelled`

**操作步骤**：

```bash
# 1. 备份
cp -r modules/order modules/order.backup.v1.0.0

# 2. 替换
rm -rf modules/order
cp -r /tmp/order_v2.0.0 modules/order

# 3. 数据库迁移（新增 cancelled 状态）
psql -U restaurant_user -d restaurant_db << SQL
ALTER TYPE order_status ADD VALUE 'cancelled' AFTER 'paid';
SQL

# 4. 重启服务
systemctl restart restaurant-system

# 5. 验证
curl -X PUT http://localhost:8001/api/orders/123/status?status=cancelled
```

**影响范围**：
- ✅ 只影响订单模块
- ✅ 其他模块无需修改
- ✅ 统计模块自动支持新状态

---

### 示例2：升级支付模块（v1.0.0 → v2.0.0）

**变更内容**：
- 新增银联支付支持
- 优化支付回调处理
- 新增支付超时机制

**操作步骤**：

```bash
# 1. 备份
cp -r modules/payment modules/payment.backup.v1.0.0

# 2. 替换
rm -rf modules/payment
cp -r /tmp/payment_v2.0.0 modules/payment

# 3. 数据库迁移（新增银联支付记录表）
python3 -m modules.payment.migrations.v2_0_0

# 4. 更新配置
vi /opt/restaurant-system/config/payment.yaml
# 添加银联支付配置

# 5. 重启服务
systemctl restart restaurant-system

# 6. 验证
curl -X POST http://localhost:8001/api/orders/123/pay \
  -H "Content-Type: application/json" \
  -d '{"payment_method":"union_pay"}'
```

**影响范围**：
- ✅ 只影响支付模块
- ✅ 订单模块通过接口调用，无需修改
- ✅ 统计模块自动支持新支付方式

---

### 示例3：升级库存模块（v1.0.0 → v2.0.0）

**变更内容**：
- 新增库存预警阈值动态配置
- 新增批量补货功能
- 优化库存查询性能

**操作步骤**：

```bash
# 1. 备份
cp -r modules/stock modules/stock.backup.v1.0.0

# 2. 替换
rm -rf modules/stock
cp -r /tmp/stock_v2.0.0 modules/stock

# 3. 数据库迁移（新增预警阈值配置表）
python3 -m modules.stock.migrations.v2_0_0

# 4. 重启服务
systemctl restart restaurant-system

# 5. 验证
curl -X POST http://localhost:8001/api/stock/restock \
  -H "Content-Type: application/json" \
  -d '{"items":[{"item_id":1,"quantity":10}]}'
```

**影响范围**：
- ✅ 只影响库存模块
- ✅ 订单模块通过接口调用，无需修改
- ✅ 管理后台自动支持新功能

---

## 🧪 升级前检查清单

### 功能检查
- [ ] 新功能需求文档已确认
- [ ] 接口变更文档已更新
- [ ] 数据库变更脚本已准备
- [ ] 回滚方案已准备

### 兼容性检查
- [ ] 依赖模块版本兼容
- [ ] 公共接口向后兼容
- [ ] 数据模型变更兼容
- [ ] 配置文件格式兼容

### 测试检查
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 性能测试通过
- [ ] 压力测试通过

### 部署检查
- [ ] 备份已完成
- [ ] 部署脚本已准备
- [ ] 监控告警已配置
- [ ] 回滚流程已验证

---

## 🚨 常见问题

### Q1: 升级后服务启动失败

**解决方案**：
```bash
# 1. 查看日志
tail -100 /var/log/restaurant-system/app.log

# 2. 检查依赖
python3 -c "from modules.order.module import OrderModule; print(OrderModule().dependencies())"

# 3. 回滚
systemctl stop restaurant-system
rm -rf modules/order
mv modules/order.backup.v1.0.0 modules/order
systemctl start restaurant-system
```

### Q2: 升级后接口返回 500 错误

**解决方案**：
```bash
# 1. 查看错误日志
grep ERROR /var/log/restaurant-system/app.log

# 2. 检查数据库连接
psql -U restaurant_user -d restaurant_db -c "SELECT 1"

# 3. 检查配置文件
cat /opt/restaurant-system/config/modules/order.yaml
```

### Q3: 升级后性能下降

**解决方案**：
```bash
# 1. 检查模块版本
curl http://localhost:8001/api/modules/order/health

# 2. 查看性能指标
curl http://localhost:8001/api/metrics

# 3. 分析慢查询
psql -U restaurant_user -d restaurant_db -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10"
```

---

## 📊 升级记录模板

```markdown
## 模块升级记录

### 基本信息
- 模块名称：OrderModule
- 原版本：1.0.0
- 新版本：2.0.0
- 升级时间：2025-02-06 14:00
- 升级人：张三

### 变更内容
- 新增订单取消功能
- 优化订单查询性能
- 新增订单状态：cancelled

### 影响范围
- ✅ 只影响订单模块
- ✅ 其他模块无需修改

### 测试结果
- ✅ 单元测试通过
- ✅ 集成测试通过
- ✅ 性能测试通过

### 部署步骤
1. 备份原模块
2. 替换新版本
3. 数据库迁移
4. 重启服务
5. 功能验证

### 验证结果
- ✅ 订单创建正常
- ✅ 订单取消正常
- ✅ 订单查询正常
- ✅ 统计功能正常

### 遗留问题
- 无

### 备注
- 升级过程顺利，无异常
```

---

**文档版本**：1.0.0  
**最后更新**：2025-02-06  
**维护者**：Coze Coding
