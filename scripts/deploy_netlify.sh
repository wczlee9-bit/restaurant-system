#!/bin/bash

# 扫码点餐系统 - Netlify 部署脚本
# 使用方法: bash scripts/deploy_netlify.sh

set -e

echo "========================================="
echo "   扫码点餐系统 - Netlify 部署脚本"
echo "========================================="
echo ""

# 工作目录
WORK_DIR="${COZE_WORKSPACE_PATH:-/workspace/projects}"
cd "$WORK_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 步骤 1: 检查必要文件
echo -e "${YELLOW}[步骤 1/5]${NC} 检查必要文件..."

REQUIRED_FILES=("netlify.toml" "assets/index.html" "assets/restaurant_full_test.html")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo -e "${RED}✗ 错误: 缺少必要文件:${NC}"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

echo -e "${GREEN}✓${NC} 所有必要文件检查通过"
echo ""

# 步骤 2: 准备部署包
echo -e "${YELLOW}[步骤 2/5]${NC} 准备部署包..."

ZIP_FILE="restaurant-system.zip"

# 删除旧的zip文件
if [ -f "$ZIP_FILE" ]; then
    echo "  删除旧的部署包: $ZIP_FILE"
    rm -f "$ZIP_FILE"
fi

# 创建新的zip文件
echo "  创建部署包: $ZIP_FILE"
zip -r "$ZIP_FILE" assets/ netlify.toml README.md NETLIFY_DEPLOY.md > /dev/null

if [ $? -eq 0 ]; then
    FILE_SIZE=$(du -h "$ZIP_FILE" | cut -f1)
    echo -e "${GREEN}✓${NC} 部署包创建成功 (大小: $FILE_SIZE)"
else
    echo -e "${RED}✗ 错误: 部署包创建失败${NC}"
    exit 1
fi
echo ""

# 步骤 3: 检查 Netlify CLI
echo -e "${YELLOW}[步骤 3/5]${NC} 检查 Netlify CLI..."

if command -v netlify &> /dev/null; then
    NETLIFY_VERSION=$(netlify --version)
    echo -e "${GREEN}✓${NC} Netlify CLI 已安装 (版本: $NETLIFY_VERSION)"
    NETLIFY_CLI_AVAILABLE=true
else
    echo -e "${YELLOW}⚠${NC} Netlify CLI 未安装"
    echo ""
    echo "  安装方法:"
    echo "  1. npm install -g netlify-cli"
    echo "  2. 或访问: https://cli.netlify.com/"
    echo ""
    NETLIFY_CLI_AVAILABLE=false
fi
echo ""

# 步骤 4: 显示部署指南
echo -e "${YELLOW}[步骤 4/5]${NC} 部署指南"
echo ""

if [ "$NETLIFY_CLI_AVAILABLE" = true ]; then
    echo "  选项 A: 使用 Netlify CLI 自动部署"
    echo "  执行命令:"
    echo "    netlify deploy --prod --dir=assets"
    echo ""
fi

echo "  选项 B: 通过 Netlify Dashboard 手动部署"
echo "  步骤:"
echo "  1. 访问: https://app.netlify.com"
echo "  2. 登录您的账号"
echo "  3. 点击 'Add new site' → 'Deploy manually'"
echo "  4. 上传文件: $WORK_DIR/$ZIP_FILE"
echo "  5. 等待部署完成（1-2分钟）"
echo ""

echo "  选项 C: 通过 Git 仓库部署"
echo "  步骤:"
echo "  1. 将项目推送到 GitHub/GitLab"
echo "  2. 在 Netlify 中连接仓库"
echo "  3. 配置构建设置:"
echo "     - Build command: (留空)"
echo "     - Publish directory: assets"
echo ""

# 步骤 5: 显示重要提示
echo -e "${YELLOW}[步骤 5/5]${NC} 重要提示"
echo ""

echo "  📝 配置 API 地址"
echo "  部署后，需要确认 API 地址配置正确:"
echo "  - 云端 API: http://9.128.251.82:8000"
echo "  - 或: http://169.254.100.163:8000"
echo ""

echo "  🔒 安全建议"
echo "  - 生产环境应配置 CORS 限制"
echo "  - 启用 HTTPS（Netlify 默认提供）"
echo "  - 定期更新依赖库"
echo ""

echo "  📊 验证部署"
echo "  部署后，请测试:"
echo "  1. 访问主页是否正常"
echo "  2. API 请求是否成功"
echo "  3. 点餐流程是否完整"
echo "  4. 不同角色切换是否正常"
echo ""

# 显示总结
echo "========================================="
echo "  部署准备完成！"
echo "========================================="
echo ""
echo "  📦 部署包位置: $WORK_DIR/$ZIP_FILE"
echo "  📄 部署指南: $WORK_DIR/NETLIFY_DEPLOY.md"
echo ""
echo "  下一步操作:"
echo "  1. 参考 NETLIFY_DEPLOY.md 进行部署"
echo "  2. 或使用 Netlify CLI: netlify deploy --prod --dir=assets"
echo ""

# 询问是否立即部署
if [ "$NETLIFY_CLI_AVAILABLE" = true ]; then
    read -p "是否立即开始部署? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "开始部署到 Netlify..."
        echo ""
        cd "$WORK_DIR"
        netlify deploy --prod --dir=assets

        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✓${NC} 部署成功！"
            echo ""
            echo "请访问 Netlify 提供的 URL 查看您的网站"
        else
            echo ""
            echo -e "${RED}✗ 部署失败，请检查错误信息${NC}"
            exit 1
        fi
    else
        echo ""
        echo "已取消自动部署。您可以稍后手动部署。"
        echo ""
    fi
else
    echo ""
    echo "准备好后，请参考 NETLIFY_DEPLOY.md 进行部署。"
    echo ""
fi

echo "========================================="
echo ""
