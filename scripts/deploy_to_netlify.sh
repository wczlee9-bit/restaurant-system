#!/bin/bash

# ============================================
# 🚀 餐饮系统 - Netlify 快速部署脚本
# ============================================

echo "======================================================"
echo "🍽️ 多店铺扫码点餐系统 - Netlify 部署工具"
echo "======================================================"
echo ""

# 检查当前目录
if [ ! -f "netlify.toml" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

echo "📋 步骤 1/4: 准备部署文件"
echo "------------------------------------------------------"

# 创建部署目录
DEPLOY_DIR="deploy_temp"

# 如果目录已存在，先清理
if [ -d "$DEPLOY_DIR" ]; then
    echo "🧹 清理旧的部署目录..."
    rm -rf "$DEPLOY_DIR"
fi

echo "📁 创建部署目录: $DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# 复制 assets 目录
echo "📋 复制前端文件..."
cp -r assets "$DEPLOY_DIR/"

# 复制配置文件
echo "⚙️  复制 Netlify 配置..."
cp netlify.toml "$DEPLOY_DIR/"

# 复制部署文档
echo "📄 复制部署文档..."
cp DEPLOYMENT_GUIDE.md "$DEPLOY_DIR/" 2>/dev/null || echo "⚠️  DEPLOYMENT_GUIDE.md 不存在，跳过"

echo "✅ 文件准备完成！"
echo ""

echo "📋 步骤 2/4: 检查部署文件"
echo "------------------------------------------------------"

# 统计文件数量
HTML_COUNT=$(find "$DEPLOY_DIR/assets" -name "*.html" | wc -l)
JS_COUNT=$(find "$DEPLOY_DIR/assets" -name "*.js" | wc -l)
CSS_COUNT=$(find "$DEPLOY_DIR/assets" -name "*.css" | wc -l)

echo "📊 统计信息："
echo "   - HTML 文件: $HTML_COUNT 个"
echo "   - JavaScript 文件: $JS_COUNT 个"
echo "   - CSS 文件: $CSS_COUNT 个"
echo ""

echo "📋 步骤 3/4: 创建压缩包"
echo "------------------------------------------------------"

# 创建压缩包
ZIP_NAME="restaurant-system-$(date +%Y%m%d-%H%M%S).zip"
echo "📦 创建压缩包: $ZIP_NAME"

# 进入部署目录并压缩
cd "$DEPLOY_DIR"
zip -r "../$ZIP_NAME" . -x "*.git*" "*.DS_Store*" "__MACOSX/*" >/dev/null
cd ..

# 获取压缩包大小
ZIP_SIZE=$(du -h "$ZIP_NAME" | cut -f1)

echo "✅ 压缩包创建完成！大小: $ZIP_SIZE"
echo ""

echo "📋 步骤 4/4: 部署指引"
echo "------------------------------------------------------"
echo ""
echo "🚀 现在您有两个选择："
echo ""
echo "方法 A: 拖拽部署（推荐，最简单）"
echo "   1. 访问 https://app.netlify.com/"
echo "   2. 登录并点击 'Add new site' → 'Deploy manually'"
echo "   3. 将 '$DEPLOY_DIR' 文件夹拖拽到上传区域"
echo "   4. 等待 1-2 分钟，部署完成！"
echo ""
echo "方法 B: Git 集成部署（推荐用于持续更新）"
echo "   1. git add ."
echo "   2. git commit -m 'update: 部署餐饮系统到 Netlify'"
echo "   3. git push"
echo "   4. 在 Netlify 中连接 GitHub 仓库"
echo ""

echo "📌 部署后别忘了启动后端服务！"
echo "   python scripts/start_restaurant_api.py"
echo ""

echo "======================================================"
echo "✅ 部署准备工作完成！"
echo "======================================================"
echo ""
echo "💡 提示：查看 DEPLOYMENT_GUIDE.md 获取详细部署说明"
echo ""
