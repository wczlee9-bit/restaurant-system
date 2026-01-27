# Linux 云服务器部署工具包

本工具包包含在 Linux 云服务器（Ubuntu 22.04 + 宝塔 Linux 面板）上部署餐饮系统的自动化脚本和配置文件。

---

## 📋 系统要求

### 最低配置

```
CPU: 2核
内存: 2GB（推荐 4GB）
硬盘: 40GB SSD（推荐 50GB）
操作系统: Ubuntu 22.04 LTS
带宽: 1TB/月 流量包
```

### 推荐配置

```
CPU: 2核
内存: 4GB
硬盘: 50GB SSD
操作系统: Ubuntu 22.04 LTS
带宽: 1TB/月 流量包
```

---

## 🚀 快速开始（3 步完成）

### Step 1: SSH 连接到服务器

```bash
ssh root@你的服务器IP
```

### Step 2: 下载并运行部署脚本

```bash
# 下载脚本
wget https://raw.githubusercontent.com/wczlee9-bit/restaurant-system/main/deploy_linux/quick_deploy.sh

# 运行脚本
sudo bash quick_deploy.sh
```

### Step 3: 访问系统

部署完成后，访问：
```
http://你的服务器IP/
http://你的服务器IP/customer_order_v3.html
```

---

## 📋 部署步骤详解

### 脚本会自动完成以下操作：

1. **更新系统**
   - 更新 apt 包索引
   - 升级已安装的软件包

2. **安装必要软件**
   - Python 3.10+
   - PostgreSQL 14+
   - Nginx
   - Git
   - 宝塔 Linux 面板（如果未安装）

3. **创建项目目录**
   - 创建 `/www/wwwroot/restaurant-system`
   - 设置权限

4. **克隆项目代码**
   - 从 GitHub 克隆最新代码
   - 或更新已有代码

5. **安装 Python 依赖**
   - 创建虚拟环境
   - 安装 FastAPI、Uvicorn、SQLAlchemy 等

6. **配置数据库**
   - 创建 PostgreSQL 数据库
   - 创建数据库用户
   - 初始化数据库表结构
   - 插入初始数据（60个菜品，43个桌号）

7. **配置后端服务**
   - 创建 systemd 服务文件
   - 启动后端服务
   - 设置开机自启

8. **配置 Nginx**
   - 创建 Nginx 配置文件
   - 配置反向代理
   - 配置 WebSocket 代理
   - 重启 Nginx

---

## 🎯 部署架构

```
Linux 服务器
├── 宝塔 Linux 面板（端口 8888）
│   ├── Nginx（端口 80/443）
│   │   ├── / → 前端静态文件
│   │   ├── /api/* → 后端 API (端口 8000)
│   │   └── /ws/* → WebSocket (端口 8000)
│   └── SSL 证书管理
├── 后端服务
│   ├── FastAPI + Uvicorn
│   ├── 端口 8000
│   └── systemd 管理
└── PostgreSQL 数据库
    ├── 端口 5432
    ├── 数据库: restaurant_system
    └── 初始数据已加载
```

---

## 🔧 常用命令

### 查看服务状态

```bash
# 查看后端服务状态
systemctl status restaurant-backend

# 查看 Nginx 状态
systemctl status nginx

# 查看 PostgreSQL 状态
systemctl status postgresql
```

### 重启服务

```bash
# 重启后端服务
systemctl restart restaurant-backend

# 重启 Nginx
systemctl restart nginx

# 重启 PostgreSQL
systemctl restart postgresql
```

### 查看日志

```bash
# 查看后端日志（实时）
journalctl -u restaurant-backend -f

# 查看后端日志（最近 50 行）
journalctl -u restaurant-backend -n 50

# 查看 Nginx 日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 查看 PostgreSQL 日志
tail -f /var/log/postgresql/postgresql-14-main.log
```

### 更新代码

```bash
cd /www/wwwroot/restaurant-system
git pull origin main
systemctl restart restaurant-backend
```

---

## 🔐 数据库信息

部署脚本会自动生成以下信息：

```
数据库名: restaurant_system
数据库用户: restaurant_user
数据库密码: 自动生成（保存此密码！）
```

**重要**：部署完成后，请保存数据库密码，后续可能需要。

### 手动访问数据库

```bash
# 连接到数据库
sudo -u postgres psql -d restaurant_system

# 退出
\q
```

---

## 🌐 访问地址

部署完成后，可以通过以下地址访问：

```
http://你的服务器IP/                    # 主页（自动跳转到 portal.html）
http://你的服务器IP/portal.html          # 门户页面
http://你的服务器IP/customer_order_v3.html  # 点餐页面
http://你的服务器IP/login.html           # 登录页面
http://你的服务器IP/docs                 # API 文档
http://你的服务器IP/health               # 健康检查
```

---

## 🔒 配置 SSL 证书（可选）

### 方法 1: 使用宝塔面板

1. 访问宝塔面板：`http://你的服务器IP:8888/`

2. 点击 **网站** → **你的站点** → **SSL**

3. 选择 **Let's Encrypt**

4. 申请免费 SSL 证书

5. 启用 **强制 HTTPS**

### 方法 2: 使用 Certbot

```bash
# 安装 Certbot
apt-get install certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d 你的域名

# 自动续期
certbot renew --dry-run
```

---

## 📊 性能优化

### 1. 开启 Nginx Gzip 压缩

在 `/etc/nginx/nginx.conf` 中添加：

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

### 2. 配置 PostgreSQL 连接池

修改数据库连接配置：

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False
)
```

### 3. 启用 Nginx 缓存

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|webp|svg|woff|woff2|ttf|eot)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
    access_log off;
}
```

---

## 🔍 故障排查

### 问题 1: 后端服务无法启动

**检查日志**：
```bash
journalctl -u restaurant-backend -n 50
```

**常见原因**：
- 端口 8000 被占用
- 数据库连接失败
- Python 依赖未安装

**解决方法**：
```bash
# 检查端口占用
netstat -tlnp | grep 8000

# 手动测试启动
cd /www/wwwroot/restaurant-system
source venv/bin/activate
python -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000
```

### 问题 2: 前端页面无法访问

**检查 Nginx**：
```bash
systemctl status nginx
nginx -t
```

**检查文件权限**：
```bash
ls -la /www/wwwroot/restaurant-system/assets/
```

### 问题 3: 数据库连接失败

**检查 PostgreSQL**：
```bash
systemctl status postgresql
sudo -u postgres psql -d restaurant_system
```

**检查环境变量**：
```bash
echo $PGDATABASE_URL
```

---

## 📚 相关文档

- [宝塔 Linux 面板文档](https://www.bt.cn/new/index.html)
- [Nginx 文档](https://nginx.org/en/docs/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)

---

## 💡 提示

1. **定期备份数据库**
   ```bash
   pg_dump -U restaurant_user restaurant_system > backup.sql
   ```

2. **监控系统资源**
   - CPU 使用率
   - 内存使用率
   - 磁盘空间

3. **定期更新系统**
   ```bash
   apt-get update && apt-get upgrade
   ```

4. **定期更新代码**
   ```bash
   cd /www/wwwroot/restaurant-system
   git pull origin main
   systemctl restart restaurant-backend
   ```

---

## 🆘 需要帮助？

- 查看日志：`journalctl -u restaurant-backend -f`
- 查看宝塔面板：`http://你的服务器IP:8888/`
- 联系技术支持

---

**版本**: v2.0.0
**更新时间**: 2025-01-12
