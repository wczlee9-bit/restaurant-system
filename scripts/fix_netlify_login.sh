#!/bin/bash

echo "======================================"
echo "🚀 Netlify 登录问题修复工具"
echo "======================================"
echo ""

# 检查是否存在 login.html 备份
if [ -f "assets/login_backup.html" ]; then
    echo "⚠️  检测到备份文件：assets/login_backup.html"
    echo ""
fi

echo "📋 当前登录页面状态："
echo ""

# 检查登录页面文件
if [ -f "assets/login_standalone.html" ]; then
    echo "✅ 独立登录页面存在: assets/login_standalone.html"
else
    echo "❌ 独立登录页面不存在"
    exit 1
fi

if [ -f "assets/login.html" ]; then
    echo "✅ 当前登录页面存在: assets/login.html"
    # 检查是否是独立版本
    if grep -q "unpkg.com" assets/login.html; then
        echo "ℹ️  当前已是独立版本（使用 unpkg CDN）"
    else
        echo "ℹ️  当前是原始版本（使用 jsdelivr CDN）"
    fi
else
    echo "❌ 当前登录页面不存在"
    exit 1
fi

echo ""
echo "======================================"
echo "🔧 修复选项"
echo "======================================"
echo ""
echo "1) 备份当前登录页面并替换为独立版本"
echo "2) 恢复原始登录页面"
echo "3) 保留当前版本，不修改"
echo "4) 显示详细说明"
echo ""
read -p "请选择操作 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "正在备份当前登录页面..."
        cp assets/login.html assets/login_backup_$(date +%Y%m%d_%H%M%S).html
        echo "✅ 备份完成"
        
        echo ""
        echo "正在替换为独立版本..."
        cp assets/login_standalone.html assets/login.html
        echo "✅ 替换完成"
        
        echo ""
        echo "📋 下一步操作："
        echo "1. 提交到 Git:"
        echo "   git add assets/login.html"
        echo "   git commit -m \"fix: 使用独立登录页面解决 Netlify 部署问题\""
        echo "   git push"
        echo ""
        echo "2. Netlify 会自动检测到更改并重新部署"
        echo "3. 部署完成后测试: https://restaurant-system.netlify.app/login"
        echo ""
        ;;
    
    2)
        echo ""
        echo "正在恢复原始登录页面..."
        if [ -f "assets/login_backup.html" ]; then
            cp assets/login_backup.html assets/login.html
            echo "✅ 恢复完成"
        else
            echo "❌ 未找到备份文件"
            exit 1
        fi
        ;;
    
    3)
        echo ""
        echo "保留当前版本，不进行修改"
        ;;
    
    4)
        echo ""
        echo "======================================"
        echo "📚 详细说明"
        echo "======================================"
        echo ""
        echo "独立登录页面（login_standalone.html）的特点："
        echo "✅ 用户数据内联到页面中，不依赖外部配置文件"
        echo "✅ 使用 unpkg CDN（比 jsdelivr 更稳定）"
        echo "✅ 简化登录逻辑，只进行本地验证"
        echo "✅ 添加资源加载检测和错误提示"
        echo ""
        echo "原始登录页面（login.html）的特点："
        echo "✅ 支持从 config/users.json 加载用户数据"
        echo "✅ 支持 API 验证和本地验证双重模式"
        echo "❌ 依赖外部配置文件，可能在 Netlify 部署时丢失"
        echo ""
        echo "推荐使用场景："
        echo "- Netlify 部署：使用独立版本"
        echo "- 本地开发：可使用原始版本"
        echo ""
        ;;
    
    *)
        echo ""
        echo "无效的选择"
        exit 1
        ;;
esac

echo ""
echo "======================================"
echo "✅ 操作完成"
echo "======================================"
echo ""
echo "📱 测试链接："
echo ""
echo "本地测试："
echo "  http://localhost:8080/login.html"
echo "  http://localhost:8080/login_standalone.html"
echo ""
echo "生产测试："
echo "  https://restaurant-system.netlify.app/login"
echo ""
echo "📚 参考文档："
echo "  NETLIFY_LOGIN_FIX.md"
echo "======================================"
