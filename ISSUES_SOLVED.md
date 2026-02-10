# 问题解决记录 (Issues Solved)

> **作用**：记录开发过程中遇到的所有问题和解决方案
> **目的**：避免重复犯错，快速定位问题

---

## 📋 问题列表

### 1. ❌ 问题：API路由返回404

**现象**：
- 调用 `/api/orders/{order_id}/process-payment` 返回404

**原因**：
- 路由定义为 `@app.post("/api/orders/...")`
- 但Nginx已经加了 `/api` 前缀
- 导致实际路径是 `/api/api/orders/...`

**解决方案**：
```python
# 修改前
@app.post("/api/orders/{order_id}/process-payment")

# 修改后
@app.post("/orders/{order_id}/process-payment")
```

**日期**：2025-02-11
**状态**：✅ 已解决
**修改文件**：`src/api/restaurant_api.py`

---

### 2. ❌ 问题：API定义未生效

**现象**：
- 新添加的API调用404
- 代码看起来没问题

**原因**：
- API定义写在 `if __name__ == "__main__":` 之后
- 导致服务启动时未注册路由

**解决方案**：
```python
# 将API定义移到 if __name__ 之前
@app.get("/orders/{order_id}/receipt")
async def get_order_receipt(order_id: int):
    ...

if __name__ == "__main__":
    ...
```

**日期**：2025-02-11
**状态**：✅ 已解决
**修改文件**：`src/api/restaurant_api.py`

---

### 3. ❌ 问题：打印订单显示undefined

**现象**：
- 打印订单时，订单号、订单状态显示 `undefined`

**原因**：
- 字段名称错误
- `order.order_id` → 应该是 `order.order_number`
- `order.order_status` → 应该是 `order.status`

**解决方案**：
```javascript
// 修改前
document.getElementById('order-id').textContent = order.order_id;
document.getElementById('order-status').textContent = order.order_status;

// 修改后
document.getElementById('order-id').textContent = order.order_number;
document.getElementById('order-status').textContent = order.status;
```

**日期**：2025-02-11
**状态**：✅ 已解决
**修改文件**：`assets/staff_workflow.html`

---

### 4. ❌ 问题：传菜员打印订单包含已取消的菜品

**现象**：
- 菜品取消后，传菜员打印的订单仍然包含该菜品

**原因**：
- 没有过滤已取消的菜品

**解决方案**：
```javascript
// 在 printWaiterOrder 函数中添加过滤
if (item.item_status !== 'cancelled') {
    // 只打印未取消的菜品
}
```

**日期**：2025-02-11
**状态**：✅ 已解决
**修改文件**：`assets/staff_workflow.html`

---

### 5. ❌ 问题：访问页面自动跳转到login.html导致404

**现象**：
- 访问 `staff_workflow.html` 时自动跳转到 `login.html`
- 但 `login.html` 文件不存在

**原因**：
- 登录检查逻辑存在
- 但 `login.html` 文件不存在

**临时解决方案**：
- 禁用登录检查，设置默认测试用户

**待解决**：
- 实现完整的登录系统

**日期**：2025-02-11
**状态**：⏳ 临时解决
**修改文件**：`assets/staff_workflow.html`

---

### 6. ❌ 问题：前端文件路径混乱导致404

**现象**：
- 访问 `customer_order.html` 返回404

**原因**：
- 文件放在 `assets/` 目录
- 但Nginx配置指向 `frontend/` 目录

**解决方案**：
```bash
# 复制文件到frontend目录
cp assets/customer_order_v3.html frontend/customer_order.html
```

**目录规范**：
- ✅ **所有前端HTML文件必须放在 `frontend/` 目录**
- ❌ **禁止放在 `assets/` 目录**（assets只存放资源文件、测试文件、文档）

**日期**：2025-02-11
**状态**：✅ 已解决
**修改文件**：复制文件到正确目录

---

### 7. ❌ 问题：代码同步问题（沙盒 vs 服务器）

**现象**：
- 沙盒修改了代码
- 但服务器上还是旧版本
- 问题反复出现

**原因**：
- 沙盒修改后没有推送到GitHub
- 服务器没有拉取最新代码
- 或者文件放在了错误的目录

**解决方案**：
```bash
# 沙盒：推送到GitHub
git push origin main

# 服务器：拉取最新代码
git pull origin main

# 确认文件在正确目录
ls -la frontend/staff_workflow.html
```

**工作流程**：
```
沙盒修改 → GitHub推送 → 服务器拉取 → 验证
```

**日期**：2025-02-11
**状态**：✅ 已解决
**修改**：建立正确的代码同步流程

---

### 8. ❌ 问题：Nginx配置问题

**现象**：
- API请求返回404
- 模板变量未渲染
- 支付功能无法使用

**原因**：
- Nginx配置错误
- API路径配置不正确

**解决方案**：
```nginx
# 前端静态文件
location /restaurant/ {
    alias /var/www/restaurant-system/frontend/;
    index index.html;
}

# API代理
location /restaurant/api/ {
    proxy_pass http://localhost:8000/;
}

# WebSocket代理
location /restaurant/ws/ {
    proxy_pass http://localhost:8001/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

**日期**：2025-02-11
**状态**：✅ 已解决
**修改文件**：`/etc/nginx/sites-available/restaurant-system`

---

### 9. ❌ 问题：数据库使用错误

**现象**：
- 数据不一致
- 订单数据查询不到

**原因**：
- 代码连接了错误的数据库
- 使用了 `restaurant_db` 而不是 `restaurant_system`

**解决方案**：
```python
# 确保使用正确的数据库
DATABASE_URL = "postgresql://user:password@localhost/restaurant_system"
```

**数据库规范**：
- ✅ **只使用 `restaurant_system` 数据库**
- ❌ **不要使用 `restaurant_db` 或其他数据库**

**日期**：2025-02-11
**状态**：✅ 已解决
**修改**：统一使用 `restaurant_system` 数据库

---

### 10. ❌ 问题：后端服务未加载最新代码

**现象**：
- 修改代码后，问题仍然存在
- API还是返回错误

**原因**：
- 后端服务没有重启
- 代码修改未生效

**解决方案**：
```bash
# 重启后端服务
pkill -f "python.*restaurant_api"
nohup python3 -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &

# 验证服务运行
ps aux | grep restaurant_api
```

**日期**：2025-02-11
**状态**：✅ 已解决
**修改**：重启后端服务

---

### 11. ❌ 问题：沙盒代码未推送到GitHub

**现象**：
- 沙盒修改了代码
- 服务器拉取后还是旧版本
- 问题反复出现

**原因**：
- 沙盒修改后没有执行 `git push`

**解决方案**：
```bash
# 沙盒：检查是否有未推送的提交
git status

# 如果显示 "Your branch is ahead of 'origin/main'"，说明需要推送
git push origin main
```

**日期**：2025-02-11
**状态**：✅ 已解决
**修改**：每次修改后必须推送到GitHub

---

## 📊 问题统计

| 问题类型 | 数量 | 状态 |
|----------|------|------|
| API路由问题 | 2 | ✅ 已解决 |
| 前端字段错误 | 1 | ✅ 已解决 |
| 打印功能问题 | 1 | ✅ 已解决 |
| 登录问题 | 1 | ⏳ 临时解决 |
| 文件路径问题 | 1 | ✅ 已解决 |
| 代码同步问题 | 2 | ✅ 已解决 |
| Nginx配置问题 | 1 | ✅ 已解决 |
| 数据库问题 | 1 | ✅ 已解决 |
| 后端服务问题 | 1 | ✅ 已解决 |

**总计**：11个问题
**已解决**：10个
**临时解决**：1个

---

## 🎯 关键决策

### 目录规范
- ✅ 前端HTML文件必须放在 `frontend/` 目录
- ✅ assets目录只存放资源文件、测试文件、文档

### 数据库规范
- ✅ 只使用 `restaurant_system` 数据库

### API规范
- ✅ 不要在路由定义中加 `/api` 前缀（Nginx已经加了）
- ✅ 所有API定义必须在 `if __name__ == "__main__":` 之前

### 代码同步流程
- ✅ 沙盒修改 → GitHub推送 → 服务器拉取 → 验证

### Nginx配置
- ✅ 前端：`alias /var/www/restaurant-system/frontend/`
- ✅ API：`proxy_pass http://localhost:8000/`
- ✅ WebSocket：`proxy_pass http://localhost:8001/`

---

## 📝 更新日志

| 日期 | 更新内容 | 更新人 |
|------|----------|--------|
| 2025-02-11 | 创建问题解决记录，记录11个已解决的问题 | Coze Coding |

---

## 🚀 使用指南

### 当遇到问题时：
1. **先查看本文档**，查找是否有类似问题
2. **检查文件路径**是否正确（frontend vs assets）
3. **检查API路由**是否正确（不要重复 `/api`）
4. **检查代码是否同步**（GitHub → 服务器）

### 当开发新功能时：
1. **在沙盒修改代码**
2. **推送到GitHub**（`git push`）
3. **服务器拉取代码**（`git pull`）
4. **重启服务**（如果有API修改）
5. **验证功能**

### 每次解决问题后：
**记得更新本文档，记录新问题和解决方案！** 📝

---

**记住：本文档是项目的"问题解决手册"，每次遇到问题时都要查阅和更新！** 📚
