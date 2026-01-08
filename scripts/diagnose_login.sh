#!/bin/bash

echo "======================================"
echo "🔍 登录系统诊断工具"
echo "======================================"
echo ""

# 检查 HTTP 服务器
echo "1️⃣  检查 HTTP 服务器状态..."
if pgrep -f "python.*http.server.*8080" > /dev/null; then
    echo "✅ HTTP 服务器正在运行 (端口 8080)"
else
    echo "❌ HTTP 服务器未运行"
    echo "   启动命令: python3 -m http.server 8080 --directory assets"
fi
echo ""

# 检查配置文件
echo "2️⃣  检查配置文件..."
if [ -f "assets/config/users.json" ]; then
    echo "✅ 配置文件存在: assets/config/users.json"
    USER_COUNT=$(cat assets/config/users.json | grep -c "username")
    echo "   用户数量: $((USER_COUNT))"
else
    echo "❌ 配置文件不存在: assets/config/users.json"
fi
echo ""

# 检查登录页面
echo "3️⃣  检查登录页面..."
if [ -f "assets/login.html" ]; then
    echo "✅ 登录页面存在: assets/login.html"
else
    echo "❌ 登录页面不存在: assets/login.html"
fi
echo ""

# 检查测试页面
echo "4️⃣  检查测试页面..."
if [ -f "assets/test_login.html" ]; then
    echo "✅ 测试页面存在: assets/test_login.html"
else
    echo "❌ 测试页面不存在: assets/test_login.html"
fi
echo ""

# 测试 HTTP 访问
echo "5️⃣  测试 HTTP 访问..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/config/users.json | grep -q "200"; then
    echo "✅ 配置文件可通过 HTTP 访问"
else
    echo "❌ 配置文件无法通过 HTTP 访问"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/login.html | grep -q "200"; then
    echo "✅ 登录页面可通过 HTTP 访问"
else
    echo "❌ 登录页面无法通过 HTTP 访问"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/test_login.html | grep -q "200"; then
    echo "✅ 测试页面可通过 HTTP 访问"
else
    echo "❌ 测试页面无法通过 HTTP 访问"
fi
echo ""

# 显示测试账号
echo "6️⃣  可用的测试账号："
echo ""
if [ -f "assets/config/users.json" ]; then
    echo "| 角色              | 用户名        | 密码          |"
    echo "|-------------------|---------------|---------------|"
    grep -A 3 '"username"' assets/config/users.json | grep -E '"username"|"password"|"icon"|"zh"' | paste - - - | \
        awk -F'"' '{ printf "| %-17s | %-13s | %-13s |\n", $8, $4, $4 }' | head -6
fi
echo ""

echo "======================================"
echo "🚀 快速测试链接"
echo "======================================"
echo ""
echo "📱 原始登录页面："
echo "   http://localhost:8080/login.html"
echo ""
echo "🧪 简化测试页面（推荐）："
echo "   http://localhost:8080/test_login.html"
echo ""
echo "📄 配置文件查看："
echo "   http://localhost:8080/config/users.json"
echo ""
echo "======================================"
echo "💡 使用建议"
echo "======================================"
echo ""
echo "1. 优先使用测试页面（test_login.html）进行快速诊断"
echo "2. 如果测试页面可以登录，说明配置和服务器都正常"
echo "3. 如果测试页面无法登录，请查看上面的检查结果"
echo "4. 如遇问题，请参考 LOGIN_TROUBLESHOOTING.md 文档"
echo ""
echo "======================================"
