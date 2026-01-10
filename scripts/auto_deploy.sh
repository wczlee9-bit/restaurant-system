#!/bin/bash
# 自动化部署脚本 - GitHub Actions 调用
# 在服务器上执行代码拉取、依赖更新、服务重启

set -e  # 遇到错误立即退出

PROJECT_PATH="/workspace/projects"
VENV_PATH="${PROJECT_PATH}/venv"
LOG_PATH="${PROJECT_PATH}/logs"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查并创建虚拟环境
setup_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        log_info "创建 Python 虚拟环境..."
        python3 -m venv "$VENV_PATH"
    fi
    source "$VENV_PATH/bin/activate"
}

# 更新依赖
update_dependencies() {
    log_info "更新 Python 依赖..."
    pip install --upgrade pip --quiet
    pip install -r "${PROJECT_PATH}/requirements.txt" --quiet
}

# 停止现有服务
stop_services() {
    log_info "停止现有服务..."
    
    # 尝试使用 systemd 停止
    systemctl --user stop restaurant-api 2>/dev/null || true
    systemctl --user stop restaurant-enhanced-api 2>/dev/null || true
    systemctl --user stop member-api 2>/dev/null || true
    systemctl --user stop headquarters-api 2>/dev/null || true
    systemctl --user stop settlement-api 2>/dev/null || true
    systemctl --user stop websocket-api 2>/dev/null || true
    
    # 如果 systemd 不可用，使用 pkill 停止
    sleep 2
    pkill -f "uvicorn.*restaurant_api" 2>/dev/null || true
    pkill -f "uvicorn.*restaurant_enhanced_api" 2>/dev/null || true
    pkill -f "uvicorn.*member_api" 2>/dev/null || true
    pkill -f "uvicorn.*headquarters_api" 2>/dev/null || true
    pkill -f "uvicorn.*settlement_api" 2>/dev/null || true
    pkill -f "uvicorn.*websocket_api" 2>/dev/null || true
}

# 启动服务
start_services() {
    log_info "启动 API 服务..."
    
    # 创建日志目录
    mkdir -p "$LOG_PATH"
    cd "$PROJECT_PATH"
    
    # 使用 systemd 或 nohup 启动服务
    if systemctl --user list-unit-files 2>/dev/null | grep -q "restaurant-api.service"; then
        log_info "使用 systemd 启动服务..."
        systemctl --user start restaurant-api
        systemctl --user start restaurant-enhanced-api
        systemctl --user start member-api
        systemctl --user start headquarters-api
        systemctl --user start settlement-api
        systemctl --user start websocket-api
    else
        log_info "使用 nohup 启动服务..."
        
        # 餐厅主 API (8000)
        nohup python -m uvicorn src.api.restaurant_api:app \
            --host 0.0.0.0 --port 8000 \
            > "$LOG_PATH/api.log" 2>&1 &
        
        # 增强 API (8007)
        nohup python -m uvicorn src.api.restaurant_enhanced_api:app \
            --host 0.0.0.0 --port 8007 \
            > "$LOG_PATH/enhanced_api.log" 2>&1 &
        
        # 会员 API (8001)
        nohup python -m uvicorn src.api.member_api:app \
            --host 0.0.0.0 --port 8001 \
            > "$LOG_PATH/member_api.log" 2>&1 &
        
        # 总公司 API (8004)
        nohup python -m uvicorn src.api.headquarters_api:app \
            --host 0.0.0.0 --port 8004 \
            > "$LOG_PATH/headquarters_api.log" 2>&1 &
        
        # 结算 API (8006)
        nohup python -m uvicorn src.api.settlement_api:app \
            --host 0.0.0.0 --port 8006 \
            > "$LOG_PATH/settlement_api.log" 2>&1 &
        
        # WebSocket API (8008)
        nohup python -m uvicorn src.api.websocket_api:app \
            --host 0.0.0.0 --port 8008 \
            > "$LOG_PATH/websocket.log" 2>&1 &
    fi
}

# 验证服务状态
verify_services() {
    log_info "等待服务启动..."
    sleep 5
    
    log_info "验证服务状态..."
    local ports=(8000 8001 8004 8006 8007 8008)
    local all_ok=true
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_info "✅ 端口 $port 运行正常"
        else
            log_error "❌ 端口 $port 启动失败"
            all_ok=false
        fi
    done
    
    if [ "$all_ok" = false ]; then
        log_error "部分服务启动失败，请检查日志"
        exit 1
    fi
    
    log_info "所有服务运行正常！"
}

# 备份重要文件
backup_files() {
    log_info "📦 备份重要文件..."
    
    BACKUP_DIR="${PROJECT_PATH}/.backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份配置文件
    [ -f "${PROJECT_PATH}/.env" ] && cp "${PROJECT_PATH}/.env" "$BACKUP_DIR/" 2>/dev/null || true
    [ -f "${PROJECT_PATH}/config/agent_llm_config.json" ] && cp "${PROJECT_PATH}/config/agent_llm_config.json" "$BACKUP_DIR/" 2>/dev/null || true
    
    log_info "备份完成: $BACKUP_DIR"
}

# 主函数
main() {
    log_info "========================================="
    log_info "🚀 开始自动部署..."
    log_info "========================================="
    
    cd "$PROJECT_PATH"
    
    # 备份重要文件
    backup_files
    
    # 拉取最新代码
    log_info "📥 拉取最新代码..."
    git fetch origin
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    git reset --hard origin/${CURRENT_BRANCH:-main}
    
    # 恢复配置文件
    log_info "📤 恢复配置文件..."
    [ -f "${BACKUP_DIR}/.env" ] && cp "$BACKUP_DIR/.env" "${PROJECT_PATH}/" 2>/dev/null || true
    [ -f "${BACKUP_DIR}/agent_llm_config.json" ] && cp "$BACKUP_DIR/agent_llm_config.json" "${PROJECT_PATH}/config/" 2>/dev/null || true
    
    # 更新依赖
    setup_venv
    update_dependencies
    
    # 重启服务
    stop_services
    start_services
    
    # 验证服务
    verify_services
    
    log_info "========================================="
    log_info "🎉 部署完成！"
    log_info "========================================="
    log_info "服务地址:"
    log_info "  - 餐厅 API:        http://localhost:8000"
    log_info "  - 增强 API:         http://localhost:8007"
    log_info "  - 会员 API:         http://localhost:8001"
    log_info "  - 总公司 API:       http://localhost:8004"
    log_info "  - 结算 API:         http://localhost:8006"
    log_info "  - WebSocket API:    http://localhost:8008"
    log_info "========================================="
}

main
