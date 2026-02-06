#!/bin/bash

###############################################################################
# 腾讯云系统模块化迁移脚本
# 作用：快速完成从现有系统到模块化架构的迁移
###############################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
SERVER_IP="129.226.196.76"
PROJECT_DIR="/opt/restaurant-system"
BACKUP_DIR="/tmp"
GITEE_REPO="https://gitee.com/your-username/restaurant-system.git"

###############################################################################
# 函数定义
###############################################################################

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
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

###############################################################################
# 步骤1：检查环境
###############################################################################

check_environment() {
    print_header "步骤1: 检查环境"
    
    # 检查是否在正确的目录
    if [ ! -f "modular_main.py" ]; then
        print_error "未找到 modular_main.py，请确保在项目根目录"
        exit 1
    fi
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        print_error "未找到 Python3"
        exit 1
    fi
    
    # 检查 Git
    if ! command -v git &> /dev/null; then
        print_error "未找到 Git"
        exit 1
    fi
    
    print_success "环境检查通过"
}

###############################################################################
# 步骤2：备份现有系统（在服务器上）
###############################################################################

backup_server() {
    print_header "步骤2: 备份腾讯云现有系统"
    
    print_info "正在连接到服务器..."
    
    ssh root@${SERVER_IP} << 'ENDSSH'
        echo "开始备份..."
        
        # 进入项目目录
        cd ${PROJECT_DIR}
        
        # 备份代码
        BACKUP_FILE="${BACKUP_DIR}/restaurant-system-backup-$(date +%Y%m%d_%H%M%S).tar.gz"
        tar -czf ${BACKUP_FILE} .
        
        if [ $? -eq 0 ]; then
            echo "代码备份成功: ${BACKUP_FILE}"
            ls -lh ${BACKUP_FILE}
        else
            echo "代码备份失败"
            exit 1
        fi
        
        # 备份数据库
        DB_BACKUP_FILE="${BACKUP_DIR}/restaurant-db-backup-$(date +%Y%m%d_%H%M%S).sql"
        PGPASSWORD='restaurant_pass_2024' pg_dump -h localhost -U restaurant_user -d restaurant_db > ${DB_BACKUP_FILE}
        
        if [ $? -eq 0 ]; then
            echo "数据库备份成功: ${DB_BACKUP_FILE}"
            ls -lh ${DB_BACKUP_FILE}
        else
            echo "数据库备份失败"
            exit 1
        fi
        
        echo "备份完成！"
ENDSSH

    if [ $? -eq 0 ]; then
        print_success "服务器备份完成"
    else
        print_error "服务器备份失败"
        exit 1
    fi
}

###############################################################################
# 步骤3：推送到 Gitee
###############################################################################

push_to_gitee() {
    print_header "步骤3: 推送到 Gitee"
    
    # 检查是否已初始化 Git
    if [ ! -d ".git" ]; then
        print_info "初始化 Git 仓库..."
        git init
        git remote add origin ${GITEE_REPO}
    fi
    
    # 添加所有文件
    print_info "添加文件到 Git..."
    git add .
    
    # 提交
    print_info "提交代码..."
    git commit -m "feat: 模块化架构迁移 - $(date '+%Y-%m-%d %H:%M:%S')"
    
    # 推送
    print_info "推送到 Gitee..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        print_success "推送到 Gitee 成功"
    else
        print_error "推送到 Gitee 失败"
        print_info "请检查 Gitee 仓库地址是否正确"
        exit 1
    fi
}

###############################################################################
# 步骤4：部署到腾讯云
###############################################################################

deploy_to_server() {
    print_header "步骤4: 部署到腾讯云"
    
    ssh root@${SERVER_IP} << 'ENDSSH'
        echo "开始部署..."
        
        # 进入项目目录
        cd ${PROJECT_DIR}
        
        # 备份当前代码（快速备份）
        if [ -d ".git" ]; then
            cp -r . ../restaurant-system.git-backup.$(date +%Y%m%d_%H%M%S)
            echo "Git 备份完成"
        fi
        
        # 拉取最新代码
        echo "正在从 Gitee 拉取代码..."
        git pull origin main
        
        if [ $? -ne 0 ]; then
            echo "拉取代码失败"
            echo "正在回滚..."
            if [ -d "../restaurant-system.git-backup.$(date +%Y%m%d_%H%M%S)" ]; then
                rm -rf *
                cp -r ../restaurant-system.git-backup.$(date +%Y%m%d_%H%M%S)/* .
                echo "回滚完成"
            fi
            exit 1
        fi
        
        echo "拉取代码成功"
        
        # 安装依赖
        echo "安装 Python 依赖..."
        pip install -r requirements.txt -q
        
        # 构建前端
        echo "构建前端..."
        cd frontend
        npm install -q
        npm run build
        cd ..
        
        # 构建管理后台
        echo "构建管理后台..."
        cd admin
        npm install -q
        npm run build
        cd ..
        
        # 停止旧服务
        echo "停止旧服务..."
        pkill -f "uvicorn"
        sleep 5
        
        # 启动新服务
        echo "启动新服务..."
        export PYTHONPATH=${PROJECT_DIR}/src:${PROJECT_DIR}/backend_extensions/src:$PYTHONPATH
        nohup python3 modular_main.py > /tmp/app.log 2>&1 &
        
        sleep 3
        
        # 检查服务
        if ps aux | grep -v grep | grep uvicorn > /dev/null; then
            echo "服务启动成功"
        else
            echo "服务启动失败"
            tail -20 /tmp/app.log
            exit 1
        fi
        
        # 健康检查
        sleep 2
        RESPONSE=$(curl -s http://localhost:8001/health)
        if [ $? -eq 0 ]; then
            echo "健康检查通过"
            echo "响应: ${RESPONSE}"
        else
            echo "健康检查失败"
            exit 1
        fi
        
        echo "部署完成！"
ENDSSH

    if [ $? -eq 0 ]; then
        print_success "部署到腾讯云成功"
    else
        print_error "部署到腾讯云失败"
        print_info "请查看服务器日志：/tmp/app.log"
        exit 1
    fi
}

###############################################################################
# 步骤5：验证部署
###############################################################################

verify_deployment() {
    print_header "步骤5: 验证部署"
    
    print_info "检查服务状态..."
    ssh root@${SERVER_IP} "curl -s http://localhost:8001/health"
    
    echo ""
    print_info "检查模块..."
    ssh root@${SERVER_IP} "curl -s http://localhost:8001/modules"
    
    echo ""
    print_info "检查 API..."
    ssh root@${SERVER_IP} "curl -s http://localhost:8001/api/menu/?store_id=1"
    
    echo ""
    print_success "验证完成"
}

###############################################################################
# 主流程
###############################################################################

main() {
    print_header "腾讯云系统模块化迁移"
    
    # 确认
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 0
    fi
    
    # 执行步骤
    check_environment
    backup_server
    push_to_gitee
    deploy_to_server
    verify_deployment
    
    # 完成
    print_header "迁移完成！"
    print_success "所有步骤已完成"
    print_info "访问地址："
    echo "  - 点餐页面: http://${SERVER_IP}/?table=1&store=1"
    echo "  - 管理后台: http://${SERVER_IP}/admin"
    echo "  - API 文档: http://${SERVER_IP}/docs"
    echo "  - 健康检查: http://${SERVER_IP}/health"
    echo "  - 模块列表: http://${SERVER_IP}/modules"
}

###############################################################################
# 执行主函数
###############################################################################

main "$@"
