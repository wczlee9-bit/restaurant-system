#!/bin/bash
# GitHub Actions 配置验证脚本
# 用于检查 GitHub Actions 自动部署配置是否正确

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASS_COUNT=0
FAIL_COUNT=0

check_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASS_COUNT++))
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAIL_COUNT++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

check_info() {
    echo -e "${BLUE}ℹ️  INFO${NC}: $1"
}

echo "========================================="
echo "🔍 GitHub Actions 配置验证"
echo "========================================="
echo ""

# 1. 检查工作流文件
echo "1️⃣  检查 GitHub Actions 工作流文件..."
if [ -f ".github/workflows/deploy.yml" ]; then
    check_pass "工作流文件存在: .github/workflows/deploy.yml"
    
    # 检查工作流文件内容
    if grep -q "on:" .github/workflows/deploy.yml && \
       grep -q "branches:" .github/workflows/deploy.yml && \
       grep -q "workflow_dispatch:" .github/workflows/deploy.yml; then
        check_pass "工作流触发条件配置正确"
    else
        check_fail "工作流触发条件配置不正确"
    fi
    
    if grep -q "SSH_PRIVATE_KEY" .github/workflows/deploy.yml && \
       grep -q "SERVER_USER" .github/workflows/deploy.yml && \
       grep -q "SERVER_HOST" .github/workflows/deploy.yml; then
        check_pass "GitHub Secrets 引用配置正确"
    else
        check_fail "GitHub Secrets 引用配置不正确"
    fi
else
    check_fail "工作流文件不存在: .github/workflows/deploy.yml"
fi
echo ""

# 2. 检查自动部署脚本
echo "2️⃣  检查自动部署脚本..."
if [ -f "scripts/auto_deploy.sh" ]; then
    check_pass "自动部署脚本存在: scripts/auto_deploy.sh"
    
    # 检查脚本是否可执行
    if [ -x "scripts/auto_deploy.sh" ]; then
        check_pass "自动部署脚本有执行权限"
    else
        check_warn "自动部署脚本没有执行权限，建议运行: chmod +x scripts/auto_deploy.sh"
    fi
    
    # 检查脚本关键函数
    if grep -q "setup_venv" scripts/auto_deploy.sh && \
       grep -q "update_dependencies" scripts/auto_deploy.sh && \
       grep -q "stop_services" scripts/auto_deploy.sh && \
       grep -q "start_services" scripts/auto_deploy.sh && \
       grep -q "verify_services" scripts/auto_deploy.sh; then
        check_pass "自动部署脚本包含所有必要函数"
    else
        check_fail "自动部署脚本缺少必要的函数"
    fi
else
    check_fail "自动部署脚本不存在: scripts/auto_deploy.sh"
fi
echo ""

# 3. 检查 systemd 服务文件
echo "3️⃣  检查 systemd 服务配置文件..."
SERVICES=(
    "restaurant-api"
    "restaurant-enhanced-api"
    "member-api"
    "headquarters-api"
    "settlement-api"
    "websocket-api"
)

ALL_SERVICES_EXIST=true
for service in "${SERVICES[@]}"; do
    if [ -f "systemd/${service}.service" ]; then
        echo -e "   ${GREEN}✓${NC} ${service}.service"
    else
        echo -e "   ${RED}✗${NC} ${service}.service"
        ALL_SERVICES_EXIST=false
    fi
done

if [ "$ALL_SERVICES_EXIST" = true ]; then
    check_pass "所有 systemd 服务配置文件存在"
else
    check_fail "部分 systemd 服务配置文件缺失"
fi
echo ""

# 4. 检查 API 服务文件
echo "4️⃣  检查 API 服务文件..."
API_FILES=(
    "src/api/restaurant_api.py"
    "src/api/restaurant_enhanced_api.py"
    "src/api/member_api.py"
    "src/api/headquarters_api.py"
    "src/api/settlement_api.py"
    "src/api/websocket_api.py"
)

ALL_API_FILES_EXIST=true
for api_file in "${API_FILES[@]}"; do
    if [ -f "$api_file" ]; then
        echo -e "   ${GREEN}✓${NC} ${api_file}"
    else
        echo -e "   ${RED}✗${NC} ${api_file}"
        ALL_API_FILES_EXIST=false
    fi
done

if [ "$ALL_API_FILES_EXIST" = true ]; then
    check_pass "所有 API 服务文件存在"
else
    check_fail "部分 API 服务文件缺失"
fi
echo ""

# 5. 检查日志目录
echo "5️⃣  检查日志目录..."
if [ -d "logs" ]; then
    check_pass "日志目录存在"
else
    check_warn "日志目录不存在，部署脚本会自动创建"
fi
echo ""

# 6. 检查依赖文件
echo "6️⃣  检查依赖文件..."
if [ -f "requirements.txt" ]; then
    check_pass "requirements.txt 存在"
    
    # 检查关键依赖
    if grep -q "fastapi" requirements.txt && \
       grep -q "uvicorn" requirements.txt && \
       grep -q "sqlalchemy" requirements.txt; then
        check_pass "关键依赖已包含在 requirements.txt"
    else
        check_warn "requirements.txt 可能缺少关键依赖"
    fi
else
    check_fail "requirements.txt 不存在"
fi
echo ""

# 7. 检查文档文件
echo "7️⃣  检查文档文件..."
DOCS=(
    "GITHUB_SECRETS_SETUP.md"
    "GITHUB_ACTIONS_USAGE.md"
)

ALL_DOCS_EXIST=true
for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo -e "   ${GREEN}✓${NC} ${doc}"
    else
        echo -e "   ${RED}✗${NC} ${doc}"
        ALL_DOCS_EXIST=false
    fi
done

if [ "$ALL_DOCS_EXIST" = true ]; then
    check_pass "所有文档文件存在"
else
    check_warn "部分文档文件缺失（可选）"
fi
echo ""

# 8. 检查 .env 文件
echo "8️⃣  检查环境配置文件..."
if [ -f ".env" ]; then
    check_pass ".env 文件存在"
    
    # 检查关键环境变量
    if grep -q "DATABASE_URL" .env && \
       grep -q "S3_ACCESS_KEY" .env && \
       grep -q "S3_SECRET_KEY" .env; then
        check_pass ".env 包含关键环境变量"
    else
        check_warn ".env 可能缺少关键环境变量"
    fi
else
    check_warn ".env 文件不存在（需要在服务器上配置）"
fi
echo ""

# 9. 模拟 GitHub Secrets 检查
echo "9️⃣  GitHub Secrets 配置检查（需要在 GitHub 仓库中配置）..."
echo "   请确保在 GitHub 仓库中配置了以下 Secrets："
echo "   - SSH_PRIVATE_KEY"
echo "   - SERVER_USER"
echo "   - SERVER_HOST"
echo ""
check_info "GitHub Secrets 需要在 GitHub 网页上手动配置"
echo ""

# 10. 端口检查
echo "🔟 端口配置检查..."
PORTS=(8000 8001 8004 8006 8007 8008)
for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        check_warn "端口 $port 已被占用（部署前需要停止服务）"
    else
        echo -e "   ${GREEN}✓${NC} 端口 $port 可用"
    fi
done
echo ""

# 总结
echo "========================================="
echo "📊 验证结果汇总"
echo "========================================="
echo -e "通过: ${GREEN}${PASS_COUNT}${NC} 项"
echo -e "失败: ${RED}${FAIL_COUNT}${NC} 项"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}🎉 所有检查通过！GitHub Actions 配置正确。${NC}"
    echo ""
    echo "下一步："
    echo "1. 在 GitHub 仓库中配置 Secrets（参考 GITHUB_SECRETS_SETUP.md）"
    echo "2. 推送代码到 main 分支触发自动部署"
    echo "3. 或在 GitHub Actions 页面手动触发部署"
    exit 0
else
    echo -e "${RED}❌ 部分检查失败，请修复后再尝试部署。${NC}"
    echo ""
    echo "常见问题："
    echo "- 缺少必要的文件：检查项目目录结构"
    echo "- 文件没有执行权限：运行 chmod +x scripts/*.sh"
    echo "- 端口被占用：停止占用端口的服务或修改端口配置"
    exit 1
fi
