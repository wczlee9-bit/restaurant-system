# 🚀 完整部署指南 - 从沙盒到腾讯云

## 📋 部署流程概览

```
沙盒环境 (Workspace)
    ↓ git push
GitHub (wczlee9-bit/restaurant-system) ✅ 已完成
    ↓ 手动/自动同步
Gitee (lijun75/restaurant) ⏳ 待执行
    ↓ 使用部署脚本
腾讯云服务器 (129.226.196.76) ⏳ 待执行
```

## ✅ 已完成的工作

### 1. 代码已推送到 GitHub

- 仓库: https://github.com/wczlee9-bit/restaurant-system
- 状态: ✅ 已推送
- 提交: 包含所有模块化架构代码和部署脚本

### 2. 部署包已创建

- 文件名: `restaurant-deployment-20260206-232701.tar.gz`
- 大小: 33M
- 内容: 源代码 + 部署脚本 + 文档

### 3. 部署脚本已准备

- `deploy_all_in_one.sh` - 腾讯云一键部署脚本
- `create_deployment_package.sh` - 部署包生成脚本

---

## 🎯 下一步：推送到 Gitee

### 方法 1：使用命令行推送

```bash
# 1. 添加 Gitee remote
git remote add gitee https://gitee.com/lijun75/restaurant.git

# 2. 推送到 Gitee
git push gitee main

# 如果需要输入密码，使用 Personal Access Token
```

### 方法 2：使用 Personal Access Token

如果遇到认证问题：

1. **获取 Token**：
   - 访问：https://gitee.com/profile/personal_access_tokens
   - 创建新 Token
   - 选择权限：`projects`（读写权限）
   - 复制 Token

2. **使用 Token 推送**：
```bash
# 使用 URL + Token 方式
git remote set-url gitee https://<your-token>@gitee.com/lijun75/restaurant.git

# 推送
git push gitee main
```

### 方法 3：手动上传

如果无法使用 Git 命令：

1. 访问 Gitee 仓库：https://gitee.com/lijun75/restaurant
2. 点击"上传文件"或"导入仓库"
3. 上传所有项目文件

---

## 🚀 从 Gitee 部署到腾讯云

### 方案 1：使用一键部署脚本（推荐）

#### 步骤 1：上传部署包到腾讯云

```bash
# 在本地执行
scp restaurant-deployment-20260206-232701.tar.gz root@129.226.196.76:/tmp/
```

#### 步骤 2：连接到腾讯云

```bash
ssh root@129.226.196.76
```

#### 步骤 3：解压并部署

```bash
# 解压部署包
cd /tmp
tar -xzf restaurant-deployment-20260206-232701.tar.gz
cd deployment_package_temp

# 运行一键部署脚本
bash deploy_all_in_one.sh
```

#### 步骤 4：验证部署

```bash
# 检查服务状态
systemctl status restaurant

# 测试 API
curl http://localhost:8000/health

# 查看日志
journalctl -u restaurant -f
```

### 方案 2：直接从 Gitee 部署

#### 步骤 1：连接到腾讯云

```bash
ssh root@129.226.196.76
```

#### 步骤 2：下载部署脚本

```bash
# 创建临时目录
mkdir -p /tmp/restaurant-deploy
cd /tmp/restaurant-deploy

# 下载部署脚本
wget https://gitee.com/lijun75/restaurant/raw/main/deploy_all_in_one.sh
chmod +x deploy_all_in_one.sh
```

#### 步骤 3：运行部署脚本

```bash
bash deploy_all_in_one.sh
```

### 方案 3：手动部署

#### 步骤 1：克隆代码

```bash
# 连接到腾讯云
ssh root@129.226.196.76

# 备份现有系统
cd /opt
cp -r restaurant-system restaurant-system-backup-$(date +%Y%m%d)

# 克隆新代码
cd /opt
rm -rf restaurant-system
git clone https://gitee.com/lijun75/restaurant.git restaurant-system
cd restaurant-system
```

#### 步骤 2：安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

#### 步骤 3：测试模块

```bash
# 运行模块测试
python test_module_loader.py
```

#### 步骤 4：配置服务

```bash
# 创建 systemd 服务
cat > /etc/systemd/system/restaurant.service << 'EOF'
[Unit]
Description=Restaurant System
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/restaurant-system
Environment="PATH=/opt/restaurant-system/venv/bin"
ExecStart=/opt/restaurant-system/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重载 systemd
systemctl daemon-reload
```

#### 步骤 5：启动服务

```bash
# 启动服务
systemctl start restaurant

# 启用开机自启
systemctl enable restaurant

# 检查状态
systemctl status restaurant
```

#### 步骤 6：配置 Nginx

```bash
# 创建 Nginx 配置
cat > /etc/nginx/sites-available/restaurant << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/restaurant /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试配置
nginx -t

# 重启 Nginx
systemctl restart nginx
```

---

## 🔧 部署脚本说明

### deploy_all_in_one.sh

**功能**：
- 环境检查（系统、依赖、数据库）
- 自动备份现有系统
- 从 Gitee 克隆最新代码
- 安装 Python 依赖
- 初始化数据库
- 测试模块加载器
- 配置 systemd 服务
- 启动服务
- 配置 Nginx
- 验证部署

**配置选项**：
```bash
export GITEE_REPO="https://gitee.com/lijun75/restaurant.git"
export PROJECT_DIR="/opt/restaurant-system"
export DB_USER="postgres"
export DB_NAME="restaurant_db"
export PYTHON_VERSION="3.10"
```

### create_deployment_package.sh

**功能**：
- 打包项目源代码
- 复制部署脚本
- 生成部署说明文档
- 创建快速部署脚本
- 打包成 .tar.gz 文件

---

## ✅ 部署验证

### 1. 检查服务状态

```bash
systemctl status restaurant
```

### 2. 测试 API

```bash
# 健康检查
curl http://localhost:8000/health

# 获取菜单
curl http://localhost:8000/api/menu

# 查看订单
curl http://localhost:8000/api/orders
```

### 3. 检查日志

```bash
# 服务日志
journalctl -u restaurant -f

# Nginx 日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 4. 访问系统

- 后端 API: http://129.226.196.76
- 健康检查: http://129.226.196.76/health

---

## 🔄 更新系统

### 自动更新

```bash
# 运行一键部署脚本（自动拉取最新代码）
bash deploy_all_in_one.sh
```

### 手动更新

```bash
# 连接到服务器
ssh root@129.226.196.76

# 拉取最新代码
cd /opt/restaurant-system
git pull

# 重启服务
systemctl restart restaurant
```

---

## 🆘 故障排除

### 问题 1：服务启动失败

```bash
# 查看详细日志
journalctl -u restaurant -n 50 --no-pager

# 手动启动测试
cd /opt/restaurant-system
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 问题 2：数据库连接失败

```bash
# 检查 PostgreSQL 状态
systemctl status postgresql

# 检查数据库是否存在
sudo -u postgres psql -l

# 查看数据库日志
tail -f /var/log/postgresql/*.log
```

### 问题 3：模块加载失败

```bash
# 运行模块测试
cd /opt/restaurant-system
source venv/bin/activate
python test_module_loader.py
```

### 问题 4：Nginx 配置错误

```bash
# 测试 Nginx 配置
nginx -t

# 查看 Nginx 错误日志
tail -f /var/log/nginx/error.log
```

---

## 📊 部署清单

### 推送到 Gitee

- [ ] 代码已推送到 GitHub ✅
- [ ] 添加 Gitee remote
- [ ] 推送到 Gitee
- [ ] 验证 Gitee 仓库内容

### 部署到腾讯云

- [ ] 上传部署包或克隆代码
- [ ] 运行部署脚本
- [ ] 服务启动成功
- [ ] API 测试通过
- [ ] Nginx 配置完成
- [ ] 访问系统正常

---

## 📞 技术支持

### 相关链接

- GitHub: https://github.com/wczlee9-bit/restaurant-system
- Gitee: https://gitee.com/lijun75/restaurant
- 腾讯云: http://129.226.196.76

### 查看文档

- `DEPLOYMENT_README.md` - 部署说明（在部署包中）
- `PUSH_TO_GITEE_GUIDE.md` - 推送指南
- `MODULAR_ARCHITECTURE_QUICKSTART.md` - 快速开始
- `GITEE_COMPLETION_REPORT.md` - 完成报告

---

## 🎉 部署成功后

恭喜！您的餐厅系统已成功部署到腾讯云！

### 可以开始使用的功能

- ✅ 扫码点餐
- ✅ 订单管理
- ✅ 库存管理
- ✅ 会员系统
- ✅ 营收分析
- ✅ 实时通信
- ✅ 小票打印

### 管理命令

```bash
# 查看状态
systemctl status restaurant

# 查看日志
journalctl -u restaurant -f

# 重启服务
systemctl restart restaurant

# 停止服务
systemctl stop restaurant
```

---

**祝您部署成功！** 🚀

---

**最后更新**: 2024-02-06
