#!/bin/bash
#
# 安全的前端部署脚本 - 不影响已有后端
# 只部署前端文件，通过Nginx代理连接后端
#

set -e

echo "=========================================="
echo "  🚀 安全部署前端（不影响后端）"
echo "=========================================="
echo ""
echo "⚠️  本脚本将："
echo "  ✅ 只部署前端文件到 /var/www/restaurant-system/frontend"
echo "  ✅ 配置Nginx代理（不影响后端服务）"
echo "  ✅ 备份现有文件（可回滚）"
echo "  ❌ 不会修改后端代码"
echo "  ❌ 不会重启后端服务"
echo "  ❌ 不会改变后端配置"
echo ""
read -p "确认继续部署？(y/n): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "❌ 已取消部署"
    exit 0
fi

echo ""
echo "=========================================="

# 配置变量
PROJECT_DIR="/www/wwwroot/restaurant-system"
FRONTEND_DIR="/var/www/restaurant-system/frontend"
BACKUP_DIR="/var/www/restaurant-system/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# 1. 检查后端服务状态
echo ""
echo "🔍 步骤1: 检查后端服务状态..."
BACKEND_RUNNING=false
for port in 8000 8001; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo "  ✅ 后端API服务运行中（端口$port）"
        BACKEND_RUNNING=true
    fi
done

if [ "$BACKEND_RUNNING" = false ]; then
    echo "  ⚠️  警告：未检测到后端API服务"
    echo "  请确认后端服务是否正常运行"
    read -p "是否继续部署？(y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        echo "❌ 已取消部署"
        exit 0
    fi
fi

# 2. 备份现有前端文件
echo ""
echo "💾 步骤2: 备份现有前端文件..."

sudo mkdir -p "$BACKUP_DIR"

if [ -d "$FRONTEND_DIR/customer" ] || [ -d "$FRONTEND_DIR/admin" ]; then
    BACKUP_FILE="$BACKUP_DIR/frontend-backup-$TIMESTAMP.tar.gz"
    echo "  正在备份到: $BACKUP_FILE"
    sudo tar -czf "$BACKUP_FILE" -C "$FRONTEND_DIR" . 2>/dev/null || true
    echo "  ✅ 备份完成"
    
    # 只保留最近5个备份
    cd "$BACKUP_DIR"
    ls -t frontend-backup-*.tar.gz | tail -n +6 | xargs -r rm
    echo "  ℹ️  保留最近5个备份"
else
    echo "  ℹ️  无现有前端文件，跳过备份"
fi

# 3. 创建前端目录
echo ""
echo "📂 步骤3: 创建前端目录..."
sudo mkdir -p "$FRONTEND_DIR"
echo "  ✅ 前端目录: $FRONTEND_DIR"

# 4. 复制前端文件
echo ""
echo "📦 步骤4: 部署前端文件..."

if [ ! -d "$PROJECT_DIR/frontend" ]; then
    echo "  ❌ 错误：frontend目录不存在"
    echo "  请确保在项目根目录执行此脚本"
    exit 1
fi

# 删除旧的前端文件
echo "  清理旧文件..."
sudo rm -rf "$FRONTEND_DIR"/* 2>/dev/null || true

# 复制新文件
echo "  复制新文件..."
sudo cp -r "$PROJECT_DIR/frontend/customer" "$FRONTEND_DIR/"
sudo cp -r "$PROJECT_DIR/frontend/admin" "$FRONTEND_DIR/"
sudo cp -r "$PROJECT_DIR/frontend/common" "$FRONTEND_DIR/"

echo "  ✅ 前端文件复制完成"

# 5. 设置权限
echo ""
echo "🔐 步骤5: 设置文件权限..."
sudo chown -R www-data:www-data "$FRONTEND_DIR"
sudo chmod -R 755 "$FRONTEND_DIR"
echo "  ✅ 权限设置完成"

# 6. 配置Nginx（不影响现有配置）
echo ""
echo "⚙️  步骤6: 配置Nginx..."

# 检查是否已有配置
NGINX_CONF="/etc/nginx/sites-available/restaurant"
if [ -f "$NGINX_CONF" ]; then
    echo "  ℹ️  备份现有Nginx配置..."
    sudo cp "$NGINX_CONF" "$NGINX_CONF.backup-$TIMESTAMP"
fi

# 创建新的Nginx配置
echo "  创建Nginx配置..."
sudo tee "$NGINX_CONF" > /dev/null <<'EOF'
# 餐饮系统前端配置（不影响后端）
server {
    listen 80;
    server_name _;

    # 顾客端 - 根目录
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

    # API代理到后端（后端运行在localhost:8000）
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket支持（端口8001）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # WebSocket代理（端口8001）
    location /ws/ {
        proxy_pass http://localhost:8001/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # 日志
    access_log /var/log/nginx/restaurant-access.log;
    error_log /var/log/nginx/restaurant-error.log;
}
EOF

# 启用站点配置
echo "  启用站点配置..."
sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/restaurant

# 测试Nginx配置
echo "  测试Nginx配置..."
if sudo nginx -t; then
    echo "  ✅ Nginx配置测试通过"
else
    echo "  ❌ Nginx配置测试失败"
    echo "  已恢复原配置"
    if [ -f "$NGINX_CONF.backup-$TIMESTAMP" ]; then
        sudo mv "$NGINX_CONF.backup-$TIMESTAMP" "$NGINX_CONF"
    fi
    exit 1
fi

# 重启Nginx（不影响后端）
echo "  重启Nginx..."
sudo systemctl reload nginx
echo "  ✅ Nginx已重启（不影响后端服务）"

# 7. 验证前端后端连接
echo ""
echo "🔗 步骤7: 验证前端后端连接..."

echo "  测试后端API..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health | grep -q "200"; then
    echo "  ✅ 后端API可访问（通过Nginx代理）"
else
    echo "  ⚠️  警告：后端API无法访问"
    echo "  可能的原因："
    echo "    - 后端服务未运行"
    echo "    - 后端服务不在端口8000"
    echo "    - 防火墙阻止"
fi

echo ""
echo "=========================================="
echo "  ✅ 部署完成！"
echo "=========================================="
echo ""
echo "📋 部署信息："
echo "  前端目录: $FRONTEND_DIR"
echo "  备份位置: $BACKUP_FILE"
echo "  Nginx配置: $NGINX_CONF"
echo ""
echo "🌐 访问地址："
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "你的服务器IP")
echo "  顾客端: http://$SERVER_IP/"
echo "  管理端: http://$SERVER_IP/admin/dashboard/index.html"
echo "  API文档: http://$SERVER_IP/api/docs"
echo ""
echo "🔧 后端服务："
echo "  状态: $(systemctl is-active --quiet restaurant-api 2>/dev/null && echo '运行中' || echo '请手动检查')"
echo "  API端口: 8000, 8001"
echo "  WebSocket端口: 8001"
echo ""
echo "⚠️  重要说明："
echo "  1. 前端已部署，不影响后端服务"
echo "  2. Nginx只负责代理，不处理业务逻辑"
echo "  3. 如需回滚："
echo "     sudo tar -xzf $BACKUP_FILE -C $FRONTEND_DIR/"
echo "     sudo systemctl reload nginx"
echo ""
echo "=========================================="
