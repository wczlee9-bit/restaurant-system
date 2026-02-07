# 🚀 一键自动化部署到腾讯云

## ✅ 已完成配置

### 1. 前端API配置已修改
- ✅ API地址已改为本地后端 `/api`
- ✅ 通过Nginx代理到本地后端服务

### 2. GitHub Actions自动化部署已配置
- ✅ 工作流文件：`.github/workflows/deploy-to-tencent-cloud.yml`
- ✅ 自动打包前端文件
- ✅ 自动上传到服务器
- ✅ 自动配置Nginx
- ✅ 自动重启服务

## 📝 配置步骤（仅需要做一次）

### 步骤1：生成SSH密钥对

**在本地电脑或服务器上执行：**

```bash
# 生成SSH密钥对
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_rsa

# 显示公钥内容
cat ~/.ssh/github_rsa.pub
```

**将公钥添加到服务器：**

```bash
# 在服务器上执行（将上面的公钥复制到authorized_keys）
mkdir -p ~/.ssh
echo "公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### 步骤2：配置GitHub Secrets

**访问GitHub仓库：**
1. 打开：https://github.com/wczlee9-bit/restaurant-system/settings/secrets/actions
2. 点击 "New repository secret"
3. 添加以下3个Secrets：

#### Secret 1: SERVER_HOST
- **Name**: `SERVER_HOST`
- **Value**: 您的服务器IP地址（例如：115.191.1.219）

#### Secret 2: SERVER_USER
- **Name**: `SERVER_USER`
- **Value**: `root`（或您的服务器用户名）

#### Secret 3: SSH_PRIVATE_KEY
- **Name**: `SSH_PRIVATE_KEY`
- **Value**: 私钥的完整内容（包含BEGIN和END行）

**获取私钥内容：**
```bash
cat ~/.ssh/github_rsa
```

复制整个内容（包括 `-----BEGIN RSA PRIVATE KEY-----` 和 `-----END RSA PRIVATE KEY-----`）

### 步骤3：测试SSH连接

**在本地测试：**
```bash
ssh -i ~/.ssh/github_rsa root@your-server-ip
```

如果能够成功登录，说明配置正确。

## 🎯 自动部署流程

配置完成后，**只需执行以下操作即可自动部署：**

### 方式1：推送代码到GitHub（推荐）
```bash
git add .
git commit -m "前端更新"
git push origin main
```

**GitHub Actions会自动：**
1. ✅ 打包前端文件
2. ✅ 上传到服务器
3. ✅ 解压到 `/var/www/restaurant-system/frontend`
4. ✅ 配置Nginx
5. ✅ 重启服务
6. ✅ 完成部署

### 方式2：手动触发部署
1. 访问：https://github.com/wczlee9-bit/restaurant-system/actions
2. 点击 "Auto Deploy to Tencent Cloud"
3. 点击 "Run workflow" → "Run workflow"

## 📦 部署内容

自动部署会上传以下目录：
- `frontend/customer/` - 顾客端页面（5个页面）
- `frontend/admin/` - 管理端页面（4个页面）
- `frontend/common/` - 通用资源（CSS、JS、images）

## 🌐 访问地址

部署成功后，可以通过以下地址访问：

| 功能 | URL |
|------|-----|
| 顾客端首页 | http://您的服务器IP/ |
| 菜单页面 | http://您的服务器IP/menu/index.html |
| 购物车 | http://您的服务器IP/cart/index.html |
| 订单列表 | http://您的服务器IP/order/index.html |
| 个人中心 | http://您的服务器IP/profile/index.html |
| 管理端仪表盘 | http://您的服务器IP/admin/dashboard/index.html |
| 菜品管理 | http://您的服务器IP/admin/dishes/index.html |
| 订单管理 | http://您的服务器IP/admin/orders/index.html |
| 会员管理 | http://您的服务器IP/admin/members/index.html |
| API文档 | http://您的服务器IP/api/docs |

## 🔍 查看部署状态

### 在GitHub上查看
1. 访问：https://github.com/wczlee9-bit/restaurant-system/actions
2. 查看最新的工作流运行状态
3. 点击可以查看详细日志

### 在服务器上验证
```bash
# 检查Nginx配置
nginx -t

# 检查Nginx状态
systemctl status nginx

# 查看部署的文件
ls -la /var/www/restaurant-system/frontend/
```

## ⚠️ 常见问题

### 1. SSH连接失败
**检查项：**
- SSH密钥是否正确配置
- `authorized_keys` 文件权限是否为 600
- 服务器SSH端口是否开放（默认22）

### 2. Nginx配置错误
**解决方案：**
```bash
# 查看Nginx错误日志
tail -f /var/log/nginx/error.log

# 检查配置文件
cat /etc/nginx/sites-available/restaurant
```

### 3. 前端无法访问后端API
**检查项：**
- 后端API服务是否运行（端口8000）
- API地址配置是否正确（应为 `/api`）
- Nginx代理配置是否正确

### 4. 静态文件404
**解决方案：**
```bash
# 检查文件权限
ls -la /var/www/restaurant-system/frontend/

# 重新设置权限
sudo chown -R www-data:www-data /var/www/restaurant-system/frontend
sudo chmod -R 755 /var/www/restaurant-system/frontend
```

## 🎉 完成！

配置完成后，每次修改前端代码并推送到GitHub，都会自动部署到您的腾讯云服务器！

**无需手动操作，完全自动化！** 🚀

---

## 📌 快速参考

### 需要配置的GitHub Secrets：
- `SERVER_HOST` = 您的服务器IP
- `SERVER_USER` = `root`
- `SSH_PRIVATE_KEY` = 私钥完整内容

### 触发自动部署：
```bash
git add .
git commit -m "更新"
git push origin main
```

### 验证部署：
- 访问：http://您的服务器IP/
- 查看Nginx日志：`tail -f /var/log/nginx/access.log`
