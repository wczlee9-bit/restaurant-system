# 🔧 餐饮点餐系统 - 问题排查指南

## 🚨 当前问题

1. ❌ 页面一直显示加载中，没有内容
2. ❌ 扫码之后不显示菜品网页

---

## 🔍 问题1：页面一直显示加载中

### 原因分析

**根本原因**：后端API服务没有运行

前端页面依赖后端API提供数据：
- 菜单数据
- 订单数据
- 用户认证
- WebSocket实时推送

如果后端服务未启动，前端无法获取数据，会一直显示加载中。

---

## ✅ 解决方案：启动后端API服务

### 方法1：在服务器上启动所有API服务

SSH登录到服务器 `115.191.1.219`，执行以下命令：

```bash
# 进入项目目录
cd /path/to/restaurant-system

# 查看启动脚本
ls -la scripts/start_api_services.sh

# 启动所有API服务
./scripts/start_api_services.sh

# 或者手动启动每个服务
# 1. 餐饮系统主API (端口8000)
python src/api/restaurant_api.py &

# 2. 订单和WebSocket API (端口8001)
python src/api/customer_api.py &

# 3. 会员API (端口8004)
python src/api/member_api.py &

# 4. 总公司API (端口8006)
python src/api/headquarters_api.py &

# 5. 增强API (端口8007)
python src/api/restaurant_enhanced_api.py &
```

### 方法2：检查服务是否已启动

```bash
# 检查端口是否在监听
netstat -tlnp | grep -E "8000|8001|8004|8006|8007"

# 检查Python进程
ps aux | grep python

# 测试API连接
curl http://localhost:8000/api/health
curl http://localhost:8001/api/health
curl http://localhost:8004/api/health
curl http://localhost:8006/api/health
curl http://localhost:8007/api/health
```

### 方法3：使用systemd管理服务（推荐）

创建systemd服务，实现开机自启和自动重启：

```bash
# 创建服务文件
sudo nano /etc/systemd/system/restaurant-api.service
```

内容：
```ini
[Unit]
Description=Restaurant System API Services
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/restaurant-system
ExecStart=/usr/bin/python3 src/api/start_all_apis.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start restaurant-api

# 设置开机自启
sudo systemctl enable restaurant-api

# 查看服务状态
sudo systemctl status restaurant-api

# 查看日志
sudo journalctl -u restaurant-api -f
```

---

## 🔍 问题2：扫码后不显示菜品网页

### 原因分析

可能的原因：
1. 二维码生成的URL错误
2. 二维码指向的页面不存在
3. 页面加载失败（API未启动）

---

## ✅ 解决方案

### 检查二维码生成配置

在店铺设置页面（`shop_settings.html`），检查：

1. **二维码目标页面**：应该指向 `customer_order_v3.html`
2. **URL参数**：应该包含桌号，如 `?table=1`

### 正确的二维码URL格式

```
https://mellow-rabanadas-877f3e.netlify.app/customer_order_v3.html?table=1
```

或使用服务器部署：
```
http://115.191.1.219/customer_order_v3.html?table=1
```

### 重新生成二维码

1. 登录店铺设置页面
2. 选择桌号（1-10号）
3. 点击"生成二维码"
4. 扫码测试是否能跳转到点餐页面

---

## 👤 工作人员登录账号信息

### 顾客（Customer）
- **用户名**：`customer`
- **密码**：`customer123`
- **角色**：顾客

### 厨师（Chef）
- **用户名**：`chef`
- **密码**：`chef123`
- **角色**：厨师

### 传菜员（Waiter）
- **用户名**：`waiter`
- **密码**：`waiter123`
- **角色**：传菜员

### 收银员（Cashier）
- **用户名**：`cashier`
- **密码**：`cashier123`
- **角色**：收银员

### 店长（Manager）
- **用户名**：`manager`
- **密码**：`manager123`
- **角色**：店长

### 系统管理员（Admin）
- **用户名**：`admin`
- **密码**：`admin123`
- **角色**：系统管理员

### 总公司（Headquarters）
- **用户名**：`hq`
- **密码**：`hq123`
- **角色**：总公司

---

## 🌐 页面访问地址

### Netlify部署
```
门户：https://mellow-rabanadas-877f3e.netlify.app/portal.html
顾客：https://mellow-rabanadas-877f3e.netlify.app/customer_order_v3.html
登录：https://mellow-rabanadas-877f3e.netlify.app/login_standalone.html
会员：https://mellow-rabanadas-877f3e.netlify.app/member_center.html
总部：https://mellow-rabanadas-877f3e.netlify.app/headquarters_dashboard.html
```

### 服务器部署（本地）
```
门户：http://115.191.1.219/portal.html
顾客：http://115.191.1.219/customer_order_v3.html
登录：http://115.191.1.219/login_standalone.html
会员：http://115.191.1.219/member_center.html
总部：http://115.191.1.219/headquarters_dashboard.html
```

---

## 📋 完整的启动步骤

### 第1步：启动后端API服务

```bash
# SSH登录到服务器
ssh root@115.191.1.219

# 进入项目目录
cd /path/to/restaurant-system

# 启动所有API服务
./scripts/start_api_services.sh

# 查看服务状态
netstat -tlnp | grep -E "8000|8001|8004|8006|8007"
```

### 第2步：验证API服务

```bash
# 测试API连接
curl http://localhost:8000/api/health
curl http://localhost:8001/api/health
curl http://localhost:8004/api/health
curl http://localhost:8006/api/health
curl http://localhost:8007/api/health
```

应该返回 `{"status": "ok"}`

### 第3步：访问前端页面

打开浏览器，访问：
```
https://mellow-rabanadas-877f3e.netlify.app/portal.html
```

### 第4步：测试功能

1. **顾客点餐测试**：
   - 点击"顾客端"→选择桌号
   - 浏览菜单
   - 添加商品到购物车
   - 提交订单

2. **工作人员登录测试**：
   - 点击"工作人员登录"
   - 使用账号：`chef` / `chef123`
   - 查看订单列表
   - 更新订单状态

3. **扫码测试**：
   - 进入店铺设置
   - 生成桌号二维码
   - 扫码测试跳转

---

## 🔧 如果API无法启动

### 检查1：Python环境

```bash
# 检查Python版本
python3 --version

# 检查依赖
pip3 list | grep -E "fastapi|uvicorn"
```

如果依赖缺失，安装：
```bash
pip3 install fastapi uvicorn python-multipart pillow
```

### 检查2：端口占用

```bash
# 检查端口是否被占用
netstat -tlnp | grep -E "8000|8001|8004|8006|8007"

# 如果被占用，停止占用的进程
sudo kill -9 <PID>
```

### 检查3：数据库连接

```bash
# 测试数据库连接
psql -h localhost -U postgres -d restaurant_db -c "SELECT 1;"
```

### 检查4：日志查看

```bash
# 查看API日志
tail -f logs/api.log

# 或直接运行查看错误
python3 src/api/restaurant_api.py
```

---

## 🎯 临时解决方案：使用静态演示页面

如果后端API暂时无法启动，可以创建一个静态演示版本：

1. 在 `customer_order_v3.html` 中添加静态菜单数据
2. 不依赖API加载数据
3. 仅用于演示UI和交互流程

---

## 📞 获取帮助

如果问题仍未解决：

1. **查看浏览器控制台**：
   - 按F12打开开发者工具
   - 查看Console标签的错误信息
   - 查看Network标签的API请求状态

2. **查看服务器日志**：
   ```bash
   tail -f logs/api.log
   journalctl -u restaurant-api -f
   ```

3. **检查防火墙**：
   ```bash
   sudo ufw status
   sudo ufw allow 8000/tcp
   sudo ufw allow 8001/tcp
   sudo ufw allow 8004/tcp
   sudo ufw allow 8006/tcp
   sudo ufw allow 8007/tcp
   ```

---

## ✅ 问题解决清单

- [ ] 后端API服务已启动
- [ ] 所有端口（8000, 8001, 8004, 8006, 8007）正常监听
- [ ] API健康检查返回200状态码
- [ ] 门户页面可以正常加载
- [ ] 顾客点餐页面可以加载菜单
- [ ] 工作人员可以成功登录
- [ ] 二维码扫码可以跳转到点餐页面
- [ ] 订单可以正常提交
- [ ] WebSocket实时推送正常

---

**最重要**：**必须先启动后端API服务，前端页面才能正常工作！**

---

**更新时间**：2026-01-10
