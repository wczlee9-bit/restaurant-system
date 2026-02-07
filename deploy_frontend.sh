#!/bin/bash

# ==========================================
# 前端部署脚本 - 部署到腾讯云服务器
# ==========================================

echo "========================================="
echo "开始部署前端到腾讯云服务器"
echo "========================================="

# 配置信息
SERVER_IP="115.191.1.219"
SERVER_USER="root"
REMOTE_DIR="/var/www/restaurant-system/frontend"

# 本地路径
LOCAL_FRONTEND_DIR="/workspace/projects/frontend"
TEMP_TAR="/tmp/restaurant-frontend.tar.gz"

echo ""
echo "步骤1: 打包前端代码..."
echo "----------------------------------------"

# 进入项目目录
cd /workspace/projects

# 打包前端代码
tar -czf "$TEMP_TAR" -C "$LOCAL_FRONTEND_DIR" .

if [ $? -eq 0 ]; then
    echo "✅ 前端代码打包成功"
    echo "   文件大小: $(du -h $TEMP_TAR | cut -f1)"
else
    echo "❌ 前端代码打包失败"
    exit 1
fi

echo ""
echo "步骤2: 上传到腾讯云服务器..."
echo "----------------------------------------"

# 上传文件
scp "$TEMP_TAR" "${SERVER_USER}@${SERVER_IP}:/tmp/"

if [ $? -eq 0 ]; then
    echo "✅ 文件上传成功"
else
    echo "❌ 文件上传失败"
    echo "   请检查SSH连接是否正常"
    exit 1
fi

echo ""
echo "步骤3: 在服务器上解压并配置..."
echo "----------------------------------------"

# 在服务器上执行命令
ssh "${SERVER_USER}@${SERVER_IP}" << 'ENDSSH'
    # 创建目录
    mkdir -p /var/www/restaurant-system/frontend
    mkdir -p /var/www/restaurant-system/frontend/customer
    mkdir -p /var/www/restaurant-system/frontend/admin
    mkdir -p /var/www/restaurant-system/frontend/common

    # 解压文件
    tar -xzf /tmp/restaurant-frontend.tar.gz -C /var/www/restaurant-system/frontend/

    # 设置权限
    chown -R www-data:www-data /var/www/restaurant-system/frontend
    chmod -R 755 /var/www/restaurant-system/frontend

    # 创建Nginx配置
    cat > /etc/nginx/sites-available/restaurant << 'EOF'
server {
    listen 80;
    server_name 115.191.1.219;

    # 顾客端入口
    location / {
        root /var/www/restaurant-system/frontend/customer;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 管理端
    location /admin/ {
        alias /var/www/restaurant-system/frontend/admin/;
        index index.html;
        try_files $uri $uri/ /admin/dashboard/index.html;
    }

    # 通用资源
    location /common/ {
        alias /var/www/restaurant-system/frontend/common/;
    }

    # API反向代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 二维码文件
    location /qrcodes/ {
        root /var/www/restaurant-system;
        expires 7d;
    }

    # Gzip压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
EOF

    # 启用配置
    ln -sf /etc/nginx/sites-available/restaurant /etc/nginx/sites-enabled/

    # 测试配置
    nginx -t

    if [ $? -eq 0 ]; then
        # 重启Nginx
        systemctl reload nginx
        echo "✅ Nginx配置成功"
    else
        echo "❌ Nginx配置错误"
        exit 1
    fi
ENDSSH

if [ $? -eq 0 ]; then
    echo "✅ 服务器配置成功"
else
    echo "❌ 服务器配置失败"
    exit 1
fi

echo ""
echo "步骤4: 清理临时文件..."
echo "----------------------------------------"

# 删除临时文件
rm -f "$TEMP_TAR"
echo "✅ 临时文件已清理"

echo ""
echo "========================================="
echo "✅ 部署完成！"
echo "========================================="
echo ""
echo "访问地址："
echo "  顾客端: http://${SERVER_IP}/"
echo "  管理端: http://${SERVER_IP}/admin/"
echo "  API文档: http://${SERVER_IP}/api/docs"
echo ""
echo "========================================="
