# 🚀 餐饮点餐系统 - 完整商用部署指南

## 📋 目录
- [系统架构](#系统架构)
- [部署前准备](#部署前准备)
- [后端服务器部署](#后端服务器部署)
- [前端Netlify部署](#前端netlify部署)
- [系统验证与测试](#系统验证与测试)
- [运维与维护](#运维与维护)
- [故障排除](#故障排除)

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户终端                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 顾客手机  │  │ 员工平板  │  │ 店长电脑  │  │ 管理后台  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Netlify (前端)                             │
│           静态网站托管 + API代理 + HTTPS                      │
│   https://yourdomain.netlify.app (或自定义域名)               │
└─────────────────────────────────────────────────────────────┘
                            │
                    API 代理转发
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              后端API服务器 (9.128.251.82)                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐             │
│  │顾客API  │ │店员API  │ │会员API  │ │总公司API│             │
│  │ :8000   │ │ :8001   │ │ :8004   │ │ :8006   │             │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘             │
│                      │                                        │
│              ┌───────▼───────┐                                │
│              │ PostgreSQL DB  │                                │
│              │   (数据库)      │                                │
│              └───────────────┘                                │
│                      │                                        │
│              ┌───────▼───────┐                                │
│              │   S3存储      │                                │
│              │ (二维码/图片)  │                                │
│              └───────────────┘                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 部署前准备

### 1. 硬件要求

**后端服务器配置（最低）**
- CPU: 2核心
- 内存: 4GB
- 硬盘: 50GB SSD
- 带宽: 10Mbps
- 操作系统: Ubuntu 20.04+ 或 CentOS 7+

**推荐配置**
- CPU: 4核心
- 内存: 8GB
- 硬盘: 100GB SSD
- 带宽: 20Mbps

### 2. 软件依赖

**服务器端**
- Python 3.8+
- PostgreSQL 13+
- Git
- Nginx (可选，用于反向代理)
- Systemd (用于服务管理)

**客户端**
- 现代浏览器 (Chrome 90+, Safari 14+, Firefox 88+, Edge 90+)
- iOS 12+ 或 Android 8+

### 3. 第三方服务

| 服务 | 用途 | 免费额度 | 推荐服务商 |
|------|------|---------|-----------|
| S3对象存储 | 存储二维码、图片 | 5GB存储 | 阿里云OSS / 腾讯云COS / AWS S3 |
| 域名解析 | 自定义域名 | - | 阿里云DNS / 腾讯云DNS |
| SSL证书 | HTTPS加密 | 免费(Let's Encrypt) | Certbot / 云服务商 |

### 4. 账号准备

- [ ] Netlify账号 (免费)
- [ ] GitHub账号 (用于代码管理)
- [ ] S3对象存储账号
- [ ] 数据库管理员账号 (PostgreSQL)

---

## 后端服务器部署

### 步骤 1: 连接服务器并更新系统

```bash
# 连接到服务器 (将IP替换为实际IP)
ssh root@9.128.251.82

# 更新系统
sudo apt update && sudo apt upgrade -y

# 设置时区 (可选)
sudo timedatectl set-timezone Asia/Shanghai
```

### 步骤 2: 安装必要软件

```bash
# 安装 Python 3.8+
sudo apt install python3.8 python3-pip python3-venv git -y

# 验证Python版本
python3 --version

# 安装 PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# 安装 Nginx (推荐，用于反向代理和负载均衡)
sudo apt install nginx -y

# 安装 Supervisor (用于进程管理)
sudo apt install supervisor -y

# 启用并启动Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 步骤 3: 配置 PostgreSQL 数据库

```bash
# 切换到postgres用户
sudo -u postgres psql

# 执行以下SQL命令 (复制粘贴)
-- 创建数据库
CREATE DATABASE restaurant_db;

-- 创建数据库用户
CREATE USER restaurant_user WITH PASSWORD 'your_secure_password';

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE restaurant_db TO restaurant_user;

-- 退出
\q

# 测试连接
psql -h localhost -U restaurant_user -d restaurant_db -c "SELECT version();"
```

### 步骤 4: 克隆代码到服务器

```bash
# 进入/opt目录
cd /opt

# 克隆代码仓库 (将YOUR_GITHUB_REPO替换为实际地址)
# 如果没有Git仓库，可以先跳过，后面手动上传代码
git clone https://github.com/YOUR_USERNAME/restaurant-system.git

# 进入项目目录
cd restaurant-system

# 或手动上传代码
# 在本地执行: scp -r /path/to/restaurant-system root@9.128.251.82:/opt/
```

### 步骤 5: 创建Python虚拟环境并安装依赖

```bash
# 进入项目目录
cd /opt/restaurant-system

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 退出虚拟环境
deactivate
```

### 步骤 6: 配置环境变量

```bash
# 创建环境变量文件
sudo nano /opt/restaurant-system/.env

# 添加以下内容 (根据实际情况修改)
DATABASE_URL=postgresql://restaurant_user:your_secure_password@localhost:5432/restaurant_db
S3_ACCESS_KEY=your_s3_access_key
S3_SECRET_KEY=your_s3_secret_key
S3_BUCKET_NAME=your_bucket_name
S3_REGION=us-east-1
S3_ENDPOINT=https://your_s3_endpoint
COZE_API_KEY=your_coze_api_key

# 保存并退出 (Ctrl+X, Y, Enter)

# 设置文件权限
sudo chmod 600 /opt/restaurant-system/.env
```

### 步骤 7: 初始化数据库

```bash
# 激活虚拟环境
cd /opt/restaurant-system
source venv/bin/activate

# 运行数据库迁移脚本
python scripts/init_database.py

# 或手动创建表
python -c "
from storage.database.db import engine
from storage.database.shared.model import Base
Base.metadata.create_all(bind=engine)
print('数据库表创建成功')
"

# 退出虚拟环境
deactivate
```

### 步骤 8: 创建Systemd服务配置

为每个API服务创建独立的Systemd服务文件：

```bash
# 创建顾客API服务
sudo nano /etc/systemd/system/restaurant-customer-api.service
```

内容：
```ini
[Unit]
Description=Restaurant Customer API
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/restaurant-system
Environment="PATH=/opt/restaurant-system/venv/bin"
ExecStart=/opt/restaurant-system/venv/bin/python -m uvicorn api.customer_api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 创建店员API服务
sudo nano /etc/systemd/system/restaurant-staff-api.service
```

内容：
```ini
[Unit]
Description=Restaurant Staff API
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/restaurant-system
Environment="PATH=/opt/restaurant-system/venv/bin"
ExecStart=/opt/restaurant-system/venv/bin/python -m uvicorn api.staff_api:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 创建会员API服务
sudo nano /etc/systemd/system/restaurant-member-api.service
```

内容：
```ini
[Unit]
Description=Restaurant Member API
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/restaurant-system
Environment="PATH=/opt/restaurant-system/venv/bin"
ExecStart=/opt/restaurant-system/venv/bin/python -m uvicorn api.member_api:app --host 0.0.0.0 --port 8004
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 创建总公司API服务
sudo nano /etc/systemd/system/restaurant-hq-api.service
```

内容：
```ini
[Unit]
Description=Restaurant Headquarters API
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/restaurant-system
Environment="PATH=/opt/restaurant-system/venv/bin"
ExecStart=/opt/restaurant-system/venv/bin/python -m uvicorn api.headquarters_api:app --host 0.0.0.0.0 --port 8006
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 步骤 9: 启动所有API服务

```bash
# 重载Systemd配置
sudo systemctl daemon-reload

# 启用所有服务 (开机自启)
sudo systemctl enable restaurant-customer-api
sudo systemctl enable restaurant-staff-api
sudo systemctl enable restaurant-member-api
sudo systemctl enable restaurant-hq-api

# 启动所有服务
sudo systemctl start restaurant-customer-api
sudo systemctl start restaurant-staff-api
sudo systemctl start restaurant-member-api
sudo systemctl start restaurant-hq-api

# 检查服务状态
sudo systemctl status restaurant-customer-api
sudo systemctl status restaurant-staff-api
sudo systemctl status restaurant-member-api
sudo systemctl status restaurant-hq-api

# 查看日志
sudo journalctl -u restaurant-customer-api -f
```

### 步骤 10: 配置防火墙

```bash
# 如果使用ufw防火墙
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 8001/tcp
sudo ufw allow 8004/tcp
sudo ufw allow 8006/tcp
sudo ufw enable

# 如果使用iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8001 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8004 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8006 -j ACCEPT
```

### 步骤 11: 配置Nginx反向代理 (可选但推荐)

```bash
# 创建Nginx配置文件
sudo nano /etc/nginx/sites-available/restaurant-api
```

内容：
```nginx
upstream customer_api {
    server 127.0.0.1:8000;
}

upstream staff_api {
    server 127.0.0.1:8001;
}

upstream member_api {
    server 127.0.0.1:8004;
}

upstream hq_api {
    server 127.0.0.1:8006;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # 日志
    access_log /var/log/nginx/restaurant-api-access.log;
    error_log /var/log/nginx/restaurant-api-error.log;

    # API路由
    location /api/orders {
        proxy_pass http://customer_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/member {
        proxy_pass http://member_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/headquarters {
        proxy_pass http://hq_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://staff_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket支持
    location /ws {
        proxy_pass http://staff_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

```bash
# 启用站点配置
sudo ln -s /etc/nginx/sites-available/restaurant-api /etc/nginx/sites-enabled/

# 测试Nginx配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 步骤 12: 验证后端服务

```bash
# 测试顾客API
curl http://localhost:8000/docs

# 测试店员API
curl http://localhost:8001/docs

# 测试会员API
curl http://localhost:8004/docs

# 测试总公司API
curl http://localhost:8006/docs

# 测试外部访问 (替换为实际IP)
curl http://9.128.251.82:8000/health
```

---

## 前端Netlify部署

### 步骤 1: 准备前端文件

在项目根目录，确认以下文件存在：

```
restaurant-system/
├── assets/              # 前端静态文件
│   ├── portal.html
│   ├── member_center.html
│   ├── headquarters_dashboard.html
│   ├── customer_order_v3.html
│   ├── staff_workflow.html
│   └── ...
├── netlify.toml         # Netlify配置文件
└── ...
```

### 步骤 2: 更新Netlify配置

编辑 `netlify.toml`，将后端IP地址替换为实际的服务器IP：

```toml
# 找到这一行
to = "http://YOUR_BACKEND_IP:8000/api/:splat"

# 替换为实际IP
to = "http://9.128.251.82:8000/api/:splat"

# 对所有API路由做相同替换
```

### 步骤 3: 推送代码到GitHub

```bash
# 在本地执行
git add .
git commit -m "Update for production deployment"
git push origin main
```

### 步骤 4: 在Netlify创建新站点

#### 方法A: 通过GitHub集成 (推荐)

1. 登录 Netlify: https://app.netlify.com
2. 点击 "Add new site" → "Import an existing project"
3. 选择 "GitHub"，授权访问
4. 选择代码仓库 `restaurant-system`
5. 配置构建设置：
   - Build command: (留空)
   - Publish directory: `assets`
6. 点击 "Deploy site"

#### 方法B: 拖拽部署

1. 打开 Netlify: https://app.netlify.com/drop
2. 将整个 `assets/` 文件夹拖拽到页面
3. 等待部署完成
4. 将 `netlify.toml` 上传到站点根目录

### 步骤 5: 配置自定义域名 (可选)

1. 在Netlify Dashboard中，点击 "Domain settings"
2. 点击 "Add custom domain"
3. 输入域名 (如: `restaurant.example.com`)
4. 配置DNS解析：
   ```
   Type: CNAME
   Name: restaurant
   Value: your-site-name.netlify.app
   ```
5. 等待DNS生效 (通常5-15分钟)

### 步骤 6: 验证部署

```bash
# 访问主页
https://your-site-name.netlify.app

# 测试API代理 (在浏览器开发者工具中)
fetch('/api/health')
  .then(r => r.text())
  .then(console.log)
```

---

## 系统验证与测试

### 1. 后端服务验证

```bash
# 在服务器上运行
sudo systemctl status restaurant-customer-api
sudo systemctl status restaurant-staff-api
sudo systemctl status restaurant-member-api
sudo systemctl status restaurant-hq-api

# 测试数据库连接
psql -h localhost -U restaurant_user -d restaurant_db -c "SELECT COUNT(*) FROM stores;"

# 检查日志
sudo journalctl -u restaurant-customer-api -n 50 --no-pager
```

### 2. 前端功能测试

使用浏览器访问前端页面，依次测试：

#### 顾客端测试
- [ ] 访问门户页面 (`/portal.html`)
- [ ] 选择桌号并点餐
- [ ] 查看菜单和价格
- [ ] 提交订单
- [ ] 选择支付方式
- [ ] 查看订单状态

#### 工作人员端测试
- [ ] 登录 (店长/厨师/传菜员/收银员)
- [ ] 查看订单列表
- [ ] 更新订单状态
- [ ] 打印小票
- [ ] 管理库存

#### 会员中心测试
- [ ] 手机号登录
- [ ] 查看积分
- [ ] 查看消费记录
- [ ] 查看积分日志
- [ ] 测试跨店铺积分

#### 总公司后台测试
- [ ] 登录总公司后台
- [ ] 查看总体统计
- [ ] 查看营收趋势图表
- [ ] 查看店铺排名
- [ ] 查看员工列表
- [ ] 查看会员统计

### 3. 集成测试

#### 订单完整流程测试

```
1. 顾客扫码 → 点餐 → 提交订单
2. 店员接单 → 确认订单
3. 厨师制作中
4. 传菜员上菜
5. 收银员结算 → 支付完成
6. 积分自动增加
7. 会员中心查看记录
8. 总公司查看营收数据
```

### 4. 性能测试

```bash
# 使用Apache Bench进行压力测试
ab -n 1000 -c 100 https://your-site-name.netlify.app/

# 或使用wrk
wrk -t4 -c100 -d30s https://your-site-name.netlify.app/
```

### 5. 安全测试

- [ ] 检查SQL注入漏洞
- [ ] 检查XSS跨站脚本漏洞
- [ ] 检查CSRF跨站请求伪造
- [ ] 验证API权限控制
- [ ] 检查敏感数据加密

---

## 运维与维护

### 日常监控

#### 1. 系统资源监控

```bash
# 查看CPU和内存使用
htop

# 查看磁盘使用
df -h

# 查看网络连接
netstat -tunlp

# 查看进程
ps aux | grep uvicorn
```

#### 2. 服务监控

```bash
# 检查所有服务状态
sudo systemctl status restaurant-*

# 设置自动重启 (已在systemd配置中)
sudo systemctl restart restaurant-customer-api
```

#### 3. 日志监控

```bash
# 实时查看日志
sudo journalctl -u restaurant-customer-api -f

# 查看最近100行
sudo journalctl -u restaurant-customer-api -n 100

# 查看错误日志
sudo journalctl -u restaurant-customer-api -p err -n 50
```

### 数据备份

#### 数据库备份

```bash
# 创建备份脚本
sudo nano /opt/restaurant-system/scripts/backup_db.sh
```

内容：
```bash
#!/bin/bash
BACKUP_DIR="/opt/restaurant-system/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/restaurant_db_$DATE.sql"

mkdir -p $BACKUP_DIR

# 备份数据库
pg_dump -h localhost -U restaurant_user restaurant_db > $BACKUP_FILE

# 压缩备份
gzip $BACKUP_FILE

# 保留最近7天的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

```bash
# 设置执行权限
chmod +x /opt/restaurant-system/scripts/backup_db.sh

# 添加到crontab (每天凌晨2点备份)
sudo crontab -e

# 添加以下行
0 2 * * * /opt/restaurant-system/scripts/backup_db.sh >> /var/log/restaurant_backup.log 2>&1
```

#### 文件备份

```bash
# 备份配置文件和上传的文件
tar -czf /opt/restaurant-system/backups/config_$(date +%Y%m%d).tar.gz \
  /opt/restaurant-system/.env \
  /opt/restaurant-system/config/
```

### 定期更新

#### 1. 系统更新

```bash
# 每月更新一次系统
sudo apt update && sudo apt upgrade -y
```

#### 2. 依赖更新

```bash
cd /opt/restaurant-system
source venv/bin/activate
pip list --outdated
pip install --upgrade package-name
deactivate
```

#### 3. 代码更新

```bash
cd /opt/restaurant-system
git pull origin main

# 重启服务
sudo systemctl restart restaurant-customer-api
sudo systemctl restart restaurant-staff-api
sudo systemctl restart restaurant-member-api
sudo systemctl restart restaurant-hq-api
```

### 扩容方案

#### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_store_id ON orders(store_id);
CREATE INDEX idx_orders_member_id ON orders(member_id);

-- 定期清理历史数据
DELETE FROM orders WHERE created_at < NOW() - INTERVAL '6 months';
```

#### 2. 增加服务器

```bash
# 使用负载均衡 (Nginx)
upstream customer_api {
    server 192.168.1.10:8000;
    server 192.168.1.11:8000;
    server 192.168.1.12:8000;
}
```

#### 3. 使用Redis缓存

```bash
# 安装Redis
sudo apt install redis-server -y

# 启动Redis
sudo systemctl start redis
sudo systemctl enable redis

# 在代码中使用Redis缓存热点数据
```

---

## 故障排除

### 常见问题

#### 1. API无法访问

**症状**: 前端提示API连接失败

**解决方案**:
```bash
# 检查服务状态
sudo systemctl status restaurant-customer-api

# 检查端口占用
sudo netstat -tunlp | grep 8000

# 检查防火墙
sudo ufw status

# 检查日志
sudo journalctl -u restaurant-customer-api -n 50
```

#### 2. 数据库连接失败

**症状**: 后端日志显示数据库连接错误

**解决方案**:
```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 测试连接
psql -h localhost -U restaurant_user -d restaurant_db

# 检查环境变量
cat /opt/restaurant-system/.env

# 检查数据库权限
sudo -u postgres psql -c "\l"
```

#### 3. WebSocket连接失败

**症状**: 订单状态不实时更新

**解决方案**:
```bash
# 检查WebSocket端口
sudo netstat -tunlp | grep 8001

# 检查Nginx配置 (如果使用)
sudo nginx -t
sudo systemctl reload nginx

# 检查浏览器控制台错误
# 确保前端WebSocket URL正确
```

#### 4. 文件上传失败

**症状**: 二维码生成失败或图片无法显示

**解决方案**:
```bash
# 检查S3配置
cat /opt/restaurant-system/.env | grep S3

# 测试S3连接
aws s3 ls s3://your-bucket-name

# 检查权限
ls -la /opt/restaurant-system/assets/uploads/
```

#### 5. Netlify部署失败

**症状**: Netlify显示构建错误

**解决方案**:
1. 检查 `netlify.toml` 配置
2. 确认 `assets/` 目录存在
3. 检查构建日志
4. 尝试手动拖拽部署

#### 6. 跨域问题

**症状**: 浏览器控制台显示CORS错误

**解决方案**:
```python
# 检查API中的CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 7. 性能问题

**症状**: 页面加载慢，API响应慢

**解决方案**:
```bash
# 1. 启用Nginx gzip压缩
sudo nano /etc/nginx/nginx.conf
# 添加:
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# 2. 使用CDN加速静态资源
# 3. 数据库查询优化
# 4. 启用Redis缓存
```

### 紧急恢复

#### 数据库恢复

```bash
# 从备份恢复
gunzip /opt/restaurant-system/backups/restaurant_db_20240101_020000.sql.gz

psql -h localhost -U restaurant_user -d restaurant_db < \
  /opt/restaurant-system/backups/restaurant_db_20240101_020000.sql
```

#### 服务快速重启

```bash
# 重启所有服务
sudo systemctl restart restaurant-customer-api
sudo systemctl restart restaurant-staff-api
sudo systemctl restart restaurant-member-api
sudo systemctl restart restaurant-hq-api

# 或使用脚本
for service in restaurant-customer-api restaurant-staff-api restaurant-member-api restaurant-hq-api; do
    sudo systemctl restart $service
done
```

---

## 总结

本部署指南涵盖了从零开始到生产环境部署的完整流程。按照本指南操作，你应该能够成功部署一个稳定、可扩展的商用餐饮点餐系统。

### 关键检查清单

- [ ] 后端服务器配置完成 (Python, PostgreSQL, Nginx)
- [ ] 数据库初始化完成
- [ ] 所有API服务正常运行
- [ ] Systemd服务配置完成
- [ ] 防火墙配置完成
- [ ] 前端部署到Netlify
- [ ] API代理配置正确
- [ ] 自定义域名配置完成 (可选)
- [ ] 数据备份脚本配置完成
- [ ] 监控和日志配置完成
- [ ] 所有功能测试通过
- [ ] 性能测试完成
- [ ] 安全测试完成

### 下一步

1. 配置支付接口 (微信支付/支付宝)
2. 配置短信通知服务
3. 配置邮件通知服务
4. 完善用户文档
5. 培训员工使用系统
6. 制定运维手册

---

**祝部署顺利！如有问题，请参考故障排除章节或联系技术支持。**
