#!/bin/bash

# ==========================================
# 腾讯云服务器前端一键部署脚本
# ==========================================
#
# 使用方法：
# 1. 将本脚本上传到服务器
# 2. 将 restaurant-frontend.tar.gz 上传到服务器的 /tmp/ 目录
# 3. 运行脚本: bash deploy_to_tencent_cloud.sh
#
# ==========================================

set -e

echo "========================================="
echo "餐饮点餐系统 - 前端一键部署脚本"
echo "========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root用户运行此脚本"
    exit 1
fi

# 配置
FRONTEND_DIR="/var/www/restaurant-system/frontend"
TEMP_FILE="/tmp/restaurant-frontend.tar.gz"

echo "步骤1: 检查环境..."
echo "----------------------------------------"

# 检查tar.gz文件是否存在
if [ ! -f "$TEMP_FILE" ]; then
    echo "❌ 未找到前端文件: $TEMP_FILE"
    echo ""
    echo "请先将 restaurant-frontend.tar.gz 上传到 /tmp/ 目录"
    exit 1
fi

echo "✅ 前端文件已找到"
echo "   文件大小: $(du -h $TEMP_FILE | cut -f1)"

# 检查Nginx是否安装
if ! command -v nginx &> /dev/null; then
    echo "⚠️  Nginx未安装，开始安装..."
    apt-get update
    apt-get install -y nginx
else
    echo "✅ Nginx已安装"
fi

echo ""
echo "步骤2: 创建目录结构..."
echo "----------------------------------------"

# 创建目录
mkdir -p "$FRONTEND_DIR"
mkdir -p "$FRONTEND_DIR/customer"
mkdir -p "$FRONTEND_DIR/admin"
mkdir -p "$FRONTEND_DIR/common/css"
mkdir -p "$FRONTEND_DIR/common/js"
mkdir -p "$FRONTEND_DIR/common/images"

echo "✅ 目录结构已创建"

echo ""
echo "步骤3: 解压前端文件..."
echo "----------------------------------------"

# 备份现有文件
if [ -d "$FRONTEND_DIR" ] && [ "$(ls -A $FRONTEND_DIR)" ]; then
    echo "备份现有前端文件..."
    BACKUP_DIR="/var/www/restaurant-system/frontend.backup.$(date +%Y%m%d_%H%M%S)"
    cp -r "$FRONTEND_DIR" "$BACKUP_DIR"
    echo "✅ 已备份到: $BACKUP_DIR"
fi

# 清空目录（保留目录结构）
find "$FRONTEND_DIR" -mindepth 1 -delete

# 解压文件
tar -xzf "$TEMP_FILE" -C "$FRONTEND_DIR"

echo "✅ 前端文件已解压"

echo ""
echo "步骤4: 设置权限..."
echo "----------------------------------------"

# 设置权限
chown -R www-data:www-data "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"

echo "✅ 权限已设置"

echo ""
echo "步骤5: 配置Nginx..."
echo "----------------------------------------"

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

echo "✅ Nginx配置文件已创建"

# 启用配置
ln -sf /etc/nginx/sites-available/restaurant /etc/nginx/sites-enabled/

# 删除默认配置
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm -f /etc/nginx/sites-enabled/default
    echo "✅ 默认配置已删除"
fi

# 测试配置
echo ""
echo "步骤6: 测试Nginx配置..."
echo "----------------------------------------"

nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx配置测试通过"
else
    echo "❌ Nginx配置测试失败"
    exit 1
fi

echo ""
echo "步骤7: 重启Nginx..."
echo "----------------------------------------"

systemctl restart nginx
systemctl enable nginx

echo "✅ Nginx已重启"

echo ""
echo "步骤8: 配置防火墙..."
echo "----------------------------------------"

# 检查是否安装了ufw
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    echo "✅ 防火墙已配置（允许80端口）"
else
    echo "⚠️  未检测到ufw防火墙，跳过配置"
fi

echo ""
echo "========================================="
echo "✅ 部署完成！"
echo "========================================="
echo ""
echo "访问地址："
echo "  📱 顾客端: http://115.191.1.219/"
echo "  🖥️  管理端: http://115.191.1.219/admin/dashboard/index.html"
echo "  📖 API文档: http://115.191.1.219/api/docs"
echo ""
echo "测试流程："
echo "  1. 访问顾客端，测试扫码点餐"
echo "  2. 访问管理端，测试后台管理"
echo "  3. 查看API文档，测试API接口"
echo ""
echo "========================================="
echo ""
echo "提示："
echo "  - 如果遇到问题，请查看Nginx日志："
echo "    tail -f /var/log/nginx/error.log"
echo ""
echo "  - 修改API地址（如果需要）："
echo "    vi /var/www/restaurant-system/frontend/common/js/api.js"
echo ""
echo "========================================="
