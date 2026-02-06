# 扫码点餐前端 - 部署说明

## 📦 项目结构

```
frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.js
    ├── style.css
    ├── App.vue
    ├── api/
    │   └── restaurant.js
    └── views/
        ├── Menu.vue
        ├── OrderSuccess.vue
        └── OrderDetail.vue
```

## 🚀 在服务器上部署

### 步骤 1：将前端代码上传到服务器

```bash
# 在服务器上创建前端项目目录
mkdir -p /opt/restaurant-system/frontend/src/{api,views}

# 复制以下文件到服务器（从沙盒）
# frontend/index.html -> /opt/restaurant-system/frontend/
# frontend/package.json -> /opt/restaurant-system/frontend/
# frontend/vite.config.js -> /opt/restaurant-system/frontend/
# frontend/src/main.js -> /opt/restaurant-system/frontend/src/
# frontend/src/style.css -> /opt/restaurant-system/frontend/src/
# frontend/src/App.vue -> /opt/restaurant-system/frontend/src/
# frontend/src/api/restaurant.js -> /opt/restaurant-system/frontend/src/api/
# frontend/src/views/Menu.vue -> /opt/restaurant-system/frontend/src/views/
# frontend/src/views/OrderSuccess.vue -> /opt/restaurant-system/frontend/src/views/
# frontend/src/views/OrderDetail.vue -> /opt/restaurant-system/frontend/src/views/
```

### 步骤 2：安装依赖

```bash
cd /opt/restaurant-system/frontend
npm install
```

### 步骤 3：构建项目

```bash
npm run build
```

### 步骤 4：验证部署

```bash
# 检查构建产物
ls -la /opt/restaurant-system/frontend/dist

# 重启 Nginx
systemctl restart nginx

# 测试访问
curl -I http://129.226.196.76/
```

## 🔗 访问地址

- 扫码点餐：http://129.226.196.76/?table=1&store=1
- API 文档：http://129.226.196.76/docs

## 📱 使用说明

1. 访问点餐页面，可以通过 URL 参数指定桌号和店铺：
   - http://129.226.196.76/?table=1&store=1
   - `table`: 桌号（默认：1）
   - `store`: 店铺 ID（默认：1）

2. 浏览菜单，添加菜品到购物车

3. 填写特殊要求（可选）

4. 提交订单

5. 查看订单详情和状态

## 🔧 故障排查

### 问题 1：npm install 失败

```bash
# 安装 Node.js（如果没有）
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# 验证安装
node -v
npm -v
```

### 问题 2：构建失败

```bash
# 清除缓存重新安装
rm -rf node_modules package-lock.json
npm install
npm run build
```

### 问题 3：Nginx 404 错误

```bash
# 检查文件是否存在
ls -la /opt/restaurant-system/frontend/dist

# 检查 Nginx 配置
nginx -t

# 查看 Nginx 日志
tail -f /var/log/nginx/error.log
```

## 🎨 功能特性

- ✅ 菜单展示（分类、价格、库存）
- ✅ 购物车管理（添加、修改、删除）
- ✅ 订单提交（支持特殊要求）
- ✅ 订单状态查看
- ✅ 订单详情查看
- ✅ 响应式设计（支持手机/平板/电脑）

## 📊 技术栈

- Vue.js 3 (Composition API)
- Vite 5
- Axios
- CSS3 (Flexbox/Grid)
