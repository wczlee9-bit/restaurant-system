#!/bin/bash

###############################################################################
# 从 Gitee 快速部署脚本
# 作用：从 Gitee 拉取代码并部署到腾讯云
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
GITEE_REPO="https://gitee.com/lijun75/restaurant.git"

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
# 主流程
###############################################################################

main() {
    print_header "从 Gitee 部署到腾讯云"
    
    # 在服务器上执行
    ssh root@${SERVER_IP} << 'ENDSSH'
        # 颜色定义
        GREEN='\033[0;32m'
        YELLOW='\033[1;33m'
        NC='\033[0m'
        
        echo -e "${YELLOW}========================================${NC}"
        echo -e "${YELLOW}  从 Gitee 部署到腾讯云${NC}"
        echo -e "${YELLOW}========================================${NC}"
        
        # 进入项目目录
        cd ${PROJECT_DIR}
        
        # 1. 拉取最新代码
        echo -e "\n${YELLOW}步骤1: 拉取最新代码${NC}"
        git pull origin main
        
        if [ $? -ne 0 ]; then
            echo -e "\033[0;31m❌ 拉取代码失败\033[0m"
            exit 1
        fi
        
        echo -e "${GREEN}✅ 代码拉取成功${NC}"
        
        # 2. 安装依赖
        echo -e "\n${YELLOW}步骤2: 安装依赖${NC}"
        pip install -r requirements.txt -q
        
        if [ $? -ne 0 ]; then
            echo -e "\033[0;31m❌ 依赖安装失败\033[0m"
            exit 1
        fi
        
        echo -e "${GREEN}✅ 依赖安装成功${NC}"
        
        # 3. 构建前端
        echo -e "\n${YELLOW}步骤3: 构建前端${NC}"
        cd frontend
        npm install -q
        npm run build
        
        if [ $? -ne 0 ]; then
            echo -e "\033[0;31m❌ 前端构建失败\033[0m"
            exit 1
        fi
        
        cd ..
        echo -e "${GREEN}✅ 前端构建成功${NC}"
        
        # 4. 构建管理后台
        echo -e "\n${YELLOW}步骤4: 构建管理后台${NC}"
        cd admin
        npm install -q
        npm run build
        
        if [ $? -ne 0 ]; then
            echo -e "\033[0;31m❌ 管理后台构建失败\033[0m"
            exit 1
        fi
        
        cd ..
        echo -e "${GREEN}✅ 管理后台构建成功${NC}"
        
        # 5. 停止旧服务
        echo -e "\n${YELLOW}步骤5: 停止旧服务${NC}"
        pkill -f "uvicorn"
        sleep 5
        echo -e "${GREEN}✅ 服务已停止${NC}"
        
        # 6. 启动新服务
        echo -e "\n${YELLOW}步骤6: 启动新服务${NC}"
        export PYTHONPATH=${PROJECT_DIR}/src:${PROJECT_DIR}/backend_extensions/src:$PYTHONPATH
        nohup python3 modular_main.py > /tmp/app.log 2>&1 &
        
        sleep 3
        
        if ps aux | grep -v grep | grep uvicorn > /dev/null; then
            echo -e "${GREEN}✅ 服务启动成功${NC}"
        else
            echo -e "\033[0;31m❌ 服务启动失败\033[0m"
            tail -20 /tmp/app.log
            exit 1
        fi
        
        # 7. 健康检查
        echo -e "\n${YELLOW}步骤7: 健康检查${NC}"
        sleep 2
        RESPONSE=$(curl -s http://localhost:8001/health)
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 健康检查通过${NC}"
            echo "响应: ${RESPONSE}"
        else
            echo -e "\033[0;31m❌ 健康检查失败\033[0m"
            exit 1
        fi
        
        # 8. 检查模块
        echo -e "\n${YELLOW}步骤8: 检查模块${NC}"
        MODULES=$(curl -s http://localhost:8001/modules)
        echo "模块列表:"
        echo "${MODULES}"
        
        echo -e "\n${GREEN}========================================${NC}"
        echo -e "${GREEN}  部署完成！${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo -e "${YELLOW}访问地址：${NC}"
        echo "  - 点餐页面: http://129.226.196.76/?table=1&store=1"
        echo "  - 管理后台: http://129.226.196.76/admin"
        echo "  - API 文档: http://129.226.196.76/docs"
        echo "  - 健康检查: http://129.226.196.76/health"
        echo "  - 模块列表: http://129.226.196.76/modules"
ENDSSH

    if [ $? -eq 0 ]; then
        print_success "部署成功！"
    else
        print_error "部署失败"
        exit 1
    fi
}

###############################################################################
# 执行主函数
###############################################################################

main "$@"
