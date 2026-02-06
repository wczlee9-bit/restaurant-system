#!/bin/bash

###############################################################################
# 生成部署包脚本
# 作用：创建一个完整的部署包，包含所有必要文件
# 使用：bash create_deployment_package.sh
###############################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置变量
PACKAGE_NAME="restaurant-deployment-$(date +%Y%m%d-%H%M%S).tar.gz"
TEMP_DIR="deployment_package_temp"

print_header() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

###############################################################################
# 步骤 1：清理临时目录
###############################################################################

clean_temp() {
    print_header "步骤 1：清理临时目录"

    if [ -d "$TEMP_DIR" ]; then
        print_info "删除旧的临时目录..."
        rm -rf "$TEMP_DIR"
    fi

    mkdir -p "$TEMP_DIR"
    print_success "临时目录创建完成"
}

###############################################################################
# 步骤 2：打包源代码
###############################################################################

package_source() {
    print_header "步骤 2：打包源代码"

    print_info "打包项目源代码..."

    # 使用 git archive 打包源代码（排除 .git 和其他不必要的文件）
    git archive --format=tar.gz --output="$TEMP_DIR/source.tar.gz" HEAD --prefix=restaurant/

    if [ $? -eq 0 ]; then
        print_success "源代码打包完成"
    else
        print_info "使用 cp 方式打包..."
        mkdir -p "$TEMP_DIR/restaurant"
        
        # 复制项目文件
        cp -r core "$TEMP_DIR/restaurant/" 2>/dev/null || true
        cp -r src "$TEMP_DIR/restaurant/" 2>/dev/null || true
        cp -r modules "$TEMP_DIR/restaurant/" 2>/dev/null || true
        cp -r config "$TEMP_DIR/restaurant/" 2>/dev/null || true
        cp -r assets "$TEMP_DIR/restaurant/" 2>/dev/null || true
        cp -r docs "$TEMP_DIR/restaurant/" 2>/dev/null || true
        cp -r scripts "$TEMP_DIR/restaurant/" 2>/dev/null || true
        cp -r frontend "$TEMP_DIR/restaurant/" 2>/dev/null || true
        cp -r admin "$TEMP_DIR/restaurant/" 2>/dev/null || true
        cp -r backend_extensions "$TEMP_DIR/restaurant/" 2>/dev/null || true
        cp requirements.txt "$TEMP_DIR/restaurant/" 2>/dev/null || true
        cp modular_app.py "$TEMP_DIR/restaurant/" 2>/dev/null || true
        cp test_module_loader.py "$TEMP_DIR/restaurant/" 2>/dev/null || true
        
        # 复制文档
        cp *.md "$TEMP_DIR/restaurant/" 2>/dev/null || true
        
        print_success "源代码复制完成"
    fi
}

###############################################################################
# 步骤 3：复制部署脚本
###############################################################################

copy_scripts() {
    print_header "步骤 3：复制部署脚本"

    print_info "复制部署脚本..."

    cp deploy_all_in_one.sh "$TEMP_DIR/"
    cp deploy_from_gitee.sh "$TEMP_DIR/" 2>/dev/null || true
    cp migrate_to_gitee.sh "$TEMP_DIR/" 2>/dev/null || true

    print_success "部署脚本复制完成"
}

###############################################################################
# 步骤 4：创建部署说明
###############################################################################

create_readme() {
    print_header "步骤 4：创建部署说明"

    cat > "$TEMP_DIR/DEPLOYMENT_README.md" << 'EOF'
# 🚀 餐厅系统一键部署包

## 📦 包含内容

- `source.tar.gz` - 项目源代码
- `deploy_all_in_one.sh` - 一键部署脚本
- `DEPLOYMENT_README.md` - 本文件

## 🎯 快速部署

### 方法 1：直接部署（推荐）

```bash
# 1. 上传部署包到腾讯云服务器
scp restaurant-deployment-*.tar.gz root@your-server-ip:/tmp/

# 2. SSH 连接到服务器
ssh root@your-server-ip

# 3. 解压部署包
cd /tmp
tar -xzf restaurant-deployment-*.tar.gz
cd deployment_package_temp

# 4. 运行一键部署脚本
bash deploy_all_in_one.sh
```

### 方法 2：从源代码部署

```bash
# 1. 解压源代码
cd /tmp
tar -xzf deployment_package_temp/source.tar.gz
cd restaurant

# 2. 手动部署（参考 deploy_all_in_one.sh 中的步骤）
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# ... 其他步骤
```

## ⚙️ 配置选项

在运行部署脚本前，可以设置以下环境变量：

```bash
# Gitee 仓库地址
export GITEE_REPO="https://gitee.com/lijun75/restaurant.git"

# 项目安装目录
export PROJECT_DIR="/opt/restaurant-system"

# 数据库配置
export DB_USER="postgres"
export DB_NAME="restaurant_db"

# Python 版本
export PYTHON_VERSION="3.10"

# 备份目录
export BACKUP_DIR="/tmp/restaurant-backup"
```

## 📝 部署步骤说明

部署脚本会自动执行以下步骤：

1. ✅ 环境检查
2. ✅ 备份现有系统
3. ✅ 从 Gitee 克隆代码
4. ✅ 安装依赖
5. ✅ 初始化数据库
6. ✅ 测试模块加载器
7. ✅ 配置服务
8. ✅ 启动服务
9. ✅ 配置 Nginx
10. ✅ 验证部署

## 🎯 部署后验证

部署完成后，可以通过以下方式验证：

```bash
# 检查服务状态
systemctl status restaurant

# 查看服务日志
journalctl -u restaurant -f

# 测试 API
curl http://localhost:8000/health
```

## 📊 访问地址

部署成功后，可以通过以下地址访问：

- 后端 API: `http://your-server-ip`
- 健康检查: `http://your-server-ip/health`

## 🔄 更新部署

如果需要更新系统：

```bash
# 运行一键部署脚本
bash deploy_all_in_one.sh

# 脚本会自动：
# - 备份现有系统
# - 拉取最新代码
# - 更新依赖
# - 重启服务
```

## ❗ 注意事项

1. **首次部署**：确保 PostgreSQL 已安装并运行
2. **数据库备份**：脚本会自动备份现有数据库
3. **网络连接**：确保服务器可以访问 Gitee
4. **权限要求**：需要 root 权限运行部署脚本

## 🆘 故障排除

### 服务启动失败

```bash
# 查看服务日志
journalctl -u restaurant -n 50 --no-pager

# 手动启动服务
cd /opt/restaurant-system
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 数据库连接失败

```bash
# 检查 PostgreSQL 状态
systemctl status postgresql

# 检查数据库是否存在
sudo -u postgres psql -l

# 查看数据库日志
sudo tail -f /var/log/postgresql/*.log
```

### Nginx 配置错误

```bash
# 测试 Nginx 配置
nginx -t

# 查看 Nginx 日志
tail -f /var/log/nginx/error.log
```

## 📞 获取帮助

如有问题，请查看：
- 项目文档：https://gitee.com/lijun75/restaurant
- 部署日志：`journalctl -u restaurant -f`

## 🎉 部署成功后

恭喜！您的餐厅系统已成功部署。可以开始使用以下功能：

- ✅ 扫码点餐
- ✅ 订单管理
- ✅ 库存管理
- ✅ 会员系统
- ✅ 营收分析
- ✅ 实时通信

---

**祝您使用愉快！** 🚀
EOF

    print_success "部署说明创建完成"
}

###############################################################################
# 步骤 5：创建快速部署脚本
###############################################################################

create_quick_deploy() {
    print_header "步骤 5：创建快速部署脚本"

    cat > "$TEMP_DIR/quick_deploy.sh" << 'EOF'
#!/bin/bash

###############################################################################
# 快速部署脚本
# 作用：快速部署餐厅系统
# 使用：bash quick_deploy.sh
###############################################################################

set -e

echo "========================================"
echo "  餐厅系统快速部署"
echo "========================================"
echo ""

# 解压源代码
echo "[1/5] 解压源代码..."
if [ -f "source.tar.gz" ]; then
    tar -xzf source.tar.gz
    cd restaurant
    echo "✅ 源代码解压完成"
else
    echo "❌ 未找到 source.tar.gz"
    exit 1
fi

# 创建虚拟环境
echo "[2/5] 创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate
echo "✅ 虚拟环境创建完成"

# 安装依赖
echo "[3/5] 安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ 依赖安装完成"

# 测试模块
echo "[4/5] 测试模块..."
python test_module_loader.py
echo "✅ 模块测试完成"

# 启动服务
echo "[5/5] 启动服务..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 &
echo "✅ 服务启动完成"

echo ""
echo "========================================"
echo "  部署完成！"
echo "========================================"
echo ""
echo "访问地址: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "按 Ctrl+C 停止服务"
EOF

    chmod +x "$TEMP_DIR/quick_deploy.sh"

    print_success "快速部署脚本创建完成"
}

###############################################################################
# 步骤 6：打包部署包
###############################################################################

create_package() {
    print_header "步骤 6：打包部署包"

    print_info "创建部署包..."

    cd "$TEMP_DIR"
    tar -czf "../$PACKAGE_NAME" *

    cd ..

    if [ -f "$PACKAGE_NAME" ]; then
        FILE_SIZE=$(du -h "$PACKAGE_NAME" | cut -f1)
        print_success "部署包创建完成: $PACKAGE_NAME ($FILE_SIZE)"
    else
        print_info "部署包创建失败"
        exit 1
    fi
}

###############################################################################
# 步骤 7：清理临时目录
###############################################################################

cleanup() {
    print_header "步骤 7：清理临时目录"

    print_info "删除临时目录..."
    rm -rf "$TEMP_DIR"
    print_success "清理完成"
}

###############################################################################
# 步骤 8：显示部署说明
###############################################################################

show_instructions() {
    print_header "部署包创建完成"

    echo ""
    echo "📦 部署包信息:"
    echo "  文件名: $PACKAGE_NAME"
    echo "  大小: $(du -h "$PACKAGE_NAME" | cut -f1)"
    echo ""

    echo "📤 上传到腾讯云:"
    echo "  scp $PACKAGE_NAME root@your-server-ip:/tmp/"
    echo ""

    echo "🚀 在腾讯云上部署:"
    echo "  ssh root@your-server-ip"
    echo "  cd /tmp"
    echo "  tar -xzf $PACKAGE_NAME"
    echo "  cd deployment_package_temp"
    echo "  bash deploy_all_in_one.sh"
    echo ""

    echo "📖 详细说明请查看: deployment_package_temp/DEPLOYMENT_README.md"
    echo ""
}

###############################################################################
# 主函数
###############################################################################

main() {
    print_header "创建餐厅系统部署包"

    clean_temp
    package_source
    copy_scripts
    create_readme
    create_quick_deploy
    create_package
    cleanup
    show_instructions

    print_success "部署包创建成功！"
}

# 运行主函数
main
