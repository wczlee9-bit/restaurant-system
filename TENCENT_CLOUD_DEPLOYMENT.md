# 🚀 腾讯云服务器前端部署指南

## 服务器信息
- **IP地址**: 115.191.1.219
- **用户**: root
- **操作系统**: Linux

## 部署步骤

### 方法1：SSH手动部署（推荐）

由于沙盒环境限制，请按照以下步骤在腾讯云服务器上手动部署：

#### 步骤1：SSH登录到服务器
```bash
ssh root@115.191.1.219
```

#### 步骤2：创建前端目录
```bash
# 创建前端目录结构
mkdir -p /var/www/restaurant-system/frontend/customer
mkdir -p /var/www/restaurant-system/frontend/admin
mkdir -p /var/www/restaurant-system/frontend/common/css
mkdir -p /var/www/restaurant-system/frontend/common/js
mkdir -p /var/www/restaurant-system/frontend/common/images
```

#### 步骤3：下载前端代码
从本地上传前端文件到服务器。可以使用以下任一方法：

**方法A：使用Git克隆**
```bash
cd /var/www/restaurant-system
git clone https://github.com/wczlee9-bit/restaurant-system.git temp
cp -r temp/frontend/* frontend/
rm -rf temp
```

**方法B：手动上传文件**
将本地 `/workspace/projects/frontend` 目录下的所有文件上传到服务器的 `/var/www/restaurant-system/frontend/` 目录。

#### 步骤4：设置权限
```bash
# 设置权限
chown -R www-data:www-data /var/www/restaurant-system/frontend
chmod -R 755 /var/www/restaurant-system/frontend
```

#### 步骤5：配置Nginx
创建Nginx配置文件：
```bash
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
```

#### 步骤6：启用Nginx配置
```bash
# 创建符号链接
ln -sf /etc/nginx/sites-available/restaurant /etc/nginx/sites-enabled/

# 删除默认配置
rm -f /etc/nginx/sites-enabled/default

# 测试配置
nginx -t

# 重启Nginx
systemctl restart nginx
```

#### 步骤7：配置防火墙
```bash
# 允许HTTP访问
ufw allow 80/tcp
ufw reload
```

### 方法2：使用GitHub Actions自动部署

参考 `GITHUB_ACTIONS_QUICKSTART.md` 配置自动部署。

## 验证部署

### 1. 检查Nginx状态
```bash
systemctl status nginx
```

### 2. 检查文件权限
```bash
ls -la /var/www/restaurant-system/frontend/
```

### 3. 测试访问

在浏览器中打开以下URL：

- **顾客端首页**: http://115.191.1.219/
- **管理端仪表盘**: http://115.191.1.219/admin/dashboard/index.html
- **菜品管理**: http://115.191.1.219/admin/dishes/index.html
- **订单管理**: http://115.191.1.219/admin/orders/index.html
- **会员管理**: http://115.191.1.219/admin/members/index.html

### 4. 测试API

访问API文档：
- http://115.191.1.219/api/docs

## 常见问题

### 问题1：Nginx 404错误
**原因**: 文件未正确上传或路径配置错误
**解决**:
```bash
# 检查文件是否存在
ls -la /var/www/restaurant-system/frontend/customer/

# 检查Nginx错误日志
tail -f /var/log/nginx/error.log
```

### 问题2：API无法访问
**原因**: 后端服务未启动或端口配置错误
**解决**:
```bash
# 检查后端服务是否运行
systemctl status restaurant-backend

# 检查8000端口是否监听
netstat -tlnp | grep 8000
```

### 问题3：权限问题
**原因**: 文件权限不正确
**解决**:
```bash
# 重置权限
chown -R www-data:www-data /var/www/restaurant-system/frontend
chmod -R 755 /var/www/restaurant-system/frontend
```

## 扫码点餐测试

### 1. 生成餐桌二维码

餐桌二维码URL格式：
```
http://115.191.1.219/?table=餐桌号
```

例如：
```
http://115.191.1.219/?table=1
http://115.191.1.219/?table=2
http://115.191.1.219/?table=3
```

### 2. 测试流程

1. **顾客扫码**
   - 扫描餐桌二维码
   - 显示欢迎页面
   - 点击"开始点餐"

2. **浏览菜单**
   - 查看菜品列表
   - 选择分类筛选
   - 添加菜品到购物车

3. **提交订单**
   - 查看购物车
   - 确认订单信息
   - 提交订单

4. **管理后台**
   - 登录管理后台
   - 查看订单列表
   - 更新订单状态
   - 查看统计数据

## 前端文件结构

```
/var/www/restaurant-system/frontend/
├── customer/              # 顾客端
│   ├── index.html         # 扫码入口
│   ├── menu/
│   │   └── index.html     # 菜单页面
│   ├── cart/
│   │   └── index.html     # 购物车
│   ├── order/
│   │   └── index.html     # 订单列表
│   └── profile/
│       └── index.html     # 个人中心
├── admin/                 # 管理端
│   ├── dashboard/
│   │   └── index.html     # 仪表盘
│   ├── dishes/
│   │   └── index.html     # 菜品管理
│   ├── orders/
│   │   └── index.html     # 订单管理
│   └── members/
│       └── index.html     # 会员管理
└── common/                # 通用资源
    ├── css/
    │   └── style.css      # 样式文件
    └── js/
        └── api.js         # API封装
```

## 更新API地址

如果后端API地址不是 localhost:8000，需要修改：

```bash
# 编辑API配置文件
vi /var/www/restaurant-system/frontend/common/js/api.js

# 修改API_BASE为你的实际API地址
# 例如: const API_BASE = 'https://your-api-domain.com/api';
```

## 重启服务

如果修改了配置，需要重启Nginx：

```bash
# 重启Nginx
systemctl restart nginx

# 或重新加载配置
systemctl reload nginx
```

## 监控日志

查看Nginx访问日志：
```bash
tail -f /var/log/nginx/access.log
```

查看Nginx错误日志：
```bash
tail -f /var/log/nginx/error.log
```

## 安全建议

1. **启用HTTPS**
   - 安装Let's Encrypt证书
   - 配置SSL/HTTPS

2. **配置防火墙**
   - 只开放必要的端口
   - 限制访问来源

3. **定期更新**
   - 更新系统和Nginx
   - 修复安全漏洞

## 联系支持

如果遇到问题，请提供：
1. 错误信息
2. Nginx日志
3. 浏览器控制台错误

---

**部署完成后，请访问 http://115.191.1.219 验证部署结果！** 🚀
