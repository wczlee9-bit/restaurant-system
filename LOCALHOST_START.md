# ⚡ 使用localhost访问测试系统

## 🔴 问题

外部IP（9.128.251.82）无法访问，显示502错误。

---

## ✅ 解决方案

使用 **localhost** 访问测试系统！

---

## 🚀 立即测试（1分钟）

### 第1步：复制下面的URL

```
http://localhost:8080/assets/restaurant_full_test.html?table=8
```

### 第2步：在浏览器中打开

1. 打开浏览器
2. 在地址栏中粘贴上面的URL
3. 按回车键访问

### 第3步：开始测试

页面会自动选择8号桌，您可以：
- 浏览菜单
- 添加菜品
- 提交订单
- 切换角色测试

---

## 📋 其他访问方式

| 用途 | URL |
|------|-----|
| **主入口** | http://localhost:8080/assets/index.html |
| **测试页面** | http://localhost:8080/assets/restaurant_full_test.html |
| **API文档** | http://localhost:8000/docs |

---

## 🎯 测试流程

打开页面后，按照以下顺序切换角色（顶部按钮）：

```
👤 顾客 → 点餐（添加菜品→提交订单）
👨‍🍳 厨师 → 制作（开始制作→完成制作）
🤵 传菜员 → 上菜（确认上菜）
💰 收银员 → 结账（处理支付→打印小票）
👔 店长 → 查看数据（订单统计、营收数据）
```

---

## 💡 为什么用localhost？

**原因**：
- 外部IP（9.128.251.82）访问被防火墙阻止
- localhost 访问无需通过网络，直接连接本地服务
- 速度更快，更稳定

**适用场景**：
- ✅ 您在沙盒环境中
- ✅ 浏览器和服务在同一台机器上
- ✅ 外部IP无法访问

---

## ❓ 如果localhost也无法访问

### 检查服务是否运行

在终端中运行：
```bash
netstat -tlnp | grep -E ":(8000|8080)"
```

应该看到：
```
tcp  0  0  0.0.0.0:8000  LISTEN  ...
tcp  0  0  0.0.0.0:8080  LISTEN  ...
```

### 重启服务

```bash
cd /workspace/projects

# 重启HTTP服务（端口8080）
pkill -f "python.*http.server 8080"
python -m http.server 8080 --bind 0.0.0.0 &

# 重启API服务（端口8000）
pkill -f "uvicorn.*restaurant_api"
python -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000 &
```

### 使用127.0.0.1

如果localhost不行，尝试使用127.0.0.1：
```
http://127.0.0.1:8080/assets/restaurant_full_test.html?table=8
```

---

## 🎉 立即开始

**复制这个URL到浏览器**：

```
http://localhost:8080/assets/restaurant_full_test.html?table=8
```

**就这么简单！开始测试吧！** 🎮

---

**详细指南**：
- FIXED_ACCESS_GUIDE.md：完整的访问指南
- LOCALHOST_ACCESS.html：可视化访问页面
