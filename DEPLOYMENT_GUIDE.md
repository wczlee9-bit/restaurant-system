# 🚀 餐饮点餐系统 - 正式部署指南

本文档详细介绍如何将餐饮点餐系统部署到生产环境，包括后端 API 服务器部署和前端 Netlify 部署。

---

## 📋 部署前准备

### 1. 服务器准备

#### 需要的服务器
- **后端 API 服务器**：1 台 Linux 服务器（推荐 Ubuntu 20.04+）
- **数据库服务器**：PostgreSQL 13+（可以是与后端同一台服务器）
- **对象存储**：兼容 S3 的对象存储服务（如 AWS S3、阿里云 OSS、腾讯云 COS）

#### 软件环境
- Python 3.8+
- PostgreSQL 13+
- Nginx（可选，用于反向代理）
- Git

### 2. 域名准备
- 主域名（如：restaurant.example.com）
- API 子域名（如：api.restaurant.example.com）
- 或使用 Netlify 提供的子域名

### 3. 配置文件准备
- 数据库连接信息
- 对象存储访问凭证
- 支付接口配置（如需要）

---

## 🔧 后端 API 服务器部署

### 步骤 1：安装必要软件

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.8+
sudo apt install python3.8 python3-pip python3-venv git -y

# 安装 PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# 安装 Nginx（可选，用于反向代理）
sudo apt install nginx -y
```

### 步骤 2：配置 PostgreSQL 数据库

```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 创建数据库和用户
CREATE DATABASE restaurant_db;
CREATE USER restaurant_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE restaurant_db TO restaurant_user;
\q
```

### 步骤 3：克隆项目代码

```bash
# 创建项目目录
sudo mkdir -p /opt/restaurant
sudo chown $USER:$USER /opt/restaurant

# 克隆代码（假设使用 GitHub）
cd /opt/restaurant
git clone https://github.com/your-username/restaurant-system.git

# 进入项目目录
cd restaurant-system
```

### 步骤 4：创建 Python 虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

### 步骤 5：配置环境变量

```bash
# 创建环境变量文件
cat > .env << EOF
# 数据库配置
DATABASE_URL=postgresql://restaurant_user:your_secure_password@localhost:5432/restaurant_db

# 对象存储配置
S3_BUCKET=your-bucket-name
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_ENDPOINT=https://your-s3-endpoint.com

# API 配置
API_BASE_URL=http://api.restaurant.example.com

# 其他配置
LOG_LEVEL=INFO
EOF
```

### 步骤 6：初始化数据库

```bash
# 运行数据库迁移脚本
python scripts/init_database.py

# 创建测试数据（可选）
python scripts/init_test_data_full.py
```

### 步骤 7：配置 systemd 服务

创建 API 服务文件：

```bash
sudo nano /etc/systemd/system/restaurant-restaurant-api.service
```

内容如下：

```ini
[Unit]
Description=Restaurant API Service (Main)
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/restaurant/restaurant-system
Environment="PATH=/opt/restaurant/restaurant-system/venv/bin"
ExecStart=/opt/restaurant/restaurant-system/venv/bin/python -m uvicorn api.restaurant_api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

创建其他 API 服务：

```bash
sudo nano /etc/systemd/system/restaurant-customer-api.service
```

```ini
[Unit]
Description=Restaurant API Service (Customer)
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/restaurant/restaurant-system
Environment="PATH=/opt/restaurant/restaurant-system/venv/bin"
ExecStart=/opt/restaurant/restaurant-system/venv/bin/python -m uvicorn api.customer_api:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo nano /etc/systemd/system/restaurant-member-api.service
```

```ini
[Unit]
Description=Restaurant API Service (Member)
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/restaurant/restaurant-system
Environment="PATH=/opt/restaurant/restaurant-system/venv/bin"
ExecStart=/opt/restaurant/restaurant-system/venv/bin/python -m uvicorn api.member_api:app --host 0.0.0.0 --port 8004
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo nano /etc/systemd/system/restaurant-headquarters-api.service
```

```ini
[Unit]
Description=Restaurant API Service (Headquarters)
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/restaurant/restaurant-system
Environment="PATH=/opt/restaurant/restaurant-system/venv/bin"
ExecStart=/opt/restaurant/restaurant-system/venv/bin/python -m uvicorn api.headquarters_api:app --host 0.0.0.0 --port 8006
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动所有服务：

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start restaurant-restaurant-api
sudo systemctl start restaurant-customer-api
sudo systemctl start restaurant-member-api
sudo systemctl start restaurant-headquarters-api

# 设置开机自启
sudo systemctl enable restaurant-restaurant-api
sudo systemctl enable restaurant-customer-api
sudo systemctl enable restaurant-member-api
sudo systemctl enable restaurant-headquarters-api

# 检查服务状态
sudo systemctl status restaurant-restaurant-api
sudo systemctl status restaurant-customer-api
sudo systemctl status restaurant-member-api
sudo systemctl status restaurant-headquarters-api
```

### 步骤 8：配置 Nginx 反向代理（可选）

如果使用 Nginx，创建配置文件：

```bash
sudo nano /etc/nginx/sites-available/restaurant-api
```

内容如下：

```nginx
upstream restaurant_main {
    server 127.0.0.1:8000;
}

upstream restaurant_customer {
    server 127.0.0.1:8001;
}

upstream restaurant_member {
    server 127.0.0.1:8004;
}

upstream restaurant_headquarters {
    server 127.0.0.1:8006;
}

server {
    listen 80;
    server_name api.restaurant.example.com;

    # 主 API
    location /api {
        proxy_pass http://restaurant_main;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 顾客 API
    location /api/orders {
        proxy_pass http://restaurant_customer;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://restaurant_customer;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 会员 API
    location /api/member {
        proxy_pass http://restaurant_member;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 总公司管理 API
    location /api/headquarters {
        proxy_pass http://restaurant_headquarters;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/restaurant-api /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 步骤 9：配置防火墙

```bash
# 允许 HTTP 和 HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 允许 SSH
sudo ufw allow 22/tcp

# 启用防火墙
sudo ufw enable
```

---

## 🌐 前端 Netlify 部署

### 步骤 1：准备配置文件

确保 `netlify-production.toml` 文件存在，并根据实际情况修改 API 地址：

```toml
# 修改 API 地址为你的实际地址
# 从：http://9.128.251.82:8000
# 改为：http://your-api-server.com 或 https://api.your-domain.com
```

### 步骤 2：使用 Git 部署到 Netlify

#### 方式一：通过 GitHub 连接（推荐）

1. **推送到 GitHub**

```bash
# 确保所有更改已提交
git add .
git commit -m "部署生产版本"

# 推送到 GitHub
git push origin main
```

2. **在 Netlify Dashboard 配置**

- 登录 Netlify Dashboard：https://app.netlify.com
- 点击 "Add new site" -> "Import an existing project"
- 选择 "GitHub" 并授权
- 选择你的仓库
- 配置构建设置：
  - **Build command**: `echo "No build needed"`
  - **Publish directory**: `assets`
  - **Branch to deploy**: `main`
- 点击 "Deploy site"

3. **使用生产配置**

部署后，在 Netlify Dashboard 中：
- 进入 Site settings -> Build & deploy -> Post processing
- 或直接将 `netlify-production.toml` 上传到项目根目录并重命名为 `netlify.toml`

#### 方式二：拖拽部署（快速测试）

1. **准备部署包**

```bash
# 在项目根目录创建临时文件夹
mkdir -p deploy/restaurant-frontend

# 复制 assets 文件夹到部署包
cp -r assets deploy/restaurant-frontend/

# 复制生产配置文件
cp netlify-production.toml deploy/restaurant-frontend/netlify.toml
```

2. **拖拽到 Netlify**

- 访问 https://app.netlify.com/drop
- 将 `deploy/restaurant-frontend` 文件夹拖拽到页面中
- 等待部署完成

### 步骤 3：配置域名（可选）

1. 在 Netlify Dashboard 中，进入 "Domain management"
2. 点击 "Add custom domain"
3. 输入你的域名（如：restaurant.example.com）
4. 按照提示配置 DNS 记录：

```
类型: CNAME
名称: @ 或 www
值: your-site-name.netlify.app
```

### 步骤 4：启用 HTTPS

Netlify 自动为所有站点提供 HTTPS 证书，无需额外配置。

---

## 🧪 正式测试

### 1. 后端 API 测试

创建测试脚本 `test_production_apis.py`：

```python
#!/usr/bin/env python3
"""
生产环境 API 测试脚本
"""
import requests
import json

# 修改为实际的生产环境 API 地址
API_BASE_URL = "http://your-api-server.com"
# 或使用 HTTPS
# API_BASE_URL = "https://api.your-domain.com"

def test_api_health():
    """测试 API 健康状态"""
    print("=" * 50)
    print("测试 API 健康状态")
    print("=" * 50)
    
    apis = [
        ("主 API", 8000),
        ("顾客 API", 8001),
        ("会员 API", 8004),
        ("总公司管理 API", 8006)
    ]
    
    for name, port in apis:
        url = f"{API_BASE_URL}:{port}" if port not in API_BASE_URL else API_BASE_URL
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ {name} ({url}): 正常")
            else:
                print(f"✗ {name} ({url}): 状态码 {response.status_code}")
        except Exception as e:
            print(f"✗ {name} ({url}): {str(e)}")

def test_member_api():
    """测试会员 API"""
    print("\n" + "=" * 50)
    print("测试会员 API")
    print("=" * 50)
    
    # 1. 注册会员
    url = f"{API_BASE_URL}:8004/api/member/register"
    response = requests.post(url, json={"phone": "13800138000", "name": "生产测试会员"})
    print(f"注册会员: {response.status_code}")
    
    if response.status_code == 200:
        member = response.json()
        print(f"✓ 会员 ID: {member['id']}")
        
        # 2. 获取会员信息
        url = f"{API_BASE_URL}:8004/api/member/{member['id']}"
        response = requests.get(url)
        print(f"获取会员信息: {response.status_code}")
        
        # 3. 获取订单列表
        url = f"{API_BASE_URL}:8004/api/member/{member['id']}/orders"
        response = requests.get(url)
        print(f"获取订单列表: {response.status_code}")

def test_headquarters_api():
    """测试总公司管理 API"""
    print("\n" + "=" * 50)
    print("测试总公司管理 API")
    print("=" * 50)
    
    # 1. 获取总体统计
    url = f"{API_BASE_URL}:8006/api/headquarters/overall-stats"
    response = requests.get(url)
    print(f"获取总体统计: {response.status_code}")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✓ 总店铺数: {stats['total_stores']}")
        print(f"✓ 总订单数: {stats['total_orders']}")
        print(f"✓ 总营收: {stats['total_revenue']}")
    
    # 2. 获取店铺列表
    url = f"{API_BASE_URL}:8006/api/headquarters/stores"
    response = requests.get(url)
    print(f"获取店铺列表: {response.status_code}")

if __name__ == "__main__":
    test_api_health()
    test_member_api()
    test_headquarters_api()
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
```

运行测试：

```bash
python test_production_apis.py
```

### 2. 前端页面测试

#### 基础功能测试

1. **访问主页**
   - 访问你的 Netlify 站点 URL
   - 检查页面是否正常加载
   - 检查门户页面是否正常显示

2. **测试各功能入口**
   - 顾客端：点击进入，检查是否能正常显示菜单
   - 工作人员端：点击进入，检查登录页面是否正常
   - 店铺设置：点击进入，检查是否能正常访问
   - 菜品管理：点击进入，检查是否能正常显示
   - 物料采购：点击进入，检查是否能正常显示
   - 跨店铺结算：点击进入，检查是否能正常显示
   - **会员中心**：点击进入，检查登录页面是否正常
   - **总公司后台**：点击进入，检查是否能正常加载统计数据

#### 会员中心测试

1. **登录测试**
   - 输入手机号登录
   - 检查是否能成功获取会员信息
   - 检查登录状态是否持久化

2. **会员信息查看**
   - 检查积分、消费金额、订单数是否正确显示
   - 检查会员等级和折扣信息
   - 检查下一等级进度条

3. **订单记录测试**
   - 切换到"订单记录"标签页
   - 检查订单列表是否正常显示
   - 点击订单，检查详情是否正确

4. **积分日志测试**
   - 切换到"积分日志"标签页
   - 检查积分记录是否正常显示

#### 总公司管理后台测试

1. **总体统计测试**
   - 检查各项统计数据是否正确显示
   - 总店铺数、活跃店铺、总订单数、总营收等

2. **营收趋势测试**
   - 检查营收趋势图表是否正常显示
   - 检查折线图和柱状图是否正确

3. **店铺排名测试**
   - 检查店铺营收排名是否正确
   - 检查前10名店铺数据

4. **店铺列表测试**
   - 检查店铺列表是否正常显示
   - 点击"查看详情"，检查是否能正常跳转

5. **员工列表测试**
   - 检查员工列表是否正常显示
   - 检查员工信息是否完整

6. **会员统计测试**
   - 检查会员统计数据
   - 检查新注册会员列表

### 3. 集成测试

1. **完整订单流程测试**
   - 顾客选择桌号
   - 浏览菜单并下单
   - 支付订单
   - 检查订单状态更新
   - 检查会员积分是否增加

2. **会员积分测试**
   - 在会员中心登录
   - 查看积分变化
   - 查看订单记录

3. **总公司数据统计测试**
   - 完成几笔订单后
   - 在总公司后台查看统计数据更新
   - 检查营收趋势图表

### 4. 性能测试

```bash
# 使用 ab 进行压力测试
ab -n 1000 -c 10 https://your-site-name.netlify.app/
```

---

## 📊 监控和维护

### 1. 服务器监控

```bash
# 查看服务状态
sudo systemctl status restaurant-*

# 查看服务日志
sudo journalctl -u restaurant-restaurant-api -f
sudo journalctl -u restaurant-customer-api -f
sudo journalctl -u restaurant-member-api -f
sudo journalctl -u restaurant-headquarters-api -f

# 查看系统资源使用
htop
```

### 2. 数据库备份

创建定期备份脚本：

```bash
sudo nano /opt/restaurant/backup.sh
```

内容如下：

```bash
#!/bin/bash
# 数据库备份脚本

BACKUP_DIR="/opt/restaurant/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/restaurant_db_${DATE}.sql"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 备份数据库
pg_dump -U restaurant_user -h localhost restaurant_db > ${BACKUP_FILE}

# 压缩备份文件
gzip ${BACKUP_FILE}

# 删除7天前的备份
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

设置定时任务：

```bash
chmod +x /opt/restaurant/backup.sh
crontab -e
```

添加每天凌晨2点备份：

```
0 2 * * * /opt/restaurant/backup.sh >> /var/log/restaurant_backup.log 2>&1
```

### 3. 日志管理

配置日志轮转：

```bash
sudo nano /etc/logrotate.d/restaurant
```

内容如下：

```
/opt/restaurant/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload restaurant-* > /dev/null 2>&1 || true
    endscript
}
```

---

## 🔐 安全加固

### 1. 配置防火墙

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

### 2. 配置 fail2ban

```bash
sudo apt install fail2ban -y
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

### 3. 启用 HTTPS（Nginx）

安装 Let's Encrypt：

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.your-domain.com
```

自动续期：

```bash
sudo certbot renew --dry-run
```

---

## 📝 部署检查清单

### 后端部署
- [ ] 服务器软件已安装（Python、PostgreSQL、Git）
- [ ] 数据库已创建并配置
- [ ] 代码已克隆到服务器
- [ ] Python 虚拟环境已创建
- [ ] 依赖已安装
- [ ] 环境变量已配置
- [ ] 数据库已初始化
- [ ] Systemd 服务已创建并启动
- [ ] Nginx 反向代理已配置（如需要）
- [ ] 防火墙已配置
- [ ] API 服务测试通过

### 前端部署
- [ ] Netlify 配置文件已更新（API 地址）
- [ ] 代码已推送到 GitHub
- [ ] Netlify 站点已创建
- [ ] 部署已完成
- [ ] 自定义域名已配置（如需要）
- [ ] HTTPS 已启用

### 测试
- [ ] 后端 API 健康检查通过
- [ ] 会员 API 测试通过
- [ ] 总公司管理 API 测试通过
- [ ] 前端页面访问正常
- [ ] 会员中心功能测试通过
- [ ] 总公司后台功能测试通过
- [ ] 完整订单流程测试通过
- [ ] 性能测试通过

### 监控和维护
- [ ] 服务器监控已配置
- [ ] 数据库备份已配置
- [ ] 日志轮转已配置
- [ ] 安全加固已完成
- [ ] 监控告警已配置（如需要）

---

## ❓ 常见问题

### 1. API 服务无法启动

**问题**：`systemctl status` 显示服务启动失败

**解决**：
```bash
# 查看详细日志
sudo journalctl -u restaurant-restaurant-api -n 50

# 检查端口是否被占用
sudo netstat -tulpn | grep :8000

# 检查配置文件语法
python -m uvicorn api.restaurant_api:app --help
```

### 2. 前端无法访问后端 API

**问题**：浏览器控制台显示 CORS 错误或 404

**解决**：
- 检查 `netlify.toml` 中的 API 地址是否正确
- 检查后端服务器的防火墙是否开放了相应端口
- 检查 Nginx 反向代理配置是否正确
- 确保后端 API 服务正在运行

### 3. 数据库连接失败

**问题**：后端日志显示数据库连接错误

**解决**：
- 检查数据库是否正在运行：`sudo systemctl status postgresql`
- 检查数据库连接字符串是否正确
- 检查数据库用户权限
- 检查防火墙是否开放了数据库端口（5432）

### 4. Netlify 部署失败

**问题**：Netlify 部署显示错误

**解决**：
- 检查 `netlify.toml` 语法是否正确
- 检查 `assets` 目录是否存在
- 查看 Netlify 部署日志
- 确保仓库已正确推送

### 5. 页面加载缓慢

**问题**：前端页面加载速度慢

**解决**：
- 检查图片是否已优化
- 检查 CDN 配置
- 使用 Netlify 提供的 Lighthouse 工具分析性能
- 启用 Netlify 的缓存策略

---

## 🎉 部署完成

恭喜！你已经成功将餐饮点餐系统部署到生产环境。

**下一步建议**：
1. 定期检查系统运行状态
2. 监控服务器资源使用情况
3. 定期备份数据库
4. 收集用户反馈，持续优化系统
5. 根据业务需求进行功能迭代

如有任何问题，请参考技术文档或联系技术支持。
