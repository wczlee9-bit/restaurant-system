# 🚀 服务器前端部署 - 最简操作指南

## 📝 前提条件

- 服务器IP：`115.191.1.219`
- 可以SSH登录到服务器（需要root权限）
- 服务器操作系统：Linux (Ubuntu/Debian/CentOS)

---

## ⚡ 5分钟快速部署（复制粘贴即可）

### 步骤1：SSH登录到服务器

```bash
ssh root@115.191.1.219
```

输入密码登录（如果提示）。

---

### 步骤2：在服务器上执行以下命令（一次性复制所有命令）

```bash
# ==========================================
# 餐饮点餐系统前端 - 一键安装脚本
# ==========================================

echo "开始安装..."

# 1. 安装Nginx
apt-get update
apt-get install -y nginx

# 2. 创建前端目录
mkdir -p /var/www/restaurant-frontend
mkdir -p /var/www/restaurant-frontend/qrcodes

# 3. 下载前端文件（从本地上传后解压）
# 如果已经有压缩包，执行：
# tar -xzf /tmp/restaurant-frontend.tar.gz -C /var/www/restaurant-frontend/

# 如果还没有上传，先创建一个测试页面
cat > /var/www/restaurant-frontend/portal.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>餐饮点餐系统 - 测试页面</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: #f5f5f5;
        }
        h1 { color: #333; }
        .success { color: #4CAF50; font-size: 24px; margin: 20px 0; }
        .info { color: #666; margin: 10px 0; }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 10px;
            cursor: pointer;
            border-radius: 5px;
            font-size: 16px;
        }
        button:hover { background: #45a049; }
    </style>
</head>
<body>
    <h1>🎉 餐饮点餐系统</h1>
    <div class="success">✓ Nginx部署成功！</div>
    <div class="info">服务器地址: 115.191.1.219</div>
    <div class="info">当前页面: portal.html</div>

    <div style="margin-top: 40px;">
        <h3>功能模块入口</h3>
        <button onclick="window.location.href='customer_order_v3.html'">👤 顾客点餐</button><br><br>
        <button onclick="window.location.href='login_standalone.html'">🏪 工作人员登录</button><br><br>
        <button onclick="window.location.href='member_center.html'">👥 会员中心</button><br><br>
        <button onclick="window.location.href='headquarters_dashboard.html'">🏢 总公司后台</button>
    </div>

    <div style="margin-top: 40px; padding: 20px; background: white; border-radius: 10px;">
        <h3>📋 部署检查清单</h3>
        <p>如果看到此页面，说明：</p>
        <ul style="text-align: left; display: inline-block;">
            <li>✅ Nginx已成功安装</li>
            <li>✅ 前端目录已创建</li>
            <li>✅ Web服务正常运行</li>
        </ul>
    </div>

    <div style="margin-top: 40px; padding: 20px; background: #fff3cd; border-radius: 10px;">
        <h3>⚠️ 下一步操作</h3>
        <p>1. 将本地的 <code>restaurant-frontend.tar.gz</code> 上传到服务器</p>
        <p>2. 在服务器上执行: <code>tar -xzf restaurant-frontend.tar.gz -C /var/www/restaurant-frontend/</code></p>
        <p>3. 重新访问页面即可看到完整系统</p>
    </div>
</body>
</html>
EOF

# 4. 设置权限
chown -R www-data:www-data /var/www/restaurant-frontend
chmod -R 755 /var/www/restaurant-frontend

# 5. 配置Nginx
cat > /etc/nginx/sites-available/restaurant << 'EOF'
server {
    listen 80;
    server_name 115.191.1.219;

    root /var/www/restaurant-frontend;
    index portal.html;

    location = / {
        return 302 /portal.html;
    }

    location / {
        try_files $uri $uri/ =404;
    }
}
EOF

# 6. 启用配置
ln -sf /etc/nginx/sites-available/restaurant /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 7. 测试配置
nginx -t

# 8. 启动Nginx
systemctl restart nginx
systemctl enable nginx

# 9. 配置防火墙
ufw allow 80/tcp
ufw reload

echo "=========================================="
echo "✅ 安装完成！"
echo "=========================================="
echo "访问地址: http://115.191.1.219"
echo "=========================================="
```

---

### 步骤3：验证部署

在本地浏览器中打开：

```
http://115.191.1.219
```

**如果看到"餐饮点餐系统"页面，说明Nginx部署成功！** 🎉

---

### 步骤4：上传完整的前端文件（重要！）

上面的步骤只是安装了Nginx并创建了测试页面。现在需要上传完整的前端文件。

#### 方法A：使用scp上传（推荐）

**在本地项目目录执行**（本地电脑，不是服务器）：

```bash
# 确保你在项目根目录
cd /workspace/projects

# 上传前端文件
scp restaurant-frontend.tar.gz root@115.191.1.219:/tmp/
```

**然后在服务器上执行**：

```bash
# SSH登录到服务器
ssh root@115.191.1.219

# 解压前端文件
tar -xzf /tmp/restaurant-frontend.tar.gz -C /var/www/restaurant-frontend/

# 重新加载Nginx
systemctl reload nginx
```

#### 方法B：手动上传文件

如果scp无法使用，可以使用其他方式上传：

1. 使用文件传输工具（如FileZilla、WinSCP）上传 `restaurant-frontend.tar.gz` 到服务器
2. 或使用U盘、网盘等中间方式传输
3. 上传后执行步骤3的解压命令

---

### 步骤5：重新访问网站

刷新浏览器页面，访问：

```
http://115.191.1.219/portal.html
```

**现在应该看到完整的餐饮点餐系统界面！** ✨

---

## 🌐 完整的访问地址列表

部署成功后，可以访问以下页面：

| 功能 | URL |
|-----|-----|
| 🏠 门户首页 | `http://115.191.1.219/portal.html` |
| 👤 顾客点餐 | `http://115.191.1.219/customer_order_v3.html` |
| 🏪 工作人员登录 | `http://115.191.1.219/login_standalone.html` |
| 👨‍🍳 厨师工作台 | `http://115.191.1.219/kitchen_display.html` |
| 🍽️ 订单管理 | `http://115.191.1.219/staff_workflow.html` |
| 📋 菜品管理 | `http://115.191.1.219/menu_management.html` |
| 📦 库存管理 | `http://115.191.1.219/inventory_management.html` |
| 🏬 店铺设置 | `http://115.191.1.219/shop_settings.html` |
| 👥 会员中心 | `http://115.191.1.219/member_center.html` |
| 🏢 总公司后台 | `http://115.191.1.219/headquarters_dashboard.html` |
| 💰 结算管理 | `http://115.191.1.219/settlement_management.html` |
| 🎁 优惠管理 | `http://115.191.1.219/discount_management.html` |

---

## ✅ 部署检查清单

部署完成后，检查以下项目：

- [ ] 可以访问 `http://115.191.1.219/portal.html`
- [ ] 页面显示正常，样式正确
- [ ] 所有功能页面链接可以点击
- [ ] 顾客点餐功能可以下单
- [ ] 工作人员可以登录
- [ ] API请求成功（无CORS错误）
- [ ] 移动端可以正常访问

---

## 🔧 常见问题

### Q1: 找不到 restaurant-frontend.tar.gz 文件

**A**: 在本地项目目录执行以下命令创建：

```bash
cd /workspace/projects
tar -czf restaurant-frontend.tar.gz -C assets .
```

---

### Q2: scp上传失败

**A**: 尝试其他上传方式：
- 使用FileZilla等FTP工具
- 使用WinSCP（Windows）
- 将文件复制到U盘，然后在服务器上读取

---

### Q3: 上传后页面还是测试页面

**A**: 确认解压路径是否正确：

```bash
# 在服务器上执行
ls -la /var/www/restaurant-frontend/portal.html

# 应该看到完整的portal.html文件，而不是测试页面
```

---

### Q4: API请求失败

**A**: 检查后端API是否运行：

```bash
# 在服务器上执行
curl http://localhost:8000/api/health
curl http://localhost:8001/api/health
```

如果API未运行，需要启动后端服务。

---

## 📞 需要帮助？

如果遇到问题，请提供：

1. 具体的错误信息
2. 执行的命令和输出
3. 浏览器访问的URL和显示的错误

---

**祝部署顺利！🚀**
