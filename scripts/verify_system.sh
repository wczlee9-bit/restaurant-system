#!/bin/bash

# ============================================
# 餐饮点餐系统 - 系统验证脚本
# 用途：验证系统部署后的各项功能和配置
# ============================================

set -e

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
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# 统计变量
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
run_test() {
    local test_name=$1
    local test_command=$2

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    log_info "测试: $test_name"

    if eval "$test_command" > /dev/null 2>&1; then
        log_success "$test_name - 通过"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        log_error "$test_name - 失败"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# 打印分隔线
print_separator() {
    echo ""
    echo "========================================"
    echo ""
}

# ============================================
# 系统检查
# ============================================
check_system() {
    print_separator
    log_info "开始系统检查..."
    print_separator

    # 检查操作系统
    log_info "检查操作系统..."
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        log_info "操作系统: $NAME $VERSION"
    fi

    # 检查CPU
    log_info "CPU核心数: $(nproc)"

    # 检查内存
    log_info "内存使用情况:"
    free -h

    # 检查磁盘
    log_info "磁盘使用情况:"
    df -h

    print_separator
}

# ============================================
# 服务检查
# ============================================
check_services() {
    print_separator
    log_info "检查系统服务..."
    print_separator

    # PostgreSQL
    run_test "PostgreSQL服务" "systemctl is-active postgresql"

    # Nginx
    run_test "Nginx服务" "systemctl is-active nginx"

    # 餐饮系统API服务
    run_test "顾客API服务 (端口8000)" "systemctl is-active restaurant-customer-api"
    run_test "店员API服务 (端口8001)" "systemctl is-active restaurant-staff-api"
    run_test "会员API服务 (端口8004)" "systemctl is-active restaurant-member-api"
    run_test "总公司API服务 (端口8006)" "systemctl is-active restaurant-hq-api"

    print_separator
}

# ============================================
# 端口检查
# ============================================
check_ports() {
    print_separator
    log_info "检查端口监听..."
    print_separator

    # 检查端口是否被监听
    check_port() {
        local port=$1
        local service_name=$2

        if netstat -tunlp 2>/dev/null | grep -q ":$port "; then
            log_success "端口 $port ($service_name) - 正常监听"
            return 0
        else
            log_error "端口 $port ($service_name) - 未监听"
            return 1
        fi
    }

    check_port 8000 "顾客API"
    check_port 8001 "店员API"
    check_port 8004 "会员API"
    check_port 8006 "总公司API"
    check_port 5432 "PostgreSQL"
    check_port 80 "Nginx HTTP"
    check_port 443 "Nginx HTTPS"

    print_separator
}

# ============================================
# 数据库检查
# ============================================
check_database() {
    print_separator
    log_info "检查数据库连接和表..."
    print_separator

    # 检查数据库连接
    run_test "数据库连接" "psql -h localhost -U restaurant_user -d restaurant_db -c 'SELECT 1' > /dev/null 2>&1"

    # 检查关键表是否存在
    log_info "检查数据库表..."

    TABLES=("stores" "members" "orders" "order_items" "users" "roles" "daily_revenue")

    for table in "${TABLES[@]}"; do
        if psql -h localhost -U restaurant_user -d restaurant_db -c "\dt $table" 2>/dev/null | grep -q "$table"; then
            log_success "表 $table 存在"
        else
            log_error "表 $table 不存在"
        fi
    done

    # 检查数据
    log_info "检查数据完整性..."

    STORE_COUNT=$(psql -h localhost -U restaurant_user -d restaurant_db -t -c "SELECT COUNT(*) FROM stores;" 2>/dev/null | tr -d ' ')
    MEMBER_COUNT=$(psql -h localhost -U restaurant_user -d restaurant_db -t -c "SELECT COUNT(*) FROM members;" 2>/dev/null | tr -d ' ')
    ORDER_COUNT=$(psql -h localhost -U restaurant_user -d restaurant_db -t -c "SELECT COUNT(*) FROM orders;" 2>/dev/null | tr -d ' ')

    log_info "店铺数量: $STORE_COUNT"
    log_info "会员数量: $MEMBER_COUNT"
    log_info "订单数量: $ORDER_COUNT"

    print_separator
}

# ============================================
# API 检查
# ============================================
check_apis() {
    print_separator
    log_info "检查 API 端点..."
    print_separator

    # 顾客API
    run_test "顾客API文档 (8000)" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/docs | grep -q '200'"

    # 店员API
    run_test "店员API文档 (8001)" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8001/docs | grep -q '200'"

    # 会员API
    run_test "会员API文档 (8004)" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8004/docs | grep -q '200'"

    # 总公司API
    run_test "总公司API文档 (8006)" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8006/docs | grep -q '200'"

    # 测试健康检查端点
    run_test "健康检查接口" "curl -s http://localhost:8000/api/health | grep -q 'healthy'"

    print_separator
}

# ============================================
# 文件检查
# ============================================
check_files() {
    print_separator
    log_info "检查关键文件..."
    print_separator

    PROJECT_DIR="/opt/restaurant-system"

    # 检查项目目录
    if [ -d "$PROJECT_DIR" ]; then
        log_success "项目目录存在: $PROJECT_DIR"
    else
        log_error "项目目录不存在: $PROJECT_DIR"
    fi

    # 检查Python虚拟环境
    if [ -d "$PROJECT_DIR/venv" ]; then
        log_success "Python虚拟环境存在"
    else
        log_error "Python虚拟环境不存在"
    fi

    # 检查环境变量文件
    if [ -f "$PROJECT_DIR/.env" ]; then
        log_success "环境变量文件存在"
        log_warning "请确保 .env 文件包含正确的配置"
    else
        log_error "环境变量文件不存在"
    fi

    # 检查API文件
    API_FILES=(
        "$PROJECT_DIR/src/api/customer_api.py"
        "$PROJECT_DIR/src/api/staff_api.py"
        "$PROJECT_DIR/src/api/member_api.py"
        "$PROJECT_DIR/src/api/headquarters_api.py"
    )

    for file in "${API_FILES[@]}"; do
        if [ -f "$file" ]; then
            log_success "API文件存在: $(basename $file)"
        else
            log_error "API文件不存在: $(basename $file)"
        fi
    done

    print_separator
}

# ============================================
# 日志检查
# ============================================
check_logs() {
    print_separator
    log_info "检查最近日志..."
    print_separator

    # 检查系统服务日志
    log_info "顾客API最近20行日志:"
    journalctl -u restaurant-customer-api -n 20 --no-pager 2>/dev/null || log_warning "无法读取日志"

    echo ""

    log_info "店员API最近20行日志:"
    journalctl -u restaurant-staff-api -n 20 --no-pager 2>/dev/null || log_warning "无法读取日志"

    print_separator
}

# ============================================
# 性能检查
# ============================================
check_performance() {
    print_separator
    log_info "性能检查..."
    print_separator

    # CPU使用率
    log_info "CPU使用率:"
    top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print "CPU使用率: " (100 - $1) "%"}'

    # 内存使用率
    log_info "内存使用率:"
    free | grep Mem | awk '{printf "内存使用率: %.2f%%\n", ($3/$2)*100}'

    # 磁盘使用率
    log_info "磁盘使用率:"
    df -h / | awk 'NR==2{printf "根分区使用率: %s\n", $5}'

    # API响应时间
    log_info "API响应时间测试..."

    test_api_response() {
        local url=$1
        local name=$2

        local start=$(date +%s.%N)
        curl -s "$url" > /dev/null
        local end=$(date +%s.%N)

        local duration=$(echo "$end - $start" | bc)
        log_info "$name: ${duration}s"
    }

    test_api_response "http://localhost:8000/api/health" "健康检查接口"

    print_separator
}

# ============================================
# 安全检查
# ============================================
check_security() {
    print_separator
    log_info "安全检查..."
    print_separator

    # 检查防火墙
    if command -v ufw &> /dev/null; then
        log_info "防火墙状态:"
        ufw status | grep -E "Status|8000|8001|8004|8006"
    else
        log_warning "未安装ufw防火墙"
    fi

    # 检查开放端口
    log_info "开放端口:"
    netstat -tunlp | grep LISTEN | grep -E ":(8000|8001|8004|8006|22|80|443) "

    # 检查环境变量权限
    if [ -f "/opt/restaurant-system/.env" ]; then
        local perms=$(stat -c "%a" /opt/restaurant-system/.env)
        if [ "$perms" == "600" ] || [ "$perms" == "400" ]; then
            log_success "环境变量文件权限正确 ($perms)"
        else
            log_warning "环境变量文件权限过宽 ($perms)，建议设置为 600"
        fi
    fi

    print_separator
}

# ============================================
# 备份检查
# ============================================
check_backups() {
    print_separator
    log_info "备份检查..."
    print_separator

    BACKUP_DIR="/opt/restaurant-system/backups"

    if [ -d "$BACKUP_DIR" ]; then
        log_info "备份目录: $BACKUP_DIR"

        # 列出备份文件
        if [ "$(ls -A $BACKUP_DIR 2>/dev/null)" ]; then
            log_info "可用的备份文件:"
            ls -lh $BACKUP_DIR/*.sql.gz 2>/dev/null | tail -5
        else
            log_warning "备份目录为空"
        fi

        # 检查备份脚本
        if [ -f "$BACKUP_DIR/backup_db.sh" ]; then
            log_success "备份脚本存在"

            # 检查cron任务
            if crontab -l 2>/dev/null | grep -q "backup_db.sh"; then
                log_success "自动备份任务已配置"
                crontab -l 2>/dev/null | grep "backup_db.sh"
            else
                log_warning "未配置自动备份任务"
            fi
        else
            log_warning "备份脚本不存在"
        fi
    else
        log_warning "备份目录不存在"
    fi

    print_separator
}

# ============================================
# 外部连接检查
# ============================================
check_external_connectivity() {
    print_separator
    log_info "外部连接检查..."
    print_separator

    # 检查公网IP
    PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "无法获取")
    log_info "公网IP: $PUBLIC_IP"

    # 检查外网访问
    log_info "测试从外网访问API..."

    # 获取服务器IP
    SERVER_IP=$(hostname -I | awk '{print $1}')

    # 测试从外网访问（需要提供外网访问方式）
    log_warning "请手动从外部网络测试以下URL:"
    log_info "  http://$SERVER_IP:8000/api/health"
    log_info "  http://$SERVER_IP:8001/api/health"
    log_info "  http://$SERVER_IP:8004/api/health"
    log_info "  http://$SERVER_IP:8006/api/health"

    print_separator
}

# ============================================
# 生成报告
# ============================================
generate_report() {
    print_separator
    log_info "生成验证报告..."
    print_separator

    REPORT_FILE="/opt/restaurant-system/verification_report_$(date +%Y%m%d_%H%M%S).txt"

    {
        echo "=========================================="
        echo "餐饮点餐系统 - 系统验证报告"
        echo "=========================================="
        echo "时间: $(date)"
        echo "服务器: $(hostname)"
        echo "IP地址: $(hostname -I | awk '{print $1}')"
        echo ""
        echo "=========================================="
        echo "测试统计"
        echo "=========================================="
        echo "总测试数: $TOTAL_TESTS"
        echo "通过: $PASSED_TESTS"
        echo "失败: $FAILED_TESTS"
        echo "通过率: $(echo "scale=2; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)%"
        echo ""
        echo "=========================================="
        echo "详细日志"
        echo "=========================================="
        echo "请查看上方输出"
    } > "$REPORT_FILE"

    log_success "验证报告已保存: $REPORT_FILE"
    cat "$REPORT_FILE"

    print_separator
}

# ============================================
# 主函数
# ============================================
main() {
    echo ""
    echo "========================================"
    echo "  餐饮点餐系统 - 系统验证脚本"
    echo "========================================"
    echo ""

    # 运行各项检查
    check_system
    check_services
    check_ports
    check_database
    check_apis
    check_files
    check_logs
    check_performance
    check_security
    check_backups
    check_external_connectivity

    # 生成报告
    generate_report

    # 最终结果
    print_separator
    if [ $FAILED_TESTS -eq 0 ]; then
        log_success "所有测试通过！系统运行正常。"
        echo ""
        log_info "================================"
        log_info "系统访问地址："
        log_info "  后端API: http://$(hostname -I | awk '{print $1}')"
        log_info "  API文档: http://$(hostname -I | awk '{print $1}'):8000/docs"
        log_info "================================"
        exit 0
    else
        log_error "有 $FAILED_TESTS 个测试失败，请检查并修复。"
        echo ""
        log_info "查看详细日志:"
        log_info "  sudo journalctl -u restaurant-* -n 50"
        exit 1
    fi
}

# 运行主函数
main
