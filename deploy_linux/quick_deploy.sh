#!/bin/bash
#
# 餐饮系统 - Linux 服务器一键部署脚本
# 适用于 Ubuntu 22.04 LTS + 宝塔 Linux 面板
#

set -e

echo "========================================"
echo "餐饮系统 - Linux 服务器一键部署"
echo "========================================"
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo "请使用 root 用户运行此脚本"
    echo "使用命令: sudo bash quick_deploy.sh"
    exit 1
fi

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="restaurant-system"
GITHUB_REPO="https://github.com/wczlee9-bit/restaurant-system.git"
INSTALL_DIR="/www/wwwroot/$PROJECT_NAME"
PYTHON_VERSION="3.10"
DB_NAME="restaurant_system"
DB_USER="restaurant_user"
DB_PASS=$(openssl rand -base64 16)
BACKEND_PORT=8000

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署配置${NC}"
echo -e "${GREEN}========================================${NC}"
echo "项目目录: $INSTALL_DIR"
echo "Python 版本: $PYTHON_VERSION"
echo "数据库名: $DB_NAME"
echo "数据库用户: $DB_USER"
echo "数据库密码: $DB_PASS"
echo "后端端口: $BACKEND_PORT"
echo ""
echo -e "${YELLOW}请保存以下信息:${NC}"
echo "数据库密码: $DB_PASS"
echo ""
read -p "按回车键继续..."
echo ""

# Step 1: 更新系统
echo -e "${GREEN}Step 1/8: 更新系统...${NC}"
apt-get update -y
apt-get upgrade -y
echo "✅ 系统更新完成"
echo ""

# Step 2: 安装必要软件
echo -e "${GREEN}Step 2/8: 安装必要软件...${NC}"
apt-get install -y python3 python3-pip python3-venv git nginx postgresql postgresql-contrib

# 检查宝塔面板是否已安装
if [ -f /www/server/panel/class/common.py ]; then
    echo "✅ 宝塔面板已安装"
else
    echo -e "${YELLOW}宝塔面板未安装，开始安装...${NC}"
    wget -O install.sh https://download.bt.cn/install/install-ubuntu_6.0.sh
    bash install.sh y
    echo "✅ 宝塔面板安装完成"
    echo -e "${YELLOW}请查看宝塔面板地址和密码${NC}"
fi
echo ""

# Step 3: 创建项目目录
echo -e "${GREEN}Step 3/8: 创建项目目录...${NC}"
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR
echo "✅ 项目目录创建完成: $INSTALL_DIR"
echo ""

# Step 4: 克隆项目代码
echo -e "${GREEN}Step 4/8: 克隆项目代码...${NC}"
if [ -d ".git" ]; then
    echo "项目已存在，拉取最新代码..."
    git pull origin main
else
    echo "克隆项目代码..."
    git clone $GITHUB_REPO .
fi
echo "✅ 项目代码下载完成"
echo ""

# Step 5: 安装 Python 依赖
echo -e "${GREEN}Step 5/8: 安装 Python 依赖...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-multipart pillow python-dotenv qrcode requests
pip install pandas openpyxl xlsxwriter
pip install passlib[bcrypt] python-jose[cryptography]
pip install httpx websockets
echo "✅ Python 依赖安装完成"
echo ""

# Step 6: 配置数据库
echo -e "${GREEN}Step 6/8: 配置数据库...${NC}"

# 启动 PostgreSQL 服务
systemctl start postgresql
systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\q
EOF

# 设置环境变量
export PGDATABASE_URL="postgresql://$DB_USER:$DB_PASS@localhost/$DB_NAME"
echo "export PGDATABASE_URL=$PGDATABASE_URL" >> ~/.bashrc

# 初始化数据库
source venv/bin/activate
python src/storage/database/init_db.py

echo "✅ 数据库配置完成"
echo "数据库连接字符串: $PGDATABASE_URL"
echo ""

# Step 7: 配置后端服务
echo -e "${GREEN}Step 7/8: 配置后端服务...${NC}"

# 创建 systemd 服务文件
cat > /etc/systemd/system/restaurant-backend.service << EOF
[Unit]
Description=Restaurant Backend Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
Environment="PGDATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost/$DB_NAME"
ExecStart=$INSTALL_DIR/venv/bin/uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port $BACKEND_PORT
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动后端服务
systemctl daemon-reload
systemctl enable restaurant-backend
systemctl start restaurant-backend

# 检查后端服务状态
sleep 3
if systemctl is-active --quiet restaurant-backend; then
    echo "✅ 后端服务启动成功"
else
    echo "❌ 后端服务启动失败"
    echo "查看日志: journalctl -u restaurant-backend -n 50"
fi
echo ""

# Step 8: 配置 Nginx
echo -e "${GREEN}Step 8/8: 配置 Nginx...${NC}"

# 创建 Nginx 配置文件
cat > /etc/nginx/sites-available/restaurant << EOF
server {
    listen 80;
    server_name _;

    root $INSTALL_DIR/assets;
    index index.html portal.html;

    # 主页重定向
    location = / {
        rewrite ^ /portal.html last;
    }

    # 前端静态文件
    location / {
        try_files \$uri \$uri/ /portal.html;
        expires 7d;
        add_header Cache-Control "public";
    }

    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|webp|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:$BACKEND_PORT/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket 代理
    location /ws/ {
        proxy_pass http://127.0.0.1:$BACKEND_PORT/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        proxy_connect_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_read_timeout 3600s;
    }

    # 健康检查端点
    location /health {
        proxy_pass http://127.0.0.1:$BACKEND_PORT/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        access_log off;
    }

    client_max_body_size 50M;
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/restaurant /etc/nginx/sites-enabled/

# 测试 Nginx 配置
nginx -t

# 重启 Nginx
systemctl restart nginx

echo "✅ Nginx 配置完成"
echo ""

# 完成
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "访问地址:"
echo "  前端: http://$(curl -s ifconfig.me)/"
echo "  点餐页面: http://$(curl -s ifconfig.me)/customer_order_v3.html"
echo "  API 文档: http://$(curl -s ifconfig.me)/docs"
echo ""
echo "重要信息:"
echo "  数据库名: $DB_NAME"
echo "  数据库用户: $DB_USER"
echo "  数据库密码: $DB_PASS"
echo "  后端端口: $BACKEND_PORT"
echo ""
echo "常用命令:"
echo "  查看后端日志: journalctl -u restaurant-backend -f"
echo "  重启后端: systemctl restart restaurant-backend"
echo "  查看后端状态: systemctl status restaurant-backend"
echo "  重启 Nginx: systemctl restart nginx"
echo ""
echo "宝塔面板:"
echo "  如果已安装，宝塔面板会显示在端口 8888"
echo "  访问: http://$(curl -s ifconfig.me):8888/"
echo ""
