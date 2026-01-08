# 🚀 餐饮点餐系统 - 快速开始指南

欢迎使用餐饮点餐系统！本指南将帮助你在30分钟内完成商用系统的部署和上线。

---

## 📋 部署概览

本系统采用前后端分离架构：
- **前端**: 部署在 Netlify (静态网站)
- **后端**: 部署在你的服务器上 (API服务)

---

## ⚡ 5分钟快速部署

### 步骤 1: 准备工作 (2分钟)

✅ 确认你已有：
- [ ] 一台Linux服务器 (推荐Ubuntu 20.04+)
- [ ] Netlify账号 (免费注册: https://app.netlify.com)
- [ ] GitHub账号 (可选，用于代码管理)

### 步骤 2: 部署后端服务器 (20分钟)

#### 2.1 连接服务器
```bash
ssh root@9.128.251.82
```

#### 2.2 上传代码
```bash
# 方法A: 如果有Git仓库
cd /opt
git clone https://github.com/YOUR_USERNAME/restaurant-system.git

# 方法B: 手动上传
# 在本地使用 scp 命令上传整个项目文件夹
scp -r /path/to/restaurant-system root@9.128.251.82:/opt/
```

#### 2.3 一键部署
```bash
cd /opt/restaurant-system
chmod +x scripts/deploy_to_server.sh
sudo ./scripts/deploy_to_server.sh install
```

脚本会自动完成：
- ✅ 安装Python、PostgreSQL、Nginx
- ✅ 配置数据库
- ✅ 创建Systemd服务
- ✅ 启动所有API服务
- ✅ 配置防火墙

#### 2.4 配置环境变量
```bash
nano /opt/restaurant-system/.env
```

填入以下信息（根据实际情况修改）：
```env
DATABASE_URL=postgresql://restaurant_user:your_password@localhost:5432/restaurant_db
S3_ACCESS_KEY=your_s3_access_key
S3_SECRET_KEY=your_s3_secret_key
S3_BUCKET_NAME=your_bucket_name
S3_REGION=us-east-1
S3_ENDPOINT=https://your_s3_endpoint
COZE_API_KEY=your_coze_api_key
```

保存并重启服务：
```bash
sudo systemctl restart restaurant-*
```

### 步骤 3: 部署前端到Netlify (5分钟)

#### 3.1 更新Netlify配置

编辑项目根目录的 `netlify.toml`：

```toml
# 将 YOUR_BACKEND_IP 替换为你的服务器IP
to = "http://9.128.251.82:8000/api/:splat"
```

#### 3.2 部署到Netlify

**方法A: 拖拽部署（最快）**
1. 访问: https://app.netlify.com/drop
2. 将 `assets/` 文件夹拖拽到页面
3. 等待部署完成，获得站点地址

**方法B: GitHub集成（推荐）**
```bash
# 在本地执行
git add .
git commit -m "Update for production"
git push origin main
```

然后在 Netlify Dashboard 导入GitHub仓库。

#### 3.3 配置自定义域名（可选）

1. 在 Netlify Dashboard 添加自定义域名
2. 配置DNS解析
3. 等待HTTPS证书生成

### 步骤 4: 验证部署 (3分钟)

#### 4.1 在服务器上运行验证脚本
```bash
cd /opt/restaurant-system
sudo ./scripts/verify_system.sh
```

#### 4.2 在浏览器测试
访问你的Netlify站点地址，测试以下功能：
- [ ] 门户页面正常显示
- [ ] 可以选择桌号点餐
- [ ] 工作人员可以登录
- [ ] 会员中心可以访问
- [ ] 总公司后台可以登录

---

## 📚 详细文档

如果你需要更详细的说明，请参考以下文档：

### 1. 完整商用部署指南
📄 `COMMERCIAL_DEPLOYMENT.md`

包含内容：
- 系统架构图
- 详细的安装步骤
- 数据库配置
- Systemd服务配置
- Nginx反向代理配置
- 备份策略
- 扩容方案
- 故障排除

### 2. Netlify部署指南
📄 `NETLIFY_DEPLOYMENT.md`

包含内容：
- Netlify详细介绍
- 三种部署方法
- 自定义域名配置
- API代理配置
- 常见问题解决

### 3. 用户使用手册
📄 `USER_MANUAL.md`

包含内容：
- 顾客端使用指南
- 工作人员端使用指南
- 会员中心使用指南
- 总公司后台使用指南
- 常见问题解答

### 4. 服务器部署脚本
🔧 `scripts/deploy_to_server.sh`

使用方法：
```bash
# 安装系统
sudo ./scripts/deploy_to_server.sh install

# 更新系统
sudo ./scripts/deploy_to_server.sh update

# 启动服务
sudo ./scripts/deploy_to_server.sh start

# 停止服务
sudo ./scripts/deploy_to_server.sh stop

# 重启服务
sudo ./scripts/deploy_to_server.sh restart

# 查看状态
sudo ./scripts/deploy_to_server.sh status

# 备份数据库
sudo ./scripts/deploy_to_server.sh backup

# 恢复数据库
sudo ./scripts/deploy_to_server.sh restore /path/to/backup.sql.gz
```

### 5. 系统验证脚本
🔧 `scripts/verify_system.sh`

使用方法：
```bash
sudo ./scripts/verify_system.sh
```

验证内容：
- 系统服务状态
- 端口监听情况
- 数据库连接
- API端点可用性
- 文件完整性
- 日志检查
- 性能检查
- 安全检查
- 备份检查

---

## 🔧 常用命令

### 后端服务管理

```bash
# 查看所有服务状态
sudo systemctl status restaurant-*

# 启动所有服务
sudo systemctl start restaurant-*

# 停止所有服务
sudo systemctl stop restaurant-*

# 重启所有服务
sudo systemctl restart restaurant-*

# 查看服务日志
sudo journalctl -u restaurant-customer-api -f
sudo journalctl -u restaurant-staff-api -f
sudo journalctl -u restaurant-member-api -f
sudo journalctl -u restaurant-hq-api -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/restaurant-api-access.log
sudo tail -f /var/log/nginx/restaurant-api-error.log
```

### 数据库管理

```bash
# 连接数据库
psql -h localhost -U restaurant_user -d restaurant_db

# 备份数据库
pg_dump -h localhost -U restaurant_user restaurant_db > backup.sql

# 恢复数据库
psql -h localhost -U restaurant_user -d restaurant_db < backup.sql

# 查看数据库大小
psql -h localhost -U restaurant_user -d restaurant_db -c "SELECT pg_size_pretty(pg_database_size('restaurant_db'));"
```

### 防火墙管理

```bash
# 查看防火墙状态
sudo ufw status

# 开放端口
sudo ufw allow 8000/tcp
sudo ufw allow 8001/tcp
sudo ufw allow 8004/tcp
sudo ufw allow 8006/tcp
```

### 日志查看

```bash
# 查看最近100行日志
sudo journalctl -u restaurant-customer-api -n 100

# 查看错误日志
sudo journalctl -u restaurant-customer-api -p err

# 实时查看日志
sudo journalctl -u restaurant-customer-api -f
```

---

## 🎯 系统访问地址

部署完成后，你的系统可以通过以下地址访问：

### 前端地址
```
主页: https://your-site.netlify.app
顾客端: https://your-site.netlify.app/customer_order_v3.html?table=1
工作人员登录: https://your-site.netlify.app/login_standalone.html
会员中心: https://your-site.netlify.app/member_center.html
总公司后台: https://your-site.netlify.app/headquarters_dashboard.html
```

### 后端API
```
顾客API: http://9.128.251.82:8000
店员API: http://9.128.251.82:8001
会员API: http://9.128.251.82:8004
总公司API: http://9.128.251.82:8006

API文档:
- http://9.128.251.82:8000/docs
- http://9.128.251.82:8001/docs
- http://9.128.251.82:8004/docs
- http://9.128.251.82:8006/docs
```

### WebSocket
```
WebSocket: ws://9.128.251.82:8001/ws
```

---

## 💡 提示和建议

### 性能优化

1. **启用Nginx缓存**
   ```nginx
   location /api/ {
       proxy_cache my_cache;
       proxy_cache_valid 200 60m;
       proxy_pass http://staff_api;
   }
   ```

2. **使用CDN加速静态资源**
   - Netlify自动提供CDN
   - 确保图片已优化

3. **数据库索引优化**
   ```sql
   CREATE INDEX idx_orders_created_at ON orders(created_at);
   CREATE INDEX idx_orders_store_id ON orders(store_id);
   ```

### 安全建议

1. **定期更新系统和依赖**
   ```bash
   sudo apt update && sudo apt upgrade -y
   cd /opt/restaurant-system
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **配置防火墙**
   ```bash
   sudo ufw enable
   sudo ufw default deny incoming
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

3. **定期备份数据**
   - 已配置每天凌晨2点自动备份
   - 备份文件保存在 `/opt/restaurant-system/backups/`

### 监控建议

1. **监控服务状态**
   ```bash
   # 创建监控脚本
   nano /opt/scripts/monitor.sh
   ```

   ```bash
   #!/bin/bash
   for service in restaurant-customer-api restaurant-staff-api restaurant-member-api restaurant-hq-api; do
       if ! systemctl is-active --quiet $service; then
           echo "Service $service is not running. Restarting..."
           systemctl restart $service
       fi
   done
   ```

   ```bash
   # 添加到crontab（每5分钟检查一次）
   chmod +x /opt/scripts/monitor.sh
   (crontab -l 2>/dev/null; echo "*/5 * * * * /opt/scripts/monitor.sh") | crontab -
   ```

2. **监控磁盘空间**
   ```bash
   # 添加到crontab（每天检查一次）
   (crontab -l 2>/dev/null; echo "0 9 * * * df -h | mail -s 'Disk Usage' admin@example.com") | crontab -
   ```

---

## ❓ 遇到问题？

### 常见问题快速解决

#### 1. 服务无法启动
```bash
# 查看服务状态
sudo systemctl status restaurant-customer-api

# 查看详细日志
sudo journalctl -u restaurant-customer-api -n 50

# 检查端口占用
sudo netstat -tunlp | grep 8000
```

#### 2. 数据库连接失败
```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 测试数据库连接
psql -h localhost -U restaurant_user -d restaurant_db -c "SELECT 1;"

# 检查环境变量
cat /opt/restaurant-system/.env
```

#### 3. API请求失败
```bash
# 测试API端点
curl http://localhost:8000/api/health

# 检查防火墙
sudo ufw status

# 检查Nginx配置
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. Netlify部署失败
- 检查 `netlify.toml` 配置
- 确认 `assets/` 目录存在
- 查看Netlify构建日志
- 尝试手动拖拽部署

### 获取帮助

如果以上方法无法解决问题：

1. 查看详细文档：
   - 完整商用部署指南: `COMMERCIAL_DEPLOYMENT.md`
   - 故障排除章节

2. 查看日志文件：
   - 系统日志: `sudo journalctl -u restaurant-*`
   - Nginx日志: `/var/log/nginx/restaurant-api-*.log`

3. 联系技术支持：
   - 邮箱: support@example.com
   - 电话: 400-xxx-xxxx

---

## 🎉 恭喜！

你已经成功部署了餐饮点餐系统！

### 下一步

1. **配置支付接口**
   - 接入微信支付
   - 接入支付宝

2. **配置短信通知**
   - 订单状态通知
   - 会员注册验证码

3. **培训员工**
   - 工作人员端使用培训
   - 会员中心使用培训

4. **准备上线**
   - 生成桌号二维码
   - 测试完整流程
   - 正式开业

---

**祝你生意兴隆！🍽️**
