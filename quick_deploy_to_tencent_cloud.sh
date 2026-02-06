#!/bin/bash

###############################################################################
# 腾讯云极速部署脚本
# 作用：一行命令完成所有部署
# 使用：bash quick_deploy_to_tencent_cloud.sh
###############################################################################

echo "========================================="
echo "  餐厅系统 - 极速部署"
echo "========================================="
echo ""

# 项目配置
GITHUB_REPO="https://github.com/wczlee9-bit/restaurant-system.git"
PROJECT_DIR="/opt/restaurant-system"

# 步骤 1：进入临时目录
echo "[1/8] 准备部署环境..."
cd /tmp

# 步骤 2：备份现有系统
echo "[2/8] 备份现有系统..."
if [ -d "$PROJECT_DIR" ]; then
    cp -r "$PROJECT_DIR" "$PROJECT_DIR-backup-$(date +%Y%m%d-%H%M%S)" 2>/dev/null || true
fi

# 步骤 3：删除旧项目
echo "[3/8] 清理旧项目..."
rm -rf "$PROJECT_DIR"

# 步骤 4：克隆代码
echo "[4/8] 从 GitHub 克隆代码..."
git clone "$GITHUB_REPO" "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 步骤 5：创建虚拟环境
echo "[5/8] 创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 步骤 6：安装依赖
echo "[6/8] 安装依赖..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# 步骤 7：测试模块
echo "[7/8] 测试模块..."
python test_module_loader.py

# 步骤 8：配置服务
echo "[8/8] 配置并启动服务..."

# 创建 systemd 服务
cat > /etc/systemd/system/restaurant.service << 'EOF'
[Unit]
Description=Restaurant System
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/restaurant-system
Environment="PATH=/opt/restaurant-system/venv/bin"
ExecStart=/opt/restaurant-system/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl stop restaurant 2>/dev/null || true
systemctl start restaurant
systemctl enable restaurant

# 等待服务启动
sleep 3

# 配置 Nginx
cat > /etc/nginx/sites-available/restaurant << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }
}
EOF

ln -sf /etc/nginx/sites-available/restaurant /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# 完成
echo ""
echo "========================================="
echo "  🎉 部署完成！"
echo "========================================="
echo ""
echo "访问地址："
echo "  http://$(hostname -I | awk '{print $1}')"
echo ""
echo "管理命令："
echo "  查看状态: systemctl status restaurant"
echo "  查看日志: journalctl -u restaurant -f"
echo "  重启服务: systemctl restart restaurant"
echo ""
