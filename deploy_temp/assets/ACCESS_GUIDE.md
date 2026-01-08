# 🍽️ 餐饮点餐系统 - 访问指南

## 问题：无法访问 localhost？

如果您遇到 "localhost 拒绝连接" 的错误，请尝试以下解决方案：

---

## ✅ 推荐的访问方式

### 方式1：通过IP地址访问（推荐）

测试页面已升级为**自动检测API地址**，您可以通过以下任一IP地址访问：

```bash
# 主网络接口（外网可访问）
http://9.128.251.82:8080/assets/restaurant_full_test.html

# 备用网络接口
http://169.254.100.163:8080/assets/restaurant_full_test.html
```

**优势**：
- ✅ 不受localhost限制
- ✅ 自动适配API地址
- ✅ 适合远程访问测试

### 方式2：直接打开文件（本机使用）

如果测试页面在您的本地机器上：

1. 找到文件：`/workspace/projects/assets/restaurant_full_test.html`
2. 直接双击打开
3. 或在浏览器中输入文件路径

**注意**：此方式可能受浏览器安全策略限制，建议使用方式1或3。

### 方式3：使用本地服务器（本机使用）

```bash
# 启动本地HTTP服务器
cd /workspace/projects
python -m http.server 8080

# 在浏览器中访问
http://localhost:8080/assets/restaurant_full_test.html
```

---

## 🔍 服务诊断

### 检查服务状态

```bash
bash /workspace/projects/scripts/check_services.sh
```

### 查看日志

```bash
# 查看API服务日志（如果使用日志文件）
tail -f /path/to/api.log

# 或查看进程
ps aux | grep uvicorn
```

---

## 🎯 快速验证

### 1. 测试API服务

```bash
curl http://localhost:8000/health
# 或
curl http://9.128.251.82:8000/health
```

期望输出：API服务正常

### 2. 测试静态文件服务

```bash
curl http://localhost:8080/assets/restaurant_full_test.html
# 或
curl http://9.128.251.82:8080/assets/restaurant_full_test.html
```

期望输出：HTML代码（61433字节）

### 3. 查看API文档

在浏览器中打开：
- http://localhost:8000/docs
- http://9.128.251.82:8000/docs

---

## 🚨 常见问题

### Q1: "ERR_CONNECTION_REFUSED"

**原因**：
- 服务未启动
- 端口被防火墙阻止
- 使用了错误的地址

**解决方案**：
```bash
# 1. 检查服务是否运行
bash /workspace/projects/scripts/check_services.sh

# 2. 如果服务未运行，重新启动
cd /workspace/projects
python -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000 &
python -m http.server 8080 --bind 0.0.0.0 &

# 3. 尝试使用IP地址而非localhost
http://9.128.251.82:8080/assets/restaurant_full_test.html
```

### Q2: 页面加载但数据为空

**原因**：
- API地址配置错误
- 跨域问题

**解决方案**：
1. 打开浏览器开发者工具（F12）
2. 切换到Console标签
3. 查看是否有错误信息
4. 检查Network标签中的API请求是否失败

### Q3: 无法在不同设备间访问

**解决方案**：
1. 确认两个设备在同一网络
2. 使用同一IP地址访问
3. 检查防火墙设置
4. 确保服务监听在0.0.0.0（已配置）

---

## 📊 当前服务状态

| 服务 | 端口 | 状态 | 访问地址 |
|------|------|------|----------|
| API服务 | 8000 | ✅ 运行中 | http://9.128.251.82:8000 |
| 测试页面 | 8080 | ✅ 运行中 | http://9.128.251.82:8080/assets/restaurant_full_test.html |
| 主服务 | 5000 | ✅ 运行中 | http://9.128.251.82:5000 |

---

## 🎉 开始测试

### 推荐测试流程

1. **打开测试页面**
   ```
   http://9.128.251.82:8080/assets/restaurant_full_test.html
   ```

2. **切换到顾客角色**（顶部👤顾客按钮）

3. **选择桌号**（推荐8号桌）

4. **开始点餐**（浏览菜单 → 添加菜品 → 提交订单）

5. **切换到厨师**（👨‍🍳厨师按钮）→ 开始制作

6. **切换到传菜员**（🤵传菜员按钮）→ 确认上菜

7. **切换到收银员**（💰收银员按钮）→ 处理支付

8. **切换到店长**（👔店长按钮）→ 查看数据

---

## 📞 技术支持

如果问题仍未解决，请提供以下信息：

1. 使用的访问地址
2. 浏览器类型和版本
3. 浏览器控制台错误信息（F12 → Console）
4. Network标签中的API请求详情

---

**最后更新时间**：2025-01-08
**系统版本**：v2.0
**测试数据状态**：✅ 已初始化
