#!/bin/bash
#
# Gitee自动部署脚本 - 腾讯云前端一键部署
# 使用方法：在服务器上运行此脚本即可
#

set -e

echo "=========================================="
echo "  🚀 开始从Gitee自动部署前端"
echo "=========================================="

# 配置变量
PROJECT_DIR="/www/wwwroot/restaurant-system"
FRONTEND_DIR="/var/www/restaurant-system/frontend"
GITEE_REPO="https://gitee.com/你的用户名/restaurant-system.git"  # 请修改为实际的Gitee仓库地址
BRANCH="main"

# 检查是否在项目目录中
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 错误：项目目录不存在: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

echo ""
echo "📦 步骤1: 检查Git配置..."

# 检查是否已经初始化Git
if [ ! -d ".git" ]; then
    echo "⚠️  Git未初始化，正在从Gitee克隆..."

    # 如果存在旧的目录，先删除
    cd /www/wwwroot
    if [ -d "restaurant-system" ]; then
        echo "🗑️  删除旧的项目目录..."
        rm -rf restaurant-system
    fi

    # 克隆仓库
    echo "📥 正在从Gitee克隆仓库..."
    git clone "$GITEE_REPO" restaurant-system
    cd restaurant-system
else
    echo "✅ Git已初始化"

    # 检查远程仓库地址
    CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
    if [[ ! "$CURRENT_REMOTE" =~ gitee\.com ]]; then
        echo "🔧 正在配置Gitee远程仓库..."
        git remote add origin "$GITEE_REPO" 2>/dev/null || git remote set-url origin "$GITEE_REPO"
    fi
fi

echo ""
echo "📥 步骤2: 拉取最新代码..."

# 拉取最新代码
git fetch origin
git reset --hard origin/"$BRANCH"
git pull origin "$BRANCH"

echo "✅ 代码拉取完成"

echo ""
echo "📦 步骤3: 打包前端文件..."

cd "$PROJECT_DIR"

# 检查frontend目录是否存在
if [ ! -d "frontend" ]; then
    echo "❌ 错误：frontend目录不存在"
    exit 1
fi

# 打包前端文件
tar -czf /tmp/frontend.tar.gz \
    customer/ \
    admin/ \
    common/ 2>/dev/null || {
        echo "❌ 打包失败，尝试从frontend目录打包..."
        cd frontend
        tar -czf /tmp/frontend.tar.gz \
            customer/ \
            admin/ \
            common/ 2>/dev/null || {
            echo "❌ 打包失败"
            exit 1
        }
        cd ..
    }

echo "✅ 前端文件打包完成"

echo ""
echo "🚀 步骤4: 部署前端到Nginx..."

# 创建部署目录
sudo mkdir -p "$FRONTEND_DIR"

# 备份现有文件
if [ -d "$FRONTEND_DIR/customer" ]; then
    echo "💾 备份现有文件..."
    BACKUP_FILE="/tmp/frontend-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
    sudo tar -czf "$BACKUP_FILE" -C "$FRONTEND_DIR" customer/ admin/ common/ 2>/dev/null || true
    echo "✅ 备份完成: $BACKUP_FILE"
fi

# 解压新文件
echo "📂 解压前端文件..."
sudo tar -xzf /tmp/frontend.tar.gz -C "$FRONTEND_DIR/"

# 设置权限
echo "🔐 设置文件权限..."
sudo chown -R www-data:www-data "$FRONTEND_DIR"
sudo chmod -R 755 "$FRONTEND_DIR"

echo "✅ 前端文件部署完成"

echo ""
echo "⚙️  步骤5: 配置Nginx..."

# 创建Nginx配置
sudo tee /etc/nginx/sites-available/restaurant > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    # 前端根目录
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

    # API代理到后端
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # WebSocket支持
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
}
EOF

# 启用站点配置
sudo ln -sf /etc/nginx/sites-available/restaurant /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
echo "🧪 测试Nginx配置..."
sudo nginx -t

# 重启Nginx
echo "🔄 重启Nginx..."
sudo systemctl restart nginx

echo "✅ Nginx配置完成"

# 清理临时文件
rm -f /tmp/frontend.tar.gz

echo ""
echo "=========================================="
echo "  ✅ 部署完成！"
echo "=========================================="
echo ""
echo "📂 前端部署到: $FRONTEND_DIR"
echo "🌐 访问地址: http://$(curl -s ifconfig.me || echo '你的服务器IP')"
echo ""
echo "📱 顾客端: http://$(curl -s ifconfig.me || echo '你的服务器IP')/"
echo "🖥️  管理端: http://$(curl -s ifconfig.me || echo '你的服务器IP')/admin/dashboard/index.html"
echo "📖 API文档: http://$(curl -s ifconfig.me || echo '你的服务器IP')/api/docs"
echo ""
echo "=========================================="
