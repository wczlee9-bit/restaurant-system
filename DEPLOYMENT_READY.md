# 🎉 腾讯云部署准备完成

## ✅ 已完成的工作

### 1. 前端代码打包
- ✅ 所有前端文件已打包成 `restaurant-frontend.tar.gz`（23KB）
- ✅ 包含12个HTML文件和通用资源文件

### 2. 部署脚本准备
- ✅ `deploy_frontend.sh` - 本地自动化部署脚本
- ✅ `deploy_to_tencent_cloud.sh` - 服务器一键部署脚本

### 3. 部署文档
- ✅ `QUICK_TENCENT_DEPLOY.md` - 5分钟快速部署指南
- ✅ `TENCENT_CLOUD_DEPLOYMENT.md` - 完整部署文档

### 4. 代码提交
- ✅ 所有文件已提交到GitHub
- ✅ 可以从GitHub克隆到服务器

## 📦 需要上传的文件

### 方法1：直接上传（推荐）
上传以下文件到服务器 `/tmp/` 目录：
1. `restaurant-frontend.tar.gz`（23KB）
2. `deploy_to_tencent_cloud.sh`（部署脚本）

### 方法2：从GitHub克隆
无需上传文件，直接在服务器上执行：
```bash
git clone https://github.com/wczlee9-bit/restaurant-system.git
```

## 🚀 部署步骤（5分钟）

### 步骤1：SSH登录服务器
```bash
ssh root@115.191.1.219
```

### 步骤2：上传文件到服务器

**选项A - 使用scp上传**
```bash
# 在本地执行
scp restaurant-frontend.tar.gz root@115.191.1.219:/tmp/
scp deploy_to_tencent_cloud.sh root@115.191.1.219:/tmp/
```

**选项B - 使用FileZilla/WinSCP上传**
- 将 `restaurant-frontend.tar.gz` 上传到 `/tmp/`
- 将 `deploy_to_tencent_cloud.sh` 上传到 `/tmp/`

**选项C - 从GitHub克隆**
```bash
# 在服务器上执行
cd /tmp
git clone https://github.com/wczlee9-bit/restaurant-system.git
cp restaurant-system/restaurant-frontend.tar.gz /tmp/
cp restaurant-system/deploy_to_tencent_cloud.sh /tmp/
```

### 步骤3：运行部署脚本
```bash
# SSH登录后执行
chmod +x /tmp/deploy_to_tencent_cloud.sh
bash /tmp/deploy_to_tencent_cloud.sh
```

### 步骤4：验证部署
在浏览器中打开：
- 顾客端：http://115.191.1.219/
- 管理端：http://115.191.1.219/admin/dashboard/index.html
- API文档：http://115.191.1.219/api/docs

## 📋 部署脚本功能

`deploy_to_tencent_cloud.sh` 自动完成以下操作：

1. ✅ 检查环境（Nginx、权限）
2. ✅ 创建目录结构
3. ✅ 解压前端文件
4. ✅ 备份现有文件
5. ✅ 设置文件权限
6. ✅ 配置Nginx
7. ✅ 测试Nginx配置
8. ✅ 重启Nginx服务
9. ✅ 配置防火墙
10. ✅ 显示访问地址

## 🔧 手动部署（如果脚本失败）

如果自动脚本执行失败，可以手动执行以下命令：

```bash
# 1. 创建目录
mkdir -p /var/www/restaurant-system/frontend

# 2. 解压文件
tar -xzf /tmp/restaurant-frontend.tar.gz -C /var/www/restaurant-system/frontend/

# 3. 设置权限
chown -R www-data:www-data /var/www/restaurant-system/frontend
chmod -R 755 /var/www/restaurant-system/frontend

# 4. 配置Nginx
cat > /etc/nginx/sites-available/restaurant << 'EOF'
server {
    listen 80;
    server_name 115.191.1.219;

    location / {
        root /var/www/restaurant-system/frontend/customer;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /admin/ {
        alias /var/www/restaurant-system/frontend/admin/;
        index index.html;
        try_files $uri $uri/ /admin/dashboard/index.html;
    }

    location /common/ {
        alias /var/www/restaurant-system/frontend/common/;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
EOF

# 5. 启用配置
ln -sf /etc/nginx/sites-available/restaurant /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 6. 重启Nginx
nginx -t
systemctl restart nginx

# 7. 配置防火墙
ufw allow 80/tcp
```

## 🌐 访问地址

部署成功后，可以通过以下地址访问：

| 功能 | URL |
|------|-----|
| 顾客端首页 | http://115.191.1.219/ |
| 菜单页面 | http://115.191.1.219/menu/index.html |
| 购物车 | http://115.191.1.219/cart/index.html |
| 订单列表 | http://115.191.1.219/order/index.html |
| 个人中心 | http://115.191.1.219/profile/index.html |
| 管理端仪表盘 | http://115.191.1.219/admin/dashboard/index.html |
| 菜品管理 | http://115.191.1.219/admin/dishes/index.html |
| 订单管理 | http://115.191.1.219/admin/orders/index.html |
| 会员管理 | http://115.191.1.219/admin/members/index.html |
| API文档 | http://115.191.1.219/api/docs |

## 🧪 测试清单

### 顾客端测试
- [ ] 访问 http://115.191.1.219/ 显示欢迎页面
- [ ] 点击"开始点餐"进入菜单页面
- [ ] 菜单列表正常显示
- [ ] 添加菜品到购物车
- [ ] 查看购物车页面
- [ ] 提交订单成功

### 管理端测试
- [ ] 访问 http://115.191.1.219/admin/dashboard/index.html
- [ ] 仪表盘统计数据正常显示
- [ ] 菜品管理页面正常
- [ ] 订单管理页面正常
- [ ] 会员管理页面正常

### API测试
- [ ] 访问 http://115.191.1.219/api/docs
- [ ] 测试GET /api/tables/
- [ ] 测试GET /api/menu-items/
- [ ] 测试GET /api/orders/
- [ ] 测试POST /api/orders/

## ⚠️ 注意事项

1. **后端服务**
   - 确保后端API服务已启动（端口8000）
   - 如果后端API地址不是localhost:8000，需要修改 `/var/www/restaurant-system/frontend/common/js/api.js`

2. **防火墙**
   - 确保防火墙允许80端口访问
   - 如果使用云服务商，需要在安全组中开放80端口

3. **域名配置**
   - 如果使用域名，需要将域名解析到115.191.1.219
   - 修改Nginx配置中的server_name

4. **HTTPS（可选）**
   - 建议配置SSL证书启用HTTPS
   - 可以使用Let's Encrypt免费证书

## 📊 部署文件清单

| 文件 | 大小 | 说明 |
|------|------|------|
| restaurant-frontend.tar.gz | 23KB | 前端代码压缩包 |
| deploy_to_tencent_cloud.sh | - | 服务器一键部署脚本 |
| QUICK_TENCENT_DEPLOY.md | - | 快速部署指南 |
| TENCENT_CLOUD_DEPLOYMENT.md | - | 完整部署文档 |

## 🎯 下一步

1. **上传文件到服务器**
   - 使用scp、FileZilla或其他工具上传

2. **运行部署脚本**
   - `bash /tmp/deploy_to_tencent_cloud.sh`

3. **验证部署**
   - 访问 http://115.191.1.219

4. **测试功能**
   - 完整测试顾客端和管理端功能

5. **配置HTTPS（可选）**
   - 安装SSL证书
   - 启用HTTPS访问

## 📞 技术支持

如果遇到问题：
1. 查看Nginx日志：`tail -f /var/log/nginx/error.log`
2. 查看部署文档：`TENCENT_CLOUD_DEPLOYMENT.md`
3. 检查后端服务：`systemctl status restaurant-backend`

---

**现在可以开始部署了！按照上述步骤操作即可。** 🚀

**部署完成后，系统将可以通过 http://115.191.1.219 访问。** 🎉
