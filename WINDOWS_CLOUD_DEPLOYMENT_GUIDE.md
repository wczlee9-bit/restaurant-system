# Windows 云服务器部署指南（宝塔面板）

## 📋 服务器信息

- **操作系统**：Windows Server（宝塔面板 8.5.0）
- **配置**：2核/2GB/50GB SSD
- **面板**：宝塔 Windows 面板

---

## 🚀 部署架构

```
Windows 云服务器
├── 宝塔面板（Web 管理）
│   ├── Nginx（反向代理）
│   │   ├── 80 端口 → HTTP
│   │   ├── 443 端口 → HTTPS（可选）
│   │   ├── / → 前端静态文件
│   │   ├── /api/* → 后端 API (8000端口)
│   │   └── /ws/* → WebSocket (8000端口)
│   └── SSL 证书管理
├── 后端服务
│   ├── Python 3.10+
│   ├── FastAPI + Uvicorn
│   └── Windows 服务 / 后台进程
└── PostgreSQL 数据库
    └── 5432 端口
```

---

## 📖 部署步骤

### Step 1: 远程连接 Windows 服务器

#### 方法 1: 使用腾讯云控制台

1. 登录腾讯云控制台
2. 找到你的云服务器实例（lhins-e29vrpmp）
3. 点击 **登录**
4. 选择 **VNC 登录** 或 **远程桌面连接**
5. 输入用户名和密码

#### 方法 2: 使用远程桌面连接（Windows）

1. 按 `Win + R`，输入 `mstsc`
2. 输入服务器 IP 地址
3. 点击连接
4. 输入用户名和密码

#### 方法 3: 使用宝塔面板

1. 在浏览器访问宝塔面板地址（腾讯云控制台会显示）
2. 输入面板用户名和密码
3. 登录后可以直接在 Web 界面操作

---

### Step 2: 在宝塔面板安装必要软件

#### 2.1 登录宝塔面板

1. 在腾讯云控制台找到宝塔面板地址
2. 格式：`http://服务器IP:8888/面板随机ID`
3. 输入用户名和密码登录

#### 2.2 安装 Python

1. 在宝塔面板左侧菜单，点击 **软件商店**
2. 搜索 **Python**
3. 选择 **Python 3.10** 或更高版本
4. 点击 **安装**

#### 2.3 安装 PostgreSQL

1. 在宝塔面板左侧菜单，点击 **软件商店**
2. 搜索 **PostgreSQL**
3. 选择 **PostgreSQL 14** 或更高版本
4. 点击 **安装**
5. 安装后设置数据库密码（记住这个密码！）

#### 2.4 安装 Nginx（如果未安装）

1. 在宝塔面板左侧菜单，点击 **软件商店**
2. 搜索 **Nginx**
3. 选择 **Nginx 1.20+**
4. 点击 **安装**

---

### Step 3: 下载项目代码

#### 3.1 在服务器上打开 PowerShell

1. 按 `Win + X`，选择 **Windows PowerShell** 或 **终端**
2. 切换到项目目录：

```powershell
# 创建项目目录
cd C:\
mkdir restaurant-system
cd C:\restaurant-system

# 如果有 Git，克隆仓库
git clone https://github.com/wczlee9-bit/restaurant-system.git

# 或者直接下载 ZIP 文件解压
```

#### 3.2 备选方案：直接下载 ZIP

1. 在服务器上打开浏览器
2. 访问：`https://github.com/wczlee9-bit/restaurant-system`
3. 点击 **Code** → **Download ZIP**
4. 下载后解压到 `C:\restaurant-system\`

---

### Step 4: 配置数据库

#### 4.1 创建数据库

在宝塔面板操作：

1. 点击左侧菜单 **数据库** → **PostgreSQL**
2. 点击 **创建数据库**
3. 设置：
   - 数据库名：`restaurant_system`
   - 用户名：`restaurant_user`
   - 密码：设置一个强密码
   - 编码：`UTF-8`

#### 4.2 初始化数据库表结构

在 PowerShell 中执行：

```powershell
cd C:\restaurant-system\restaurant-system

# 安装 Python 依赖
pip install -r requirements.txt

# 设置环境变量
$env:PGDATABASE_URL = "postgresql://restaurant_user:你的密码@localhost:5432/restaurant_system"

# 初始化数据库
python src/storage/database/init_db.py
```

#### 4.3 验证数据库

```powershell
# 测试数据库连接
python -c "import os; os.environ['PGDATABASE_URL']='postgresql://restaurant_user:你的密码@localhost:5432/restaurant_system'; from sqlalchemy import create_engine, text; engine = create_engine(os.environ['PGDATABASE_URL']); print(engine.connect().execute(text('SELECT COUNT(*) FROM menu_items')).scalar())"

# 应该返回：60
```

---

### Step 5: 部署后端服务

#### 5.1 创建启动脚本

创建文件 `C:\restaurant-system\start_backend.bat`：

```batch
@echo off
chcp 65001
cd /d C:\restaurant-system\restaurant-system

set PGDATABASE_URL=postgresql://restaurant_user:你的密码@localhost:5432/restaurant_system

echo Starting backend service...
python -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000

pause
```

#### 5.2 配置 Windows 服务（可选，推荐）

使用 NSSM (Non-Sucking Service Manager) 将后端注册为 Windows 服务：

```powershell
# 下载 NSSM
# https://nssm.cc/download

# 下载后解压，安装为服务
cd C:\nssm
.\nssm install RestaurantBackend

# 配置服务
Path: C:\Python310\python.exe
Startup directory: C:\restaurant-system\restaurant-system
Arguments: -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000

# 启动服务
nssm start RestaurantBackend

# 设置自动启动
nssm set RestaurantBackend Start SERVICE_AUTO_START
```

#### 5.3 测试后端服务

```powershell
# 启动后端（如果未注册为服务）
cd C:\restaurant-system\restaurant-system
start_backend.bat

# 或直接运行
python -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000
```

#### 5.4 验证后端运行

打开浏览器访问：
```
http://localhost:8000/health
```

应该返回：
```json
{
  "status": "ok",
  "message": "餐饮系统API服务运行正常",
  ...
}
```

---

### Step 6: 部署前端文件

#### 6.1 在宝塔面板创建站点

1. 点击左侧菜单 **网站**
2. 点击 **添加站点**
3. 设置：
   - 域名：服务器 IP（如果有域名，填写域名）
   - 根目录：`C:/wwwroot/restaurant`
   - PHP 版本：纯静态
4. 点击 **提交**

#### 6.2 复制前端文件

```powershell
# 复制前端文件到宝塔网站目录
Copy-Item -Path "C:\restaurant-system\restaurant-system\assets\*" -Destination "C:\wwwroot\restaurant\" -Recurse -Force
```

#### 6.3 验证前端文件

在宝塔面板：
1. 点击左侧菜单 **文件**
2. 进入 `C:\wwwroot\restaurant`
3. 确认能看到所有前端文件（*.html 等）

---

### Step 7: 配置 Nginx 反向代理

#### 7.1 在宝塔面板配置 Nginx

1. 点击左侧菜单 **网站** → **站点设置**（你的站点）
2. 点击 **配置文件**
3. 修改 Nginx 配置：

```nginx
server {
    listen 80;
    server_name 你的域名或IP;

    root C:/wwwroot/restaurant;
    index index.html portal.html;

    # 前端静态文件
    location / {
        try_files $uri $uri/ /portal.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket 代理
    location /ws/ {
        proxy_pass http://127.0.0.1:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 健康检查端点
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. 点击 **保存**
5. 点击 **重载配置**

---

### Step 8: 配置 SSL 证书（可选但推荐）

#### 8.1 申请免费 SSL 证书（Let's Encrypt）

1. 在宝塔面板，点击 **网站** → **站点设置**
2. 点击 **SSL**
3. 选择 **Let's Encrypt**
4. 输入你的域名（需要已解析到服务器 IP）
5. 点击 **申请**

#### 8.2 强制 HTTPS

1. 在 SSL 设置页面
2. 开启 **强制 HTTPS**
3. Nginx 会自动添加 HTTPS 配置

---

### Step 9: 验证部署

#### 9.1 测试前端

打开浏览器访问：
```
http://你的服务器IP/
```

应该能看到门户页面。

#### 9.2 测试点餐功能

访问：
```
http://你的服务器IP/customer_order_v3.html
```

输入桌号，应该能看到菜品列表。

#### 9.3 测试 API

访问：
```
http://你的服务器IP/api/health
```

应该返回后端健康状态。

#### 9.4 检查服务状态

在宝塔面板：
1. 点击左侧菜单 **软件商店** → **运行环境**
2. 查看 PostgreSQL 运行状态
3. 查看 Nginx 运行状态

---

## 🔧 常用操作

### 重启后端服务

```powershell
# 如果使用 NSSM 注册的服务
nssm restart RestaurantBackend

# 或者手动启动
cd C:\restaurant-system\restaurant-system
start_backend.bat
```

### 查看后端日志

```powershell
# 日志文件位置
type C:\restaurant-system\restaurant-system\logs\api.log

# 或者实时查看
Get-Content C:\restaurant-system\restaurant-system\logs\api.log -Wait
```

### 重启 Nginx

在宝塔面板：
1. 点击左侧菜单 **软件商店**
2. 找到 Nginx
3. 点击 **重启**

### 重新初始化数据库

```powershell
cd C:\restaurant-system\restaurant-system
set PGDATABASE_URL=postgresql://restaurant_user:你的密码@localhost:5432/restaurant_system
python src/storage/database/init_db.py
```

---

## 📊 性能优化建议

### 1. 开启 Gzip 压缩

在 Nginx 配置中添加：

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

### 2. 配置静态文件缓存

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 3. 数据库连接池优化

修改 `src/storage/database/db.py`：

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # 连接池大小
    max_overflow=20,     # 最大溢出连接数
    pool_pre_ping=True,  # 连接前检查
    echo=False
)
```

---

## 🔒 安全建议

### 1. 配置防火墙

在宝塔面板：
1. 点击左侧菜单 **安全**
2. 只开放必要端口：
   - 80 (HTTP)
   - 443 (HTTPS)
   - 22 (SSH，如果需要)
   - 8888 (宝塔面板，可以限制 IP 访问)

### 2. 修改宝塔面板端口

1. 点击左侧菜单 **面板设置**
2. 修改面板端口
3. 记住新端口

### 3. 设置数据库强密码

确保 PostgreSQL 数据库密码足够复杂。

### 4. 定期备份数据库

在宝塔面板：
1. 点击左侧菜单 **数据库**
2. 设置自动备份计划

---

## ❓ 常见问题

### Q1: 后端服务无法启动

**解决方法**：
1. 检查 Python 版本（需要 3.10+）
2. 检查依赖是否安装完整
3. 检查数据库连接配置
4. 查看错误日志

### Q2: 前端页面无法访问

**解决方法**：
1. 检查 Nginx 是否运行
2. 检查站点配置是否正确
3. 检查文件路径是否正确

### Q3: API 请求失败

**解决方法**：
1. 检查后端服务是否运行
2. 检查 Nginx 代理配置
3. 检查防火墙设置

### Q4: 数据库连接失败

**解决方法**：
1. 检查 PostgreSQL 服务是否运行
2. 检查用户名和密码
3. 检查数据库是否存在

---

## 📚 相关文档

- [宝塔面板使用指南](https://www.bt.cn/bbs/thread-19376-1-1.html)
- [PostgreSQL Windows 安装](https://www.postgresql.org/download/windows/)
- [Nginx 配置文档](https://nginx.org/en/docs/)

---

## 💡 下一步

部署完成后，你可以：
1. 测试所有功能模块
2. 创建管理员账号
3. 配置店铺和菜品
4. 配置会员规则
5. 开始正式使用

---

**需要帮助？**
- 查看宝塔面板日志
- 查看后端日志文件
- 联系技术支持
