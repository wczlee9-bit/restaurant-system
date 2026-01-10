#!/bin/bash

# 服务器连接检查脚本

SERVER_IP="115.191.1.219"

echo "=========================================="
echo "检查服务器连接状态"
echo "服务器: $SERVER_IP"
echo "=========================================="

echo -e "\n1. 检查网络连通性..."
if ping -c 3 $SERVER_IP > /dev/null 2>&1; then
    echo "✓ 服务器可以ping通"
else
    echo "✗ 服务器无法ping通"
    exit 1
fi

echo -e "\n2. 检查SSH连接..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes root@$SERVER_IP "echo 'SSH连接成功'" 2>/dev/null; then
    echo "✓ SSH连接正常"
else
    echo "⚠  SSH连接可能需要密码或密钥"
    echo "  请确保你有权限访问服务器"
fi

echo -e "\n3. 检查服务器已开放的端口..."
for port in 80 443 8000 8001 8004 8006 8007; do
    if nc -z -w2 $SERVER_IP $port 2>/dev/null; then
        echo "✓ 端口 $port 已开放"
    else
        echo "✗ 端口 $port 未开放或连接被拒绝"
    fi
done

echo -e "\n4. 检查Nginx是否运行..."
if curl -s -o /dev/null -w "%{http_code}" http://$SERVER_IP/ 2>/dev/null | grep -q "200\|403\|404"; then
    echo "✓ Nginx正在运行"
else
    echo "⚠  Nginx未运行或未安装"
fi

echo -e "\n=========================================="
echo "检查完成"
echo "=========================================="
