# 🍽️ 餐饮点餐系统 - 测试入口

## 🚀 新功能：部署到 Netlify（推荐！）

### 为什么选择 Netlify？

✅ **公开访问**：任何人都可以访问您的网站  
✅ **HTTPS加密**：自动配置SSL证书  
✅ **CDN加速**：全球快速访问  
✅ **手机访问**：支持移动设备  
✅ **易于分享**：可以分享给他人测试  

### 快速部署（3分钟）

**方法一：手动上传**
```bash
bash scripts/deploy_netlify.sh
```
然后访问 https://app.netlify.com，上传生成的 `restaurant-system.zip` 文件

**详细指南**：请查看 [NETLIFY_QUICKSTART.md](NETLIFY_QUICKSTART.md)

---

## ⚠️ 重要提示

**外部IP无法访问（502错误），请使用localhost访问！**

---

## ⚡ 立即开始测试（本地）

**复制这个URL到浏览器打开**：

```
http://localhost:8080/assets/restaurant_full_test.html?table=8
```

**就这么简单！开始测试吧！** 🎮

---

## 📋 核心文件

| 文件 | 用途 |
|------|------|
| **LOCALHOST_START.md** | ⭐ 使用localhost开始测试 |
| **LOCALHOST_ACCESS.html** | 可视化访问页面 |
| **FIXED_ACCESS_GUIDE.md** | 完整的访问指南 |
| **START_TESTING.md** | 最简单的开始指南 |

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

## 📱 其他访问方式（localhost）

| 用途 | URL |
|------|-----|
| **主入口** | http://localhost:8080/assets/index.html |
| **测试页面** | http://localhost:8080/assets/restaurant_full_test.html |
| **API文档** | http://localhost:8000/docs |

---

## 💡 为什么用localhost？

**原因**：
- 外部IP（9.128.251.82）访问被防火墙阻止（502错误）
- localhost 访问无需通过网络，直接连接本地服务
- 速度更快，更稳定

**适用场景**：
- ✅ 您在沙盒环境中
- ✅ 浏览器和服务在同一台机器上
- ✅ 外部IP无法访问

---

## ❓ 如果localhost也无法访问

### 检查服务

```bash
netstat -tlnp | grep -E ":(8000|8080)"
```

### 重启服务

```bash
cd /workspace/projects
python -m http.server 8080 --bind 0.0.0.0 &
python -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000 &
```

### 使用127.0.0.1

如果localhost不行，尝试：
```
http://127.0.0.1:8080/assets/restaurant_full_test.html?table=8
```

---

## 🎉 立即开始

**复制这个URL到浏览器**：

```
http://localhost:8080/assets/restaurant_full_test.html?table=8
```

---

# 项目结构说明（开发者参考）

# 本地运行
## 运行流程
bash scripts/local_run.sh -m flow

## 运行节点
bash scripts/local_run.sh -m node -n node_name

# 启动HTTP服务
bash scripts/http_run.sh -m http -p 5000

