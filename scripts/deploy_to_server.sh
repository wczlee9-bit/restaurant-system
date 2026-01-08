#!/bin/bash

# ============================================
# 餐饮点餐系统 - 服务器自动部署脚本
# 用途：自动化部署后端服务到Ubuntu服务器
# ============================================

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

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root用户或sudo运行此脚本"
        exit 1
    fi
}

# 检查输入参数
if [ $# -lt 2 ]; then
    log_error "用法: $0 <操作> [参数]"
    echo ""
    echo "可用操作:"
    echo "  install       - 首次安装系统"
    echo "  update        - 更新系统代码"
    echo "  start         - 启动所有服务"
    echo "  stop          - 停止所有服务"
    echo "  restart       - 重启所有服务"
    echo "  status        - 查看服务状态"
    echo "  backup        - 备份数据库"
    echo "  restore <文件> - 从备份恢复数据库"
    echo ""
    echo "示例:"
    echo "  $0 install"
    echo "  $0 update"
    echo "  $0 backup"
    echo "  $0 restore /opt/restaurant-system/backups/restaurant_db_20240101.sql.gz"
    exit 1
fi

OPERATION=$1

# ============================================
# 安装系统
# ============================================
install_system() {
    log_info "开始安装餐饮点餐系统..."

    # 1. 更新系统
    log_info "更新系统软件包..."
    apt update && apt upgrade -y

    # 2. 安装必要软件
    log_info "安装Python 3.8+..."
    apt install -y python3.8 python3-pip python3-venv git curl wget

    log_info "安装PostgreSQL..."
    apt install -y postgresql postgresql-contrib

    log_info "安装Nginx..."
    apt install -y nginx

    log_info "安装Supervisor..."
    apt install -y supervisor

    log_success "基础软件安装完成"

    # 3. 配置PostgreSQL
    log_info "配置PostgreSQL数据库..."
    configure_database

    # 4. 克隆或更新代码
    log_info "准备项目代码..."
    setup_project

    # 5. 安装Python依赖
    log_info "安装Python依赖..."
    install_dependencies

    # 6. 创建环境变量文件
    log_info "创建环境变量配置..."
    setup_env

    # 7. 初始化数据库
    log_info "初始化数据库表..."
    init_database

    # 8. 创建Systemd服务
    log_info "创建Systemd服务..."
    create_systemd_services

    # 9. 配置Nginx
    log_info "配置Nginx反向代理..."
    configure_nginx

    # 10. 配置防火墙
    log_info "配置防火墙..."
    configure_firewall

    # 11. 启动所有服务
    log_info "启动所有服务..."
    start_all_services

    # 12. 创建备份脚本
    log_info "配置数据库自动备份..."
    setup_backup

    log_success "系统安装完成！"
    echo ""
    log_info "================================"
    log_info "访问地址："
    log_info "  前端: https://your-netlify-site.netlify.app"
    log_info "  API文档: http://$(hostname -I | awk '{print $1}'):8000/docs"
    log_info "================================"
}

# ============================================
# 配置数据库
# ============================================
configure_database() {
    log_info "创建数据库和用户..."

    # 提示输入数据库密码
    read -sp "请输入数据库密码: " DB_PASSWORD
    echo ""

    # 创建数据库和用户
    sudo -u postgres psql <<EOF
-- 创建数据库
CREATE DATABASE restaurant_db;

-- 创建用户
CREATE USER restaurant_user WITH PASSWORD '$DB_PASSWORD';

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE restaurant_db TO restaurant_user;

-- 连接到数据库并授予schema权限
\c restaurant_db
GRANT ALL ON SCHEMA public TO restaurant_user;

\q
EOF

    log_success "数据库配置完成"
}

# ============================================
# 准备项目代码
# ============================================
setup_project() {
    PROJECT_DIR="/opt/restaurant-system"

    log_info "创建项目目录: $PROJECT_DIR"
    mkdir -p $PROJECT_DIR

    if [ -d "$PROJECT_DIR" ]; then
        log_info "项目目录已存在，跳过克隆"
    else
        log_info "请将代码上传到 $PROJECT_DIR"
        log_info "或使用git克隆:"
        log_info "  git clone https://github.com/YOUR_REPO/restaurant-system.git $PROJECT_DIR"
    fi
}

# ============================================
# 安装Python依赖
# ============================================
install_dependencies() {
    PROJECT_DIR="/opt/restaurant-system"

    if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
        log_warning "未找到requirements.txt，跳过依赖安装"
        return
    fi

    log_info "创建Python虚拟环境..."
    python3 -m venv $PROJECT_DIR/venv

    log_info "安装Python依赖..."
    $PROJECT_DIR/venv/bin/pip install --upgrade pip
    $PROJECT_DIR/venv/bin/pip install -r $PROJECT_DIR/requirements.txt

    log_success "Python依赖安装完成"
}

# ============================================
# 配置环境变量
# ============================================
setup_env() {
    PROJECT_DIR="/opt/restaurant-system"
    ENV_FILE="$PROJECT_DIR/.env"

    log_info "创建环境变量文件..."

    if [ ! -f "$ENV_FILE" ]; then
        cat > $ENV_FILE <<EOF
# 数据库配置
DATABASE_URL=postgresql://restaurant_user:your_password@localhost:5432/restaurant_db

# S3对象存储配置
S3_ACCESS_KEY=your_s3_access_key
S3_SECRET_KEY=your_s3_secret_key
S3_BUCKET_NAME=your_bucket_name
S3_REGION=us-east-1
S3_ENDPOINT=https://your_s3_endpoint

# 其他配置
COZE_API_KEY=your_coze_api_key
LOG_LEVEL=INFO
EOF

        log_warning "请编辑 $ENV_FILE 并填入正确的配置"
        chmod 600 $ENV_FILE
    else
        log_info "环境变量文件已存在，跳过创建"
    fi
}

# ============================================
# 初始化数据库
# ============================================
init_database() {
    PROJECT_DIR="/opt/restaurant-system"

    log_info "初始化数据库表..."

    cd $PROJECT_DIR
    source venv/bin/activate

    # 运行初始化脚本
    if [ -f "scripts/init_database.py" ]; then
        python scripts/init_database.py
    else
        log_warning "未找到init_database.py，使用ORM创建表..."
        python -c "
from storage.database.db import engine
from storage.database.shared.model import Base
Base.metadata.create_all(bind=engine)
print('数据库表创建成功')
"
    fi

    deactivate

    log_success "数据库初始化完成"
}

# ============================================
# 创建Systemd服务
# ============================================
create_systemd_services() {
    PROJECT_DIR="/opt/restaurant-system"

    log_info "创建Systemd服务配置..."

    # 顾客API服务
    cat > /etc/systemd/system/restaurant-customer-api.service <<EOF
[Unit]
Description=Restaurant Customer API
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python -m uvicorn api.customer_api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # 店员API服务
    cat > /etc/systemd/system/restaurant-staff-api.service <<EOF
[Unit]
Description=Restaurant Staff API
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python -m uvicorn api.staff_api:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # 会员API服务
    cat > /etc/systemd/system/restaurant-member-api.service <<EOF
[Unit]
Description=Restaurant Member API
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python -m uvicorn api.member_api:app --host 0.0.0.0 --port 8004
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # 总公司API服务
    cat > /etc/systemd/system/restaurant-hq-api.service <<EOF
[Unit]
Description=Restaurant Headquarters API
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python -m uvicorn api.headquarters_api:app --host 0.0.0.0 --port 8006
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # 重载Systemd
    systemctl daemon-reload

    log_success "Systemd服务创建完成"
}

# ============================================
# 配置Nginx
# ============================================
configure_nginx() {
    log_info "配置Nginx..."

    cat > /etc/nginx/sites-available/restaurant-api <<EOF
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
    server_name _;

    # 日志
    access_log /var/log/nginx/restaurant-api-access.log;
    error_log /var/log/nginx/restaurant-api-error.log;

    # API路由
    location /api/orders {
        proxy_pass http://customer_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/member {
        proxy_pass http://member_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/headquarters {
        proxy_pass http://hq_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/ {
        proxy_pass http://staff_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # WebSocket支持
    location /ws {
        proxy_pass http://staff_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

    # 启用站点配置
    ln -sf /etc/nginx/sites-available/restaurant-api /etc/nginx/sites-enabled/

    # 测试Nginx配置
    nginx -t

    # 重启Nginx
    systemctl restart nginx

    log_success "Nginx配置完成"
}

# ============================================
# 配置防火墙
# ============================================
configure_firewall() {
    log_info "配置防火墙..."

    if command -v ufw &> /dev/null; then
        # 使用ufw
        ufw allow 22/tcp
        ufw allow 80/tcp
        ufw allow 443/tcp
        ufw allow 8000/tcp
        ufw allow 8001/tcp
        ufw allow 8004/tcp
        ufw allow 8006/tcp
        ufw --force enable
    else
        log_warning "未安装ufw，跳过防火墙配置"
    fi

    log_success "防火墙配置完成"
}

# ============================================
# 启动所有服务
# ============================================
start_all_services() {
    log_info "启用并启动所有服务..."

    # 启用服务
    systemctl enable restaurant-customer-api
    systemctl enable restaurant-staff-api
    systemctl enable restaurant-member-api
    systemctl enable restaurant-hq-api

    # 启动服务
    systemctl start restaurant-customer-api
    systemctl start restaurant-staff-api
    systemctl start restaurant-member-api
    systemctl start restaurant-hq-api

    # 等待服务启动
    sleep 3

    # 检查服务状态
    log_info "检查服务状态..."
    systemctl status restaurant-customer-api --no-pager -l
    systemctl status restaurant-staff-api --no-pager -l
    systemctl status restaurant-member-api --no-pager -l
    systemctl status restaurant-hq-api --no-pager -l

    log_success "所有服务已启动"
}

# ============================================
# 配置自动备份
# ============================================
setup_backup() {
    PROJECT_DIR="/opt/restaurant-system"
    BACKUP_DIR="$PROJECT_DIR/backups"
    BACKUP_SCRIPT="$PROJECT_DIR/scripts/backup_db.sh"

    log_info "配置数据库自动备份..."

    # 创建备份目录
    mkdir -p $BACKUP_DIR

    # 创建备份脚本
    cat > $BACKUP_SCRIPT <<'EOF'
#!/bin/bash
BACKUP_DIR="/opt/restaurant-system/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/restaurant_db_$DATE.sql"

mkdir -p $BACKUP_DIR

# 读取环境变量
source /opt/restaurant-system/.env

# 备份数据库
pg_dump -h localhost -U restaurant_user restaurant_db > $BACKUP_FILE

# 压缩备份
gzip $BACKUP_FILE

# 保留最近7天的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
EOF

    chmod +x $BACKUP_SCRIPT

    # 添加到crontab
    (crontab -l 2>/dev/null; echo "0 2 * * * $BACKUP_SCRIPT >> /var/log/restaurant_backup.log 2>&1") | crontab -

    log_success "自动备份配置完成 (每天凌晨2点)"
}

# ============================================
# 更新系统
# ============================================
update_system() {
    log_info "更新系统..."

    PROJECT_DIR="/opt/restaurant-system"

    # 拉取最新代码
    if [ -d "$PROJECT_DIR/.git" ]; then
        cd $PROJECT_DIR
        git pull origin main
    else
        log_warning "项目不是Git仓库，跳过代码更新"
    fi

    # 更新依赖
    cd $PROJECT_DIR
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate

    # 重启服务
    restart_all_services

    log_success "系统更新完成"
}

# ============================================
# 停止所有服务
# ============================================
stop_all_services() {
    log_info "停止所有服务..."

    systemctl stop restaurant-customer-api
    systemctl stop restaurant-staff-api
    systemctl stop restaurant-member-api
    systemctl stop restaurant-hq-api

    log_success "所有服务已停止"
}

# ============================================
# 重启所有服务
# ============================================
restart_all_services() {
    log_info "重启所有服务..."

    systemctl restart restaurant-customer-api
    systemctl restart restaurant-staff-api
    systemctl restart restaurant-member-api
    systemctl restart restaurant-hq-api

    sleep 3

    # 检查服务状态
    systemctl status restaurant-customer-api --no-pager
    systemctl status restaurant-staff-api --no-pager
    systemctl status restaurant-member-api --no-pager
    systemctl status restaurant-hq-api --no-pager

    log_success "所有服务已重启"
}

# ============================================
# 查看服务状态
# ============================================
show_status() {
    log_info "服务状态:"

    echo ""
    echo "顾客API服务 (端口8000):"
    systemctl status restaurant-customer-api --no-pager -l

    echo ""
    echo "店员API服务 (端口8001):"
    systemctl status restaurant-staff-api --no-pager -l

    echo ""
    echo "会员API服务 (端口8004):"
    systemctl status restaurant-member-api --no-pager -l

    echo ""
    echo "总公司API服务 (端口8006):"
    systemctl status restaurant-hq-api --no-pager -l

    echo ""
    echo "Nginx服务:"
    systemctl status nginx --no-pager -l

    echo ""
    echo "PostgreSQL服务:"
    systemctl status postgresql --no-pager -l
}

# ============================================
# 备份数据库
# ============================================
backup_database() {
    log_info "备份数据库..."

    BACKUP_DIR="/opt/restaurant-system/backups"
    BACKUP_SCRIPT="$BACKUP_DIR/backup_db.sh"

    if [ -f "$BACKUP_SCRIPT" ]; then
        $BACKUP_SCRIPT
    else
        log_error "备份脚本不存在: $BACKUP_SCRIPT"
        exit 1
    fi
}

# ============================================
# 恢复数据库
# ============================================
restore_database() {
    if [ -z "$2" ]; then
        log_error "请指定备份文件"
        echo "用法: $0 restore <备份文件路径>"
        exit 1
    fi

    BACKUP_FILE=$2

    log_info "从备份恢复数据库: $BACKUP_FILE"

    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "备份文件不存在: $BACKUP_FILE"
        exit 1
    fi

    # 停止所有服务
    stop_all_services

    # 恢复数据库
    if [[ $BACKUP_FILE == *.gz ]]; then
        log_info "解压备份文件..."
        TEMP_FILE=$(mktemp)
        gunzip -c $BACKUP_FILE > $TEMP_FILE

        log_info "恢复数据库..."
        psql -h localhost -U restaurant_user -d restaurant_db < $TEMP_FILE

        rm -f $TEMP_FILE
    else
        log_info "恢复数据库..."
        psql -h localhost -U restaurant_user -d restaurant_db < $BACKUP_FILE
    fi

    # 启动所有服务
    start_all_services

    log_success "数据库恢复完成"
}

# ============================================
# 主逻辑
# ============================================
check_root

case $OPERATION in
    install)
        install_system
        ;;
    update)
        update_system
        ;;
    start)
        start_all_services
        ;;
    stop)
        stop_all_services
        ;;
    restart)
        restart_all_services
        ;;
    status)
        show_status
        ;;
    backup)
        backup_database
        ;;
    restore)
        restore_database $@
        ;;
    *)
        log_error "未知操作: $OPERATION"
        exit 1
        ;;
esac
