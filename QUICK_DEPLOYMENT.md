# 🚀 快速部署指南 - 10 分钟完成部署

本指南帮助你在 10 分钟内完成餐饮点餐系统的部署。

---

## 📌 部署准备

### 需要的资源和信息
- ✅ 一台 Linux 服务器（已有 IP：9.128.251.82）
- ✅ PostgreSQL 数据库
- ✅ S3 兼容的对象存储
- ✅ Netlify 账户（免费）
- ✅ GitHub 账户（可选）

---

## 🎯 部署步骤

### 第 1 步：后端部署（5 分钟）

#### 1.1 连接到服务器

```bash
ssh root@9.128.251.82
```

#### 1.2 安装必要软件

```bash
# 更新系统
apt update && apt upgrade -y

# 安装 Python 和 pip
apt install python3 python3-pip python3-venv git -y

# 安装 PostgreSQL
apt install postgresql postgresql-contrib -y
```

#### 1.3 配置数据库

```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 创建数据库和用户（修改密码）
CREATE DATABASE restaurant_db;
CREATE USER restaurant_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE restaurant_db TO restaurant_user;
\q
```

#### 1.4 克隆代码

```bash
# 创建项目目录
mkdir -p /opt/restaurant
cd /opt/restaurant

# 克隆代码（替换为你的仓库地址）
git clone https://github.com/your-username/restaurant-system.git
cd restaurant-system
```

#### 1.5 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

#### 1.6 配置环境变量

```bash
# 创建 .env 文件
cat > .env << EOF
DATABASE_URL=postgresql://restaurant_user:your_secure_password@localhost:5432/restaurant_db
EOF
```

#### 1.7 初始化数据库

```bash
# 初始化数据库表
python scripts/init_database.py

# 创建测试数据
python scripts/init_test_data_full.py
```

#### 1.8 启动所有 API 服务

```bash
# 方式一：使用启动脚本（推荐）
python scripts/start_api_services.py

# 方式二：手动启动各个服务
# 主 API (端口 8000)
python -m uvicorn api.restaurant_api:app --host 0.0.0.0 --port 8000 &

# 顾客 API (端口 8001)
python -m uvicorn api.customer_api:app --host 0.0.0.0 --port 8001 &

# 会员 API (端口 8004)
python -m uvicorn api.member_api:app --host 0.0.0.0 --port 8004 &

# 总公司管理 API (端口 8006)
python -m uvicorn api.headquarters_api:app --host 0.0.0.0 --port 8006 &
```

#### 1.9 验证后端部署

```bash
# 测试各个 API
curl http://localhost:8000/
curl http://localhost:8001/
curl http://localhost:8004/
curl http://localhost:8006/
```

### 第 2 步：前端部署到 Netlify（3 分钟）

#### 2.1 更新配置文件

在项目根目录，编辑 `netlify-production.toml`，将 API 地址改为你的服务器地址：

```toml
# 将 9.128.251.82 改为你的服务器 IP 或域名
[[redirects]]
  from = "/api/member*"
  to = "http://9.128.251.82:8004/api/member:splat"
  status = 200
  force = true

[[redirects]]
  from = "/api/headquarters*"
  to = "http://9.128.251.82:8006/api/headquarters:splat"
  status = 200
  force = true

[[redirects]]
  from = "/api/orders*"
  to = "http://9.128.251.82:8001/api/orders:splat"
  status = 200
  force = true

[[redirects]]
  from = "/api/*"
  to = "http://9.128.251.82:8000/api/:splat"
  status = 200
  force = true
```

#### 2.2 推送代码到 GitHub

```bash
# 在本地开发环境
git add .
git commit -m "部署生产版本"
git push origin main
```

#### 2.3 在 Netlify 创建站点

1. 访问 https://app.netlify.com
2. 点击 "Add new site" -> "Import an existing project"
3. 选择 "GitHub" 并授权
4. 选择你的仓库
5. 配置构建设置：
   - **Build command**: `echo "No build needed"`
   - **Publish directory**: `assets`
   - **Branch to deploy**: `main`
6. 点击 "Deploy site"

#### 2.4 等待部署完成

部署通常需要 1-2 分钟，完成后你会得到一个类似这样的 URL：
`https://your-site-name.netlify.app`

### 第 3 步：配置 Netlify（2 分钟）

#### 3.1 上传生产配置

在 Netlify Dashboard 中：

1. 进入 Site settings
2. 点击 "Build & deploy" -> "Environment"
3. 或直接在 GitHub 中将 `netlify-production.toml` 重命名为 `netlify.toml`
4. 重新触发部署

#### 3.2 配置自定义域名（可选）

1. 进入 Domain management
2. 点击 "Add custom domain"
3. 输入你的域名（如：restaurant.example.com）
4. 按照提示配置 DNS

---

## 🧪 快速测试

### 测试后端 API

```bash
# 在服务器上运行
curl http://9.128.251.82:8000/api/member/levels
curl http://9.128.251.82:8006/api/headquarters/overall-stats
```

### 测试前端页面

1. 访问你的 Netlify URL（如：`https://your-site-name.netlify.app`）
2. 检查门户页面是否正常显示
3. 点击"会员中心"，检查是否能正常加载
4. 点击"总公司后台"，检查统计数据是否正常显示

### 运行验证脚本

```bash
# 在服务器上运行
chmod +x scripts/verify_deployment.sh
FRONTEND_URL="https://your-site-name.netlify.app" ./scripts/verify_deployment.sh
```

---

## 🎉 部署完成！

### 访问地址

- **前端门户**: https://your-site-name.netlify.app
- **会员中心**: https://your-site-name.netlify.app/member_center.html
- **总公司后台**: https://your-site-name.netlify.app/headquarters_dashboard.html
- **后端 API**: http://9.128.251.82:8000 (主 API)

### 后续操作

1. **配置域名**：在 Netlify 中添加自定义域名
2. **配置 HTTPS**：Netlify 自动提供 HTTPS
3. **设置监控**：配置服务器监控和告警
4. **定期备份**：配置数据库自动备份

### 常见问题

#### Q1: 后端服务启动失败

```bash
# 查看详细错误日志
journalctl -u uvicorn -f

# 检查端口是否被占用
netstat -tulpn | grep -E '8000|8001|8004|8006'
```

#### Q2: 前端无法连接后端

- 检查 `netlify.toml` 中的 API 地址是否正确
- 检查服务器防火墙是否开放了端口
- 检查后端服务是否正在运行

#### Q3: 数据库连接失败

```bash
# 测试数据库连接
psql -U restaurant_user -h localhost -d restaurant_db

# 检查 PostgreSQL 状态
systemctl status postgresql
```

---

## 📞 获取帮助

如遇到问题，请：
1. 查看 `DEPLOYMENT_GUIDE.md` 获取详细的部署文档
2. 检查服务器日志：`journalctl -u uvicorn -f`
3. 检查 Netlify 部署日志
4. 联系技术支持

---

## ✅ 检查清单

部署完成后，请确认：

- [ ] 后端所有 API 服务正在运行
- [ ] 前端页面可以正常访问
- [ ] 会员中心可以正常登录
- [ ] 总公司后台可以正常加载统计数据
- [ ] 顾客可以正常点餐
- [ ] 订单可以正常流转
- [ ] 会员积分可以正常累计
- [ ] 数据库备份已配置
- [ ] 监控告警已配置

---

祝部署顺利！🎊
