#!/bin/bash

echo "=========================================="
echo "餐饮点餐系统 - 服务诊断工具"
echo "=========================================="
echo ""

echo "1. 检查正在运行的服务..."
echo "----------------------------------------"
ps aux | grep -E "(python.*uvicorn|python.*http.server)" | grep -v grep | grep -v grep | while read line; do
    echo "✓ $line"
done
echo ""

echo "2. 检查端口监听状态..."
echo "----------------------------------------"
for port in 5000 8000 8080; do
    if lsof -i :$port >/dev/null 2>&1; then
        echo "✓ 端口 $port 正在监听"
    else
        echo "✗ 端口 $port 未监听"
    fi
done
echo ""

echo "3. 测试API连接..."
echo "----------------------------------------"
echo -n "API服务 (8000): "
if curl -s http://localhost:8000/ >/dev/null 2>&1; then
    echo "✓ 可访问"
else
    echo "✗ 无法访问"
fi

echo -n "测试页面 (8080): "
if curl -s http://localhost:8080/assets/restaurant_full_test.html >/dev/null 2>&1; then
    echo "✓ 可访问"
else
    echo "✗ 无法访问"
fi
echo ""

echo "4. 网络接口信息..."
echo "----------------------------------------"
ip addr show | grep "inet " | grep -v "127.0.0.1" | head -n 3
echo ""

echo "=========================================="
echo "诊断完成"
echo "=========================================="
echo ""
echo "推荐的访问方式："
echo "1. 如果在同一台机器上："
echo "   - 测试页面: http://localhost:8080/assets/restaurant_full_test.html"
echo "   - API文档: http://localhost:8000/docs"
echo ""
echo "2. 如果从其他机器访问，使用以下IP地址之一："
for ip in $(ip addr show | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' | cut -d'/' -f1); do
    echo "   - http://$ip:8080/assets/restaurant_full_test.html"
done
echo ""
