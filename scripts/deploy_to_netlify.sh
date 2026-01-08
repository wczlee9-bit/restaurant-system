#!/bin/bash

echo "======================================"
echo "🚀 Netlify 快速部署指南"
echo "======================================"
echo ""

# 检查 Git 状态
echo "📋 当前 Git 状态："
echo ""
git status --short

echo ""
echo "======================================"
echo "🔧 可执行的操作"
echo "======================================"
echo ""
echo "1) 提交所有更改并推送到 Netlify"
echo "2) 仅提交登录相关更改"
echo "3) 查看部署说明"
echo "4) 退出"
echo ""

read -p "请选择操作 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "正在提交所有更改..."
        echo ""
        
        git add .
        
        # 检查是否有更改
        if git diff --cached --quiet; then
            echo "❌ 没有需要提交的更改"
            exit 1
        fi
        
        git commit -m "fix: 修复 Netlify 登录问题，替换 CDN 为 unpkg"
        echo "✅ 提交完成"
        echo ""
        
        git push
        echo "✅ 推送完成"
        echo ""
        echo "📊 Netlify 将自动部署..."
        echo "   请访问 Netlify Dashboard 查看部署状态"
        echo "   https://app.netlify.com/sites/restaurant-system/deploys"
        echo ""
        ;;
    
    2)
        echo ""
        echo "正在提交登录相关更改..."
        echo ""
        
        git add login.html login_standalone.html netlify.toml
        
        git commit -m "fix: 使用独立登录页面解决 Netlify 部署问题"
        echo "✅ 提交完成"
        echo ""
        
        git push
        echo "✅ 推送完成"
        echo ""
        echo "📊 Netlify 将自动部署..."
        echo ""
        ;;
    
    3)
        echo ""
        echo "======================================"
        echo "📚 部署说明"
        echo "======================================"
        echo ""
        echo "✅ 已完成的修复："
        echo ""
        echo "1. 创建了独立登录页面（login_standalone.html）"
        echo "   - 用户数据内联到页面中"
        echo "   - 不依赖外部配置文件"
        echo "   - 使用 unpkg CDN（更稳定）"
        echo ""
        echo "2. 替换了所有 HTML 文件的 CDN"
        echo "   - 从 jsdelivr 替换为 unpkg"
        echo "   - 提高了资源加载的稳定性"
        echo ""
        echo "3. 创建了 Netlify 配置文件（netlify.toml）"
        echo "   - 配置了重定向规则"
        echo "   - 优化了缓存策略"
        echo "   - 添加了安全头部"
        echo ""
        echo "🚀 下一步："
        echo ""
        echo "1. 将更改推送到 Git"
        echo "   git add ."
        echo "   git commit -m \"fix: 修复 Netlify 登录问题\""
        echo "   git push"
        echo ""
        echo "2. Netlify 会自动检测到更改并重新部署"
        echo "   - 等待 1-2 分钟"
        echo "   - 访问 Netlify Dashboard 查看部署状态"
        echo ""
        echo "3. 部署完成后测试："
        echo "   - 访问: https://restaurant-system.netlify.app/login"
        echo "   - 点击任意演示账号卡片"
        echo "   - 查看登录是否成功"
        echo ""
        echo "📱 测试账号："
        echo ""
        echo "| 角色          | 用户名        | 密码          |"
        echo "|---------------|---------------|---------------|"
        echo "| 系统管理员    | system_admin  | admin123      |"
        echo "| 总公司        | company       | company123    |"
        echo "| 店长          | admin         | admin123      |"
        echo "| 厨师          | chef          | chef123       |"
        echo "| 传菜员        | waiter        | waiter123     |"
        echo "| 收银员        | cashier       | cashier123    |"
        echo ""
        echo "🔍 如果仍有问题："
        echo ""
        echo "1. 按 F12 打开浏览器开发者工具"
        echo "2. 查看 Console 标签的错误信息"
        echo "3. 查看 Network 标签的资源加载情况"
        echo "4. 参考 NETLIFY_LOGIN_FIX.md 文档"
        echo ""
        ;;
    
    4)
        echo "退出"
        exit 0
        ;;
    
    *)
        echo "无效的选择"
        exit 1
        ;;
esac

echo ""
echo "======================================"
echo "✅ 操作完成"
echo "======================================"
echo ""
