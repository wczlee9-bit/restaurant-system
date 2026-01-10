# 🚀 服务器前端部署指南

由于网络限制无法访问GitHub和Netlify，我们采用**服务器本地部署方案**，直接在你的后端服务器上托管前端文件。

## 📋 部署概述

- **目标服务器**：115.191.1.219
- **Web服务器**：Nginx
- **前端目录**：`/var/www/restaurant-frontend`
- **访问端口**：80 (HTTP)
- **部署时间**：约5-10分钟

---

## 🎯 方案选择

我们提供两种部署方式：

### 方式1：自动部署脚本（推荐）⭐
使用自动化脚本一键部署，简单快速。

### 方式2：手动部署
手动执行每一步，适合需要自定义配置的场景。

---

## 🚀 方式1：自动部署脚本（推荐）

### 前提条件

- ✅ 可以SSH连接到服务器 `115.191.1.219`
- ✅ 有root权限或sudo权限
- ✅ 确保服务器上已安装Python环境

### 部署步骤

#### 步骤1：准备部署文件

在本地项目目录执行：

```bash
# 确保你在项目根目录
cd /workspace/projects

# 赋予脚本执行权限
chmod +x scripts/deploy_frontend_to_server.sh
```

#### 步骤2：执行部署脚本

```bash
# 执行部署脚本
./scripts/deploy_frontend_to_server.sh
```

脚本会自动完成以下操作：
1. 压缩assets目录
2. 上传到服务器
3. 安装Nginx（如果未安装）
4. 部署前端文件
5. 配置Nginx
6. 重启服务

#### 步骤3：验证部署

部署完成后，访问以下URL验证：

```bash
# 在本地执行
curl http://115.191.1.219/portal.html
```

或在浏览器中打开：
```
http://115.191.1.219/portal.html
```

---

## 🔧 方式2：手动部署

如果脚本执行失败，可以按照以下步骤手动部署：

### 步骤1：SSH连接到服务器

```bash
ssh root@115.191.1.219
```

### 步骤2：安装Nginx

```bash
# 更新包列表
apt-get update

# 安装Nginx
apt-get install -y nginx

# 检查Nginx状态
systemctl status nginx

# 启动Nginx（如果未启动）
systemctl start nginx

# 设置开机自启
systemctl enable nginx
```

### 步骤3：创建前端目录

```bash
# 创建前端文件目录
mkdir -p /var/www/restaurant-frontend
mkdir -p /var/www/restaurant-frontend/qrcodes

# 创建日志目录（Nginx会自动创建）
mkdir -p /var/log/nginx
```

### 步骤4：上传前端文件

**在本地项目目录执行**：

```bash
# 压缩assets目录
tar -czf /tmp/restaurant-frontend.tar.gz -C assets .

# 上传到服务器
scp /tmp/restaurant-frontend.tar.gz root@115.191.1.219:/tmp/
```

**在服务器上执行**：

```bash
# 解压文件到目标目录
tar -xzf /tmp/restaurant-frontend.tar.gz -C /var/www/restaurant-frontend/

# 设置权限
chown -R www-data:www-data /var/www/restaurant-frontend
chmod -R 755 /var/www/restaurant-frontend
```

### 步骤5：配置Nginx

**在本地项目目录执行**，上传配置文件：

```bash
# 上传Nginx配置文件
scp config/nginx-restaurant.conf root@115.191.1.219:/tmp/
```

**在服务器上执行**：

```bash
# 备份现有配置（如果存在）
if [ -f /etc/nginx/sites-available/restaurant-frontend ]; then
    cp /etc/nginx/sites-available/restaurant-frontend \
       /etc/nginx/sites-available/restaurant-frontend.backup.$(date +%Y%m%d_%H%M%S)
fi

# 移动配置文件
mv /tmp/nginx-restaurant.conf /etc/nginx/sites-available/restaurant-frontend

# 创建软链接
ln -sf /etc/nginx/sites-available/restaurant-frontend \
        /etc/nginx/sites-enabled/restaurant-frontend

# 移除默认配置（可选）
rm -f /etc/nginx/sites-enabled/default

# 测试配置
nginx -t
```

**如果测试通过**：

```bash
# 重启Nginx
systemctl reload nginx
```

**如果测试失败**，检查错误信息并修复配置。

### 步骤6：配置防火墙（如果需要）

```bash
# 允许HTTP端口
ufw allow 80/tcp

# 如果使用HTTPS
# ufw allow 443/tcp

# 重新加载防火墙
ufw reload
```

### 步骤7：验证部署

```bash
# 测试Nginx是否正常运行
curl http://localhost/portal.html

# 查看Nginx状态
systemctl status nginx

# 查看访问日志
tail -f /var/log/nginx/restaurant-frontend-access.log

# 查看错误日志
tail -f /var/log/nginx/restaurant-frontend-error.log
```

---

## 🌐 访问部署后的网站

部署成功后，可以通过以下URL访问：

| 功能 | URL |
|-----|-----|
| 🏠 门户首页 | `http://115.191.1.219/portal.html` |
| 👤 顾客点餐 | `http://115.191.1.219/customer_order_v3.html` |
| 🏪 工作人员登录 | `http://115.191.1.219/login_standalone.html` |
| 👨‍🍳 厨师工作台 | `http://115.191.1.219/kitchen_display.html` |
| 📋 菜品管理 | `http://115.191.1.219/menu_management.html` |
| 📦 库存管理 | `http://115.191.1.219/inventory_management.html` |
| 🏬 店铺设置 | `http://115.191.1.219/shop_settings.html` |
| 👥 会员中心 | `http://115.191.1.219/member_center.html` |
| 🏢 总公司后台 | `http://115.191.1.219/headquarters_dashboard.html` |
| 💰 结算管理 | `http://115.191.1.219/settlement_management.html` |
| 🎁 优惠管理 | `http://115.191.1.219/discount_management.html` |

**便捷短链接**：

- 主页：`http://115.191.1.219/`
- 登录：`http://115.191.1.219/login`
- 点餐：`http://115.191.1.219/customer-order`

---

## ✅ 测试清单

部署完成后，按以下步骤测试：

### 1️⃣ 基础连接测试

```bash
# 在本地执行
curl -I http://115.191.1.219/portal.html
```

**预期结果**：
- HTTP状态码：`200 OK`
- Content-Type: `text/html`

### 2️⃣ 浏览器访问测试

在浏览器中打开 `http://115.191.1.219/portal.html`，检查：

- [ ] 页面正常加载
- [ ] 样式显示正常
- [ ] 所有链接可点击
- [ ] 无404错误

### 3️⃣ API连接测试

打开浏览器开发者工具（F12）→ Network标签，刷新页面：

- [ ] API请求成功（状态码200）
- [ ] 无CORS错误
- [ ] 可以正常加载数据

### 4️⃣ 功能测试

逐个测试各功能模块：

- [ ] 顾客点餐流程完整
- [ ] 工作人员登录正常
- [ ] 订单管理功能正常
- [ ] 菜品管理功能正常
- [ ] 库存管理功能正常
- [ ] 会员中心功能正常
- [ ] 总公司后台功能正常
- [ ] 优惠管理功能正常

### 5️⃣ 移动端测试

用手机浏览器访问：

- [ ] 页面响应式布局正常
- [ ] 触摸操作流畅
- [ ] 可以正常点餐下单

---

## 🔧 常见问题排查

### 问题1：访问网站显示 404 Not Found

**原因**：Nginx配置的文件路径不正确

**解决**：

```bash
# 在服务器上检查文件是否存在
ls -la /var/www/restaurant-frontend/portal.html

# 检查Nginx配置中的root路径
grep "root" /etc/nginx/sites-available/restaurant-frontend

# 修改配置中的路径
vim /etc/nginx/sites-available/restaurant-frontend

# 重新加载Nginx
systemctl reload nginx
```

---

### 问题2：API请求失败

**原因**：前端配置的API地址可能错误

**解决**：

1. 检查后端API是否运行：
   ```bash
   curl http://115.191.1.219:8000/api/health
   ```

2. 检查前端文件中的API地址配置
   - 确保 API 地址指向 `http://115.191.1.219`
   - 端口号正确（8000, 8001, 8004, 8006, 8007）

3. 如果使用域名，确保防火墙允许外部访问

---

### 问题3：Nginx启动失败

**原因**：配置文件语法错误

**解决**：

```bash
# 测试配置文件
nginx -t

# 查看错误详情
nginx -t 2>&1 | grep -A 5 "error"

# 修复配置后重启
systemctl restart nginx
```

---

### 问题4：无法上传文件到服务器

**原因**：SSH连接问题或权限不足

**解决**：

```bash
# 测试SSH连接
ssh root@115.191.1.219 "echo 'SSH连接正常'"

# 如果SSH需要密钥，使用密钥登录
ssh -i /path/to/key root@115.191.1.219

# 如果scp无法使用，可以手动压缩并通过其他方式传输
```

---

### 问题5：页面样式异常

**原因**：静态资源路径错误或权限问题

**解决**：

```bash
# 检查静态文件权限
ls -la /var/www/restaurant-frontend/

# 修复权限
chown -R www-data:www-data /var/www/restaurant-frontend
chmod -R 755 /var/www/restaurant-frontend

# 清除浏览器缓存
# 按 Ctrl + Shift + Delete 清除缓存
```

---

## 🔄 更新前端文件

当需要更新前端时，只需重复上传和解压步骤：

```bash
# 本地重新压缩
tar -czf /tmp/restaurant-frontend.tar.gz -C assets .

# 上传到服务器
scp /tmp/restaurant-frontend.tar.gz root@115.191.1.219:/tmp/

# 在服务器上解压
ssh root@115.191.1.219
tar -xzf /tmp/restaurant-frontend.tar.gz -C /var/www/restaurant-frontend/

# 清除浏览器缓存测试
```

---

## 📊 监控和日志

### 查看Nginx日志

```bash
# 实时查看访问日志
tail -f /var/log/nginx/restaurant-frontend-access.log

# 实时查看错误日志
tail -f /var/log/nginx/restaurant-frontend-error.log

# 查看最近100条访问记录
tail -n 100 /var/log/nginx/restaurant-frontend-access.log

# 查看错误统计
grep "error" /var/log/nginx/restaurant-frontend-error.log | wc -l
```

### 监控Nginx服务状态

```bash
# 查看服务状态
systemctl status nginx

# 查看进程
ps aux | grep nginx

# 查看监听端口
netstat -tlnp | grep nginx
# 或
ss -tlnp | grep nginx
```

---

## 🔐 配置HTTPS（可选）

如果你有SSL证书，可以配置HTTPS：

### 使用Let's Encrypt免费证书

```bash
# 安装certbot
apt-get install -y certbot python3-certbot-nginx

# 自动配置HTTPS
certbot --nginx -d 115.191.1.219

# 或使用域名
certbot --nginx -d your-domain.com
```

### 手动配置HTTPS

1. 上传证书文件到服务器：
   ```bash
   /etc/nginx/ssl/restaurant-frontend.crt
   /etc/nginx/ssl/restaurant-frontend.key
   ```

2. 修改Nginx配置，取消HTTPS部分的注释

3. 重启Nginx：
   ```bash
   systemctl restart nginx
   ```

---

## 📞 获取帮助

如果遇到问题：

1. 查看Nginx日志：`/var/log/nginx/restaurant-frontend-error.log`
2. 检查Nginx配置：`nginx -t`
3. 查看防火墙状态：`ufw status`
4. 查看端口监听：`netstat -tlnp | grep nginx`

---

## ✅ 部署完成检查清单

- [ ] Nginx安装并运行正常
- [ ] 前端文件已上传到 `/var/www/restaurant-frontend`
- [ ] Nginx配置文件正确部署
- [ ] 防火墙允许80端口访问
- [ ] 可以通过浏览器访问 `http://115.191.1.219/portal.html`
- [ ] 所有功能页面链接正常
- [ ] API连接正常，无CORS错误
- [ ] 顾客点餐功能测试通过
- [ ] 工作人员登录功能测试通过
- [ ] 会员中心功能测试通过
- [ ] 总公司后台功能测试通过
- [ ] 移动端访问测试通过

---

**祝部署顺利！🎉**
