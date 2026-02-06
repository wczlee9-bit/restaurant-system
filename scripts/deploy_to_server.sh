#!/bin/bash

# ========================================
# 多店铺扫码点餐系统 - 一键部署脚本
# ========================================
# 使用方法：
#   1. 将此脚本和项目代码上传到服务器
#   2. 执行: bash scripts/deploy_to_server.sh
# ========================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印分隔线
print_separator() {
    echo "============================================================"
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_warning "建议使用root用户执行此脚本"
        read -p "是否继续？(y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VERSION=$VERSION_ID
    else
        log_error "无法检测操作系统"
        exit 1
    fi
    log_info "检测到操作系统: $OS $VERSION"
}

# 更新系统
update_system() {
    log_info "更新系统软件包..."
    apt update -y
    apt upgrade -y
    log_success "系统更新完成"
}

# 安装系统依赖
install_dependencies() {
    log_info "安装系统依赖..."
    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        postgresql \
        postgresql-contrib \
        nginx \
        git \
        curl \
        wget \
        htop \
        vim

    log_success "系统依赖安装完成"
}

# 配置PostgreSQL
configure_postgresql() {
    log_info "配置PostgreSQL数据库..."

    # 启动PostgreSQL服务
    service postgresql start

    # 设置数据库密码（从环境变量读取或使用默认值）
    DB_PASSWORD=${DB_PASSWORD:-"Restaurant@2024"}
    DB_NAME=${DB_NAME:-"restaurant_db"}
    DB_USER=${DB_USER:-"restaurant_user"}

    # 创建数据库和用户
    log_info "创建数据库和用户..."
    sudo -u postgres psql <<EOF
-- 创建数据库用户
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';

-- 创建数据库
CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};

-- 授权
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};

-- 连接到数据库并授权schema权限
\c ${DB_NAME}
GRANT ALL ON SCHEMA public TO ${DB_USER};
EOF

    log_success "PostgreSQL配置完成"
    log_info "数据库名: ${DB_NAME}"
    log_info "数据库用户: ${DB_USER}"
    log_info "数据库密码: ${DB_PASSWORD}"
}

# 创建Python虚拟环境
create_venv() {
    log_info "创建Python虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate

    # 升级pip
    pip install --upgrade pip setuptools wheel

    log_success "虚拟环境创建完成"
}

# 安装Python依赖
install_python_dependencies() {
    log_info "安装Python依赖..."
    source venv/bin/activate

    # 如果requirements.txt存在则安装
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        # 安装核心依赖
        pip install \
            fastapi \
            uvicorn[standard] \
            sqlalchemy \
            psycopg2-binary \
            pydantic \
            python-multipart \
            python-jose[cryptography] \
            passlib[bcrypt] \
            python-dateutil \
            requests
    fi

    log_success "Python依赖安装完成"
}

# 配置环境变量
configure_env() {
    log_info "配置环境变量..."

    DB_PASSWORD=${DB_PASSWORD:-"Restaurant@2024"}
    DB_NAME=${DB_NAME:-"restaurant_db"}
    DB_USER=${DB_USER:-"restaurant_user"}

    cat > .env <<EOF
# 数据库配置
PGDATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}

# 应用配置
APP_ENV=production
SECRET_KEY=$(openssl rand -hex 32)

# 服务器配置
HOST=0.0.0.0
PORT=8080
EOF

    log_success "环境变量配置完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    source venv/bin/activate

    # 导出环境变量
    export $(cat .env | xargs)

    # 使用Python脚本初始化数据库
    python3 <<EOF
import os
import sys
sys.path.insert(0, os.getcwd())

from storage.database.init_db import init_database, ensure_test_data

print("开始初始化数据库...")
init_database()
ensure_test_data()
print("数据库初始化完成！")
EOF

    log_success "数据库初始化完成"
}

# 创建systemd服务
create_systemd_service() {
    log_info "创建systemd服务..."

    PROJECT_DIR=$(pwd)
    USER=$(whoami)

    cat > /etc/systemd/system/restaurant.service <<EOF
[Unit]
Description=Restaurant Ordering System
After=network.target postgresql.service

[Service]
Type=simple
User=${USER}
WorkingDirectory=${PROJECT_DIR}
Environment="PATH=${PROJECT_DIR}/venv/bin"
EnvironmentFile=${PROJECT_DIR}/.env
ExecStart=${PROJECT_DIR}/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    log_success "systemd服务创建完成"
}

# 配置Nginx
configure_nginx() {
    log_info "配置Nginx..."

    DOMAIN=${DOMAIN:-"localhost"}

    cat > /etc/nginx/sites-available/restaurant <<EOF
server {
    listen 80;
    server_name ${DOMAIN};

    # 日志
    access_log /var/log/nginx/restaurant_access.log;
    error_log /var/log/nginx/restaurant_error.log;

    # 反向代理到FastAPI
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时设置
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }

    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        proxy_pass http://127.0.0.1:8080;
        expires 30d;
    }
}
EOF

    # 启用站点
    ln -sf /etc/nginx/sites-available/restaurant /etc/nginx/sites-enabled/

    # 移除默认站点
    rm -f /etc/nginx/sites-enabled/default

    # 测试配置
    nginx -t

    log_success "Nginx配置完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."

    # 允许SSH
    ufw allow OpenSSH

    # 允许HTTP和HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp

    # 启用防火墙
    ufw --force enable

    log_success "防火墙配置完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."

    # 重载systemd
    systemctl daemon-reload

    # 启动并启用服务
    systemctl enable restaurant
    systemctl start restaurant

    # 重启Nginx
    systemctl restart nginx

    log_success "服务启动完成"
}

# 测试服务
test_service() {
    log_info "测试服务..."

    sleep 3

    # 测试健康检查
    if curl -sf http://127.0.0.1:8080/health > /dev/null; then
        log_success "后端服务运行正常"
    else
        log_error "后端服务启动失败"
        exit 1
    fi

    # 测试API
    if curl -sf http://127.0.0.1:8080/api/store > /dev/null; then
        log_success "API接口正常"
    else
        log_error "API接口测试失败"
        exit 1
    fi
}

# 显示部署信息
show_deployment_info() {
    print_separator
    log_success "🎉 部署完成！"
    print_separator
    echo
    echo -e "${GREEN}服务信息:${NC}"
    echo "  - 后端服务: http://127.0.0.1:8080"
    echo "  - Nginx: http://127.0.0.1 (或您的域名)"
    echo
    echo -e "${GREEN}数据库信息:${NC}"
    echo "  - 数据库名: ${DB_NAME:-restaurant_db}"
    echo "  - 用户名: ${DB_USER:-restaurant_user}"
    echo "  - 密码: ${DB_PASSWORD:-Restaurant@2024}"
    echo
    echo -e "${GREEN}管理命令:${NC}"
    echo "  - 查看状态: systemctl status restaurant"
    echo "  - 启动服务: systemctl start restaurant"
    echo "  - 停止服务: systemctl stop restaurant"
    echo "  - 重启服务: systemctl restart restaurant"
    echo "  - 查看日志: journalctl -u restaurant -f"
    echo
    echo -e "${GREEN}测试API:${NC}"
    echo "  - 健康检查: curl http://127.0.0.1:8080/health"
    echo "  - 店铺信息: curl http://127.0.0.1:8080/api/store"
    echo
    print_separator
}

# 主函数
main() {
    print_separator
    echo -e "${BLUE}多店铺扫码点餐系统 - 一键部署脚本${NC}"
    print_separator
    echo

    check_root
    detect_os

    # 询问是否继续
    read -p "是否开始部署？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "部署已取消"
        exit 0
    fi

    echo
    print_separator

    # 执行部署步骤
    update_system
    install_dependencies
    configure_postgresql
    create_venv
    install_python_dependencies
    configure_env
    init_database
    create_systemd_service
    configure_nginx
    configure_firewall
    start_services
    test_service
    show_deployment_info

    log_success "所有部署步骤完成！"
}

# 捕获Ctrl+C
trap 'log_error "部署已取消"; exit 1' INT

# 执行主函数
main "$@"
