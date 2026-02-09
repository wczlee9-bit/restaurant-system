# 下次工作计划 - 支付和小票功能

## 📅 计划日期：待定

---

## 🎯 工作目标

完成柜台支付和打印小票功能的部署和测试，实现完整的订单处理流程。

---

## 📋 待办事项清单

### 阶段1：环境准备（5分钟）
- [ ] 确认腾讯云服务器状态
- [ ] 检查当前代码版本
- [ ] 确认数据库连接正常

### 阶段2：代码同步（15分钟）
- [ ] 从 GitHub 拉取最新代码到沙盒
- [ ] 提取 `process-payment` API 代码
- [ ] 提取 `receipt` API 代码
- [ ] 复制到腾讯云服务器

### 阶段3：部署代码（10分钟）
- [ ] 将 `process-payment` API 添加到腾讯云的 `restaurant_api.py`
- [ ] 将 `receipt` API 添加到腾讯云的 `restaurant_api.py`
- [ ] 验证代码语法正确性
- [ ] 重启后端服务

### 阶段4：功能测试（30分钟）
- [ ] 测试1：柜台支付 API 响应
  ```bash
  curl -X POST http://115.191.1.219:8000/api/orders/{order_id}/process-payment
  ```
- [ ] 测试2：打印小票 API 响应
  ```bash
  curl http://115.191.1.219:8000/api/orders/{order_id}/receipt
  ```
- [ ] 测试3：收银员界面支付按钮
- [ ] 测试4：小票打印窗口
- [ ] 测试5：浏览器打印功能

### 阶段5：端到端流程测试（20分钟）
- [ ] 完整测试订单处理流程：
  1. 顾客扫码点餐
  2. 订单确认
  3. 开始制作
  4. 完成制作
  5. 传菜
  6. 上菜
  7. 柜台支付
  8. 打印小票
- [ ] 验证所有状态转换正确
- [ ] 验证数据一致性

### 阶段6：问题修复（10分钟）
- [ ] 记录发现的问题
- [ ] 修复发现的 bug
- [ ] 重新测试验证

### 阶段7：文档更新（5分钟）
- [ ] 更新测试报告
- [ ] 记录测试结果
- [ ] 推送到 Gitee

---

## 📂 需要参考的文件

### 代码位置
- 沙盒环境：`/workspace/projects/src/api/restaurant_api.py`
- 腾讯云：`/var/www/restaurant-system/src/api/restaurant_api.py`

### API 端点
1. **柜台支付 API**
   - 路径：`/api/orders/{order_id}/process-payment`
   - 方法：POST
   - 位置：restaurant_api.py 第 2107 行左右

2. **打印小票 API**
   - 路径：`/api/orders/{order_id}/receipt`
   - 方法：GET
   - 位置：restaurant_api.py 第 2145 行左右

### 前端代码
- 文件：`/var/www/restaurant-system/frontend/staff_workflow.html`
- 函数：`processPayment()` 和 `printReceipt()`

---

## 🔧 需要使用的命令

### 部署命令
```bash
# 进入项目目录
cd /var/www/restaurant-system

# 备份当前文件
cp src/api/restaurant_api.py src/api/restaurant_api.py.backup

# 重启后端服务
systemctl restart restaurant-api
# 或
pkill -f "python.*restaurant_api" && nohup python -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
```

### 测试命令
```bash
# 测试柜台支付
curl -X POST http://115.191.1.219:8000/api/orders/1/process-payment

# 测试小票打印
curl http://115.191.1.219:8000/api/orders/1/receipt

# 查看日志
tail -f /app/work/logs/bypass/app.log
```

---

## ⚠️ 注意事项

1. **数据备份**
   - 修改前先备份 `restaurant_api.py` 文件
   - 避免直接修改生产环境，先在测试环境验证

2. **服务重启**
   - 修改代码后必须重启服务
   - 确保服务启动成功后再测试

3. **测试数据**
   - 准备测试订单数据
   - 确保订单存在且处于正确状态

4. **浏览器缓存**
   - 测试时清除浏览器缓存
   - 使用 Ctrl+F5 强制刷新

5. **错误处理**
   - 如果 API 报错，查看日志定位问题
   - 常见错误：数据库连接、字段缺失、状态转换

---

## 📊 预期结果

### 成功标准
1. ✅ `process-payment` API 返回成功
2. ✅ 订单状态正确更新为 `completed`
3. ✅ 支付状态正确更新为 `paid`
4. ✅ `receipt` API 返回完整小票数据
5. ✅ 小票打印窗口正常显示
6. ✅ 浏览器打印功能正常工作
7. ✅ 端到端流程测试通过

### 验证方法
- API 返回正确的 JSON 数据
- 数据库中订单状态正确
- 前端界面显示正确
- 打印的小票格式正确

---

## 📞 联系信息

如有问题，请检查：
1. 日志文件：`/app/work/logs/bypass/app.log`
2. API 响应：使用 curl 测试
3. 浏览器控制台：查看前端错误
4. 数据库：验证数据状态

---

## 💡 备忘录

**上次完成的工作**：
- ✅ 修复工作人员端 API 路径
- ✅ 修复订单数据模型
- ✅ 修复收银员过滤逻辑
- ✅ 开发柜台支付 API（未部署）
- ✅ 开发打印小票 API（未部署）

**待完成**：
- ⏳ 部署柜台支付功能
- ⏳ 部署打印小票功能
- ⏳ 测试支付流程
- ⏳ 测试打印功能
- ⏳ 端到端流程测试

---

**计划制定时间**：2025年2月9日
**预计完成时间**：约1.5小时
