#!/bin/bash
# ========================================
# 部署后快速验证脚本
# ========================================

echo "========================================"
echo "餐饮点餐系统 - 部署后验证"
echo "========================================"

# 配置
API_BASE_URL="http://9.128.251.82"  # 修改为你的实际 API 地址
FRONTEND_URL=""  # Netlify 部署完成后，填写你的 Netlify URL

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数器
PASSED=0
FAILED=0

# 测试函数
test_api() {
    local name="$1"
    local url="$2"
    local expected_code="${3:-200}"

    echo -n "测试 $name ... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" --max-time 5)
    
    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✓ 通过${NC} (HTTP $response)"
        ((PASSED++))
    else
        echo -e "${RED}✗ 失败${NC} (HTTP $response, 期望 $expected_code)"
        ((FAILED++))
    fi
}

# 显示 API 地址
echo ""
echo -e "${YELLOW}API 基础地址: $API_BASE_URL${NC}"
echo ""

# ========================================
# 1. 后端 API 测试
# ========================================
echo "========================================"
echo "1. 后端 API 测试"
echo "========================================"

# 测试主 API (8000)
test_api "主 API 健康检查" "$API_BASE_URL:8000/"
test_api "菜单 API" "$API_BASE_URL:8000/api/menu/1"

# 测试顾客 API (8001)
test_api "顾客 API 健康检查" "$API_BASE_URL:8001/"
test_api "订单 API" "$API_BASE_URL:8001/api/orders"

# 测试会员 API (8004)
test_api "会员 API 健康检查" "$API_BASE_URL:8004/"
test_api "会员等级 API" "$API_BASE_URL:8004/api/member/levels"

# 测试总公司管理 API (8006)
test_api "总公司管理 API 健康检查" "$API_BASE_URL:8006/"
test_api "总体统计 API" "$API_BASE_URL:8006/api/headquarters/overall-stats"
test_api "店铺列表 API" "$API_BASE_URL:8006/api/headquarters/stores"
test_api "会员统计 API" "$API_BASE_URL:8006/api/headquarters/members"

# ========================================
# 2. 数据库连接测试
# ========================================
echo ""
echo "========================================"
echo "2. 数据库连接测试"
echo "========================================"

test_api "店铺数据查询" "$API_BASE_URL:8006/api/headquarters/stores?limit=1"

# ========================================
# 3. 前端页面测试
# ========================================
echo ""
echo "========================================"
echo "3. 前端页面测试"
echo "========================================"

if [ -z "$FRONTEND_URL" ]; then
    echo -e "${YELLOW}⚠ 请先设置 FRONTEND_URL 变量${NC}"
    echo "示例: export FRONTEND_URL='https://your-site.netlify.app'"
else
    test_api "门户页面" "$FRONTEND_URL/"
    test_api "会员中心页面" "$FRONTEND_URL/member_center.html"
    test_api "总公司后台页面" "$FRONTEND_URL/headquarters_dashboard.html"
fi

# ========================================
# 4. 功能测试
# ========================================
echo ""
echo "========================================"
echo "4. 功能测试"
echo "========================================"

# 注册测试会员
echo -n "测试注册会员 ... "
response=$(curl -s -X POST "$API_BASE_URL:8004/api/member/register" \
    -H "Content-Type: application/json" \
    -d '{"phone":"13900139000","name":"部署测试会员"}')

if echo "$response" | grep -q '"id"'; then
    echo -e "${GREEN}✓ 通过${NC}"
    ((PASSED++))
    
    # 提取会员 ID
    MEMBER_ID=$(echo "$response" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
    
    # 测试获取会员信息
    test_api "获取会员信息" "$API_BASE_URL:8004/api/member/$MEMBER_ID"
    
    # 测试获取会员订单
    test_api "获取会员订单" "$API_BASE_URL:8004/api/member/$MEMBER_ID/orders"
else
    echo -e "${RED}✗ 失败${NC}"
    echo "响应: $response"
    ((FAILED++))
fi

# 测试获取总体统计
echo -n "测试获取总体统计 ... "
response=$(curl -s "$API_BASE_URL:8006/api/headquarters/overall-stats")

if echo "$response" | grep -q '"total_stores"'; then
    echo -e "${GREEN}✓ 通过${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ 失败${NC}"
    echo "响应: $response"
    ((FAILED++))
fi

# ========================================
# 测试结果汇总
# ========================================
echo ""
echo "========================================"
echo "测试结果汇总"
echo "========================================"
echo -e "通过: ${GREEN}$PASSED${NC}"
echo -e "失败: ${RED}$FAILED${NC}"
echo "总计: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！系统部署成功。${NC}"
    exit 0
else
    echo -e "${RED}✗ 部分测试失败，请检查上述错误。${NC}"
    exit 1
fi
