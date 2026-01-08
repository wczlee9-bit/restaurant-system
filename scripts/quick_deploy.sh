#!/bin/bash

# Netlify 快速部署脚本
# 用于快速配置 Git 远程仓库并推送到 Netlify

set -e

echo "========================================"
echo "Netlify 快速部署脚本"
echo "========================================"
echo ""

# 检查是否已经配置了远程仓库
if git remote get-url origin &>/dev/null; then
    echo "✓ 已检测到 Git 远程仓库:"
    git remote get-url origin
    echo ""

    # 询问是否直接推送
    read -p "是否直接推送到远程仓库? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在推送到远程仓库..."
        git push origin main
        echo "✓ 推送成功！"
        echo ""
        echo "请在 Netlify 控制台查看部署状态"
        echo "部署成功后访问: https://restaurant-system.netlify.app/login"
        exit 0
    else
        echo "请手动执行: git push origin main"
        exit 0
    fi
else
    echo "未配置 Git 远程仓库"
    echo ""
    echo "请按照以下步骤操作:"
    echo ""
    echo "1. 创建 GitHub 仓库"
    echo "   - 访问 https://github.com/new"
    echo "   - 创建一个新的空仓库"
    echo ""
    echo "2. 添加远程仓库"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo "   或者使用 SSH:"
    echo "   git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git"
    echo ""
    echo "3. 推送代码"
    echo "   git push origin main"
    echo ""
    echo "4. 连接到 Netlify"
    echo "   - 访问 https://app.netlify.com"
    echo "   - 点击 'Add new site' > 'Import an existing project'"
    echo "   - 选择 GitHub 并授权"
    echo "   - 选择你的仓库"
    echo "   - 配置构建设置:"
    echo "     - Publish directory: assets"
    echo "     - Build command: (留空)"
    echo "   - 点击 'Deploy site'"
    echo ""
    echo "========================================"
    echo "需要帮助? 查看 NETLIFY_404_FIX.md"
    echo "========================================"
fi
