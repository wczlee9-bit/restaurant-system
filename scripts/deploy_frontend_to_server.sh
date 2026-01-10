#!/bin/bash

# ========================================
# 餐饮点餐系统前端部署脚本
# 目标服务器：115.191.1.219
# ========================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置变量
SERVER_IP="115.191.1.219"
SERVER_USER="root"  # 根据实际情况修改
REMOTE_DIR="/var/www/restaurant-frontend"
LOCAL_ASSETS_DIR="./assets"
NGINX_CONF="./config/nginx-restaurant.conf"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}餐饮点餐系统前端部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查本地assets目录
if [ ! -d "$LOCAL_ASSETS_DIR" ]; then
    echo -e "${RED}错误: 本地assets目录不存在${NC}"
    exit 1
fi

echo -e "\n${YELLOW}步骤1: 压缩前端文件...${NC}"
tar -czf /tmp/restaurant-frontend.tar.gz -C "$LOCAL_ASSETS_DIR" .
echo -e "${GREEN}✓ 前端文件压缩完成${NC}"

echo -e "\n${YELLOW}步骤2: 上传文件到服务器...${NC}"
# 使用scp上传压缩包
scp /tmp/restaurant-frontend.tar.gz ${SERVER_USER}@${SERVER_IP}:/tmp/
echo -e "${GREEN}✓ 文件上传完成${NC}"

echo -e "\n${YELLOW}步骤3: 在服务器上执行部署...${NC}"
# 远程执行部署命令
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e

echo "3.1 安装Nginx（如果未安装）..."
if ! command -v nginx &> /dev/null; then
    apt-get update
    apt-get install -y nginx
fi

echo "3.2 创建前端目录..."
mkdir -p /var/www/restaurant-frontend
mkdir -p /var/www/restaurant-frontend/qrcodes

echo "3.3 解压前端文件..."
rm -rf /var/www/restaurant-frontend/*
tar -xzf /tmp/restaurant-frontend.tar.gz -C /var/www/restaurant-frontend/

echo "3.4 设置权限..."
chown -R www-data:www-data /var/www/restaurant-frontend
chmod -R 755 /var/www/restaurant-frontend

echo "3.5 备份现有Nginx配置..."
if [ -f /etc/nginx/sites-available/restaurant-frontend ]; then
    cp /etc/nginx/sites-available/restaurant-frontend \
       /etc/nginx/sites-available/restaurant-frontend.backup.$(date +%Y%m%d_%H%M%S)
fi

echo "3.6 检查Nginx配置目录..."
if [ ! -d /etc/nginx/sites-available ]; then
    mkdir -p /etc/nginx/sites-available
fi
if [ ! -d /etc/nginx/sites-enabled ]; then
    mkdir -p /etc/nginx/sites-enabled
fi

echo "3.7 启用新配置..."
# 注意：这里需要手动复制配置文件，因为脚本在远程执行
# 请先手动上传nginx配置文件到服务器

echo "3.8 测试Nginx配置..."
nginx -t

echo "3.9 重启Nginx..."
systemctl restart nginx

echo "3.10 设置Nginx开机自启..."
systemctl enable nginx

ENDSSH

echo -e "\n${YELLOW}步骤4: 上传Nginx配置文件...${NC}"
# 上传Nginx配置
if [ -f "$NGINX_CONF" ]; then
    scp "$NGINX_CONF" ${SERVER_USER}@${SERVER_IP}:/tmp/nginx-restaurant.conf

    ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
    # 移动配置文件到正确位置
    mv /tmp/nginx-restaurant.conf /etc/nginx/sites-available/restaurant-frontend

    # 创建软链接（如果不存在）
    if [ ! -L /etc/nginx/sites-enabled/restaurant-frontend ]; then
        ln -sf /etc/nginx/sites-available/restaurant-frontend \
                /etc/nginx/sites-enabled/restaurant-frontend
    fi

    # 移除默认配置（可选）
    # rm -f /etc/nginx/sites-enabled/default

    # 测试配置
    nginx -t

    # 重启Nginx
    systemctl reload nginx
ENDSSH
    echo -e "${GREEN}✓ Nginx配置文件部署完成${NC}"
else
    echo -e "${YELLOW}警告: 未找到Nginx配置文件，跳过此步骤${NC}"
fi

# 清理临时文件
rm -f /tmp/restaurant-frontend.tar.gz

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✓ 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${YELLOW}访问地址：${NC}"
echo -e "  主页: http://${SERVER_IP}/"
echo -e "  门户: http://${SERVER_IP}/portal.html"
echo -e "  顾客: http://${SERVER_IP}/customer_order_v3.html"
echo -e "  登录: http://${SERVER_IP}/login_standalone.html"
echo -e "  会员: http://${SERVER_IP}/member_center.html"
echo -e "\n${YELLOW}检查部署状态：${NC}"
echo -e "  curl http://${SERVER_IP}/portal.html"
echo -e "\n${YELLOW}查看日志：${NC}"
echo -e "  ssh root@${SERVER_IP} 'tail -f /var/log/nginx/restaurant-frontend-access.log'"
echo ""
