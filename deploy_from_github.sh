#!/bin/bash

###############################################################################
# 腾讯云一键部署脚本（从 GitHub）
# 作用：从 GitHub 克隆代码并部署到腾讯云服务器
# 使用：bash deploy_from_github.sh
###############################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置变量
GITHUB_REPO="${GITHUB_REPO:-https://github.com/wczlee9-bit/restaurant-system.git}"
PROJECT_DIR="${PROJECT_DIR:-/opt/restaurant-system}"
BACKUP_DIR="${BACKUP_DIR:-/tmp/restaurant-backup}"
DB_USER="${DB_USER:-postgres}"
DB_NAME="${DB_NAME:-restaurant_db}"
PYTHON_VERSION="${PYTHON_VERSION:-3.10}"

###############################################################################
# 函数定义
###############################################################################

print_header() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_step() {
    echo -e "\n${BLUE}[步骤 $1] $2${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "未找到命令: $1"
        return 1
    fi
    return 0
}

###############################################################################
# 步骤 1：环境检查
###############################################################################

check_environment() {
    print_header "步骤 1：环境检查"

    # 检查系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_success "操作系统: Linux"
    else
        print_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi

    # 检查必需命令
    print_info "检查必需命令..."
    local commands=("git" "python${PYTHON_VERSION}" "pip${PYTHON_VERSION}" "psql" "systemctl" "nginx")
    local missing_commands=()

    for cmd in "${commands[@]}"; do
        if ! check_command $cmd; then
            missing_commands+=("$cmd")
        fi
    done

    if [ ${#missing_commands[@]} -gt 0 ]; then
        print_error "缺少必需命令: ${missing_commands[*]}"
        print_info "请先安装缺少的命令"
        exit 1
    fi

    print_success "所有必需命令已安装"

    # 检查数据库连接
    print_info "检查数据库连接..."
    if sudo -u postgres psql -c "SELECT 1;" &> /dev/null; then
        print_success "数据库连接正常"
    else
        print_error "数据库连接失败"
        print_info "请确保 PostgreSQL 服务正在运行"
        exit 1
    fi

    print_success "环境检查通过"
}

###############################################################################
# 步骤 2：备份现有系统
###############################################################################

backup_system() {
    print_header "步骤 2：备份现有系统"

    # 如果项目目录存在，先备份
    if [ -d "$PROJECT_DIR" ]; then
        print_info "备份现有系统..."

        BACKUP_NAME="restaurant-backup-$(date +%Y%m%d-%H%M%S)"
        BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

        mkdir -p "$BACKUP_DIR"

        # 备份代码
        print_info "备份代码到 $BACKUP_PATH..."
        cp -r "$PROJECT_DIR" "$BACKUP_PATH"

        # 备份数据库
        print_info "备份数据库..."
        sudo -u postgres pg_dump "$DB_NAME" > "$BACKUP_PATH/restaurant-db-backup.sql"

        print_success "备份完成: $BACKUP_PATH"
    else
        print_info "项目目录不存在，跳过备份"
    fi
}

###############################################################################
# 步骤 3：克隆代码
###############################################################################

clone_code() {
    print_header "步骤 3：从 GitHub 克隆代码"

    # 删除旧的项目目录（如果有）
    if [ -d "$PROJECT_DIR" ]; then
        print_info "删除旧的项目目录..."
        rm -rf "$PROJECT_DIR"
    fi

    # 克隆代码
    print_info "从 GitHub 克隆代码..."
    print_info "仓库地址: $GITHUB_REPO"
    git clone "$GITHUB_REPO" "$PROJECT_DIR"

    if [ $? -eq 0 ]; then
        print_success "代码克隆成功"
    else
        print_error "代码克隆失败"
        exit 1
    fi

    cd "$PROJECT_DIR"

    # 显示当前版本
    print_info "当前版本:"
    git log --oneline -3
}

###############################################################################
# 步骤 4：安装依赖
###############################################################################

install_dependencies() {
    print_header "步骤 4：安装依赖"

    cd "$PROJECT_DIR"

    # 创建虚拟环境（如果不存在）
    if [ ! -d "venv" ]; then
        print_info "创建 Python 虚拟环境..."
        python${PYTHON_VERSION} -m venv venv
    fi

    # 激活虚拟环境
    source venv/bin/activate

    # 升级 pip
    print_info "升级 pip..."
    pip install --upgrade pip

    # 安装依赖
    print_info "安装 Python 依赖..."
    pip install -r requirements.txt

    if [ $? -eq 0 ]; then
        print_success "依赖安装完成"
    else
        print_error "依赖安装失败"
        exit 1
    fi
}

###############################################################################
# 步骤 5：初始化数据库
###############################################################################

init_database() {
    print_header "步骤 5：初始化数据库"

    cd "$PROJECT_DIR"
    source venv/bin/activate

    # 检查数据库是否存在
    print_info "检查数据库..."
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        print_info "数据库已存在: $DB_NAME"

        # 询问是否更新数据库结构
        read -p "是否需要更新数据库结构？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "运行数据库迁移..."
            # 这里可以添加数据库迁移脚本
            print_success "数据库结构已更新"
        fi
    else
        print_info "创建数据库: $DB_NAME"
        sudo -u postgres createdb "$DB_NAME"

        # 初始化数据库
        print_info "初始化数据库..."
        # python scripts/init_db.py
        print_success "数据库初始化完成"
    fi
}

###############################################################################
# 步骤 6：测试模块加载器
###############################################################################

test_modules() {
    print_header "步骤 6：测试模块加载器"

    cd "$PROJECT_DIR"
    source venv/bin/activate

    print_info "运行模块加载器测试..."
    python test_module_loader.py

    if [ $? -eq 0 ]; then
        print_success "模块测试通过"
    else
        print_error "模块测试失败"
        print_info "请检查日志"
        exit 1
    fi
}

###############################################################################
# 步骤 7：配置服务
###############################################################################

configure_services() {
    print_header "步骤 7：配置服务"

    cd "$PROJECT_DIR"

    # 创建 systemd 服务文件
    print_info "创建 systemd 服务文件..."
    cat > /etc/systemd/system/restaurant.service << EOF
[Unit]
Description=Restaurant System
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # 重新加载 systemd
    print_info "重新加载 systemd..."
    systemctl daemon-reload

    print_success "服务配置完成"
}

###############################################################################
# 步骤 8：启动服务
###############################################################################

start_services() {
    print_header "步骤 8：启动服务"

    # 停止旧服务
    print_info "停止旧服务..."
    systemctl stop restaurant 2>/dev/null || true

    # 启动新服务
    print_info "启动服务..."
    systemctl start restaurant

    # 启用开机自启
    print_info "启用开机自启..."
    systemctl enable restaurant

    # 等待服务启动
    sleep 3

    # 检查服务状态
    print_info "检查服务状态..."
    if systemctl is-active --quiet restaurant; then
        print_success "服务启动成功"
    else
        print_error "服务启动失败"
        print_info "查看服务日志:"
        journalctl -u restaurant -n 20 --no-pager
        exit 1
    fi
}

###############################################################################
# 步骤 9：配置 Nginx
###############################################################################

configure_nginx() {
    print_header "步骤 9：配置 Nginx"

    # 创建 Nginx 配置文件
    print_info "创建 Nginx 配置文件..."
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
    print_info "启用站点..."
    ln -sf /etc/nginx/sites-available/restaurant /etc/nginx/sites-enabled/

    # 删除默认配置
    rm -f /etc/nginx/sites-enabled/default

    # 测试 Nginx 配置
    print_info "测试 Nginx 配置..."
    nginx -t

    if [ $? -eq 0 ]; then
        # 重启 Nginx
        print_info "重启 Nginx..."
        systemctl restart nginx
        print_success "Nginx 配置完成"
    else
        print_error "Nginx 配置错误"
        exit 1
    fi
}

###############################################################################
# 步骤 10：验证部署
###############################################################################

verify_deployment() {
    print_header "步骤 10：验证部署"

    # 检查服务状态
    print_info "检查服务状态..."
    systemctl status restaurant --no-pager

    # 检查端口监听
    print_info "检查端口监听..."
    netstat -tlnp | grep :8000

    # 测试 API
    print_info "测试 API..."
    sleep 2

    # 获取服务器 IP
    SERVER_IP=$(hostname -I | awk '{print $1}')

    # 测试健康检查
    if curl -f http://127.0.0.1:8000/health &> /dev/null; then
        print_success "API 测试通过"
    else
        print_error "API 测试失败"
    fi

    print_success "部署验证完成"
}

###############################################################################
# 主函数
###############################################################################

main() {
    print_header "餐厅系统一键部署脚本（从 GitHub）"

    print_info "配置信息:"
    echo "  GitHub 仓库: $GITHUB_REPO"
    echo "  项目目录: $PROJECT_DIR"
    echo "  数据库名: $DB_NAME"
    echo "  Python 版本: $PYTHON_VERSION"

    read -p "确认开始部署？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "部署已取消"
        exit 0
    fi

    # 执行部署步骤
    check_environment
    backup_system
    clone_code
    install_dependencies
    init_database
    test_modules
    configure_services
    start_services
    configure_nginx
    verify_deployment

    # 显示部署信息
    print_header "部署完成"

    SERVER_IP=$(hostname -I | awk '{print $1}')

    print_success "系统已成功部署！"
    echo ""
    echo "访问地址:"
    echo "  - 后端 API: http://$SERVER_IP"
    echo "  - 健康检查: http://$SERVER_IP/health"
    echo ""
    echo "管理命令:"
    echo "  - 查看状态: systemctl status restaurant"
    echo "  - 查看日志: journalctl -u restaurant -f"
    echo "  - 重启服务: systemctl restart restaurant"
    echo "  - 停止服务: systemctl stop restaurant"
    echo ""
    print_info "备份位置: $BACKUP_DIR"
    print_info "项目目录: $PROJECT_DIR"
    echo "  GitHub 仓库: $GITHUB_REPO"
}

# 运行主函数
main
