#!/bin/bash
# 扫码点餐前端 - 自动部署脚本

set -e

echo "=========================================="
echo "🚀 扫码点餐前端 - 自动部署脚本"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Node.js
echo "📦 检查 Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js 未安装，正在安装...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
else
    echo -e "${GREEN}✅ Node.js 已安装: $(node -v)${NC}"
fi

echo ""
echo "📦 安装项目依赖..."
cd /opt/restaurant-system/frontend
npm install

echo ""
echo "🔨 构建生产版本..."
npm run build

echo ""
echo "✅ 构建完成！"
echo ""
echo "📁 构建产物位置："
ls -lh dist/

echo ""
echo "🔄 重启 Nginx..."
systemctl restart nginx

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 部署完成！${NC}"
echo "=========================================="
echo ""
echo "📱 访问地址："
echo "   扫码点餐: http://129.226.196.76/?table=1&store=1"
echo "   API 文档: http://129.226.196.76/docs"
echo ""
