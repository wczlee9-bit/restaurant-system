# 扫码点餐系统 - Netlify 部署指南

## 📋 部署前准备

### 1. 后端 API 服务部署

在部署前端到 Netlify 之前，请确保后端 API 服务已经部署并运行在公网可访问的服务器上。

### 2. 修改 API 地址（如需要）

如果后端 API 部署在独立的域名，需要修改前端页面中的 API 地址。但本次更新已将所有页面改为使用相对路径，因此前端和后端需要在同一域名下部署（通过反向代理）。

## 🚀 Netlify 部署步骤

### 方法一：拖拽部署（推荐，简单快速）

1. **准备部署文件夹**
   - 在本地将 `assets` 文件夹压缩为 zip 文件
   - 或者直接将 `assets` 文件夹拖拽到 Netlify（见下一步）

2. **登录 Netlify**
   - 访问 https://app.netlify.com/
   - 使用 GitHub 账号登录

3. **创建新站点**
   - 点击 "Add new site" → "Deploy manually"
   - 在 "Drag and drop your site output folder here" 区域
   - 将 `assets` 文件夹直接拖拽进去
   - 或上传压缩的 zip 文件

4. **等待部署完成**
   - 部署过程约 1-2 分钟
   - 部署成功后，Netlify 会提供一个随机域名，如：`https://random-name-12345.netlify.app`

5. **自定义域名（可选）**
   - 点击 "Site settings" → "Change site name"
   - 输入你喜欢的名称，如：`restaurant-pos-test`
   - 最终域名：`https://restaurant-pos-test.netlify.app`

### 方法二：GitHub 自动部署（持续集成）

1. **连接 GitHub**
   - 在 Netlify 控制台点击 "Add new site" → "Import an existing project"
   - 选择 GitHub，授权访问你的仓库
   - 选择 `restaurant-system` 仓库

2. **配置构建设置**
   - Build command: `echo "No build needed"`
   - Publish directory: `assets`
   - 点击 "Deploy site"

3. **后续更新**
   - 每次推送到 GitHub 的 main 分支，Netlify 会自动部署
   - 无需手动操作

## 🔧 配置 API 代理（重要）

由于前端页面使用相对路径访问 API，需要在 Netlify 中配置 API 代理。

### 方案 A：使用 Netlify Functions（推荐）

在项目根目录创建 `netlify.toml` 文件（已存在），并添加以下配置：

```toml
[[redirects]]
  from = "/api/*"
  to = "http://你的后端IP:8000/api/:splat"
  status = 200
  force = true
```

例如：
```toml
[[redirects]]
  from = "/api/*"
  to = "http://9.128.251.82:8000/api/:splat"
  status = 200
  force = true
```

### 方案 B：使用反向代理服务器

如果有 Nginx 或 Apache 服务器，配置反向代理：

**Nginx 配置示例：**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/assets;
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 👥 测试人员账号信息

由于登录页面已隐藏演示账号信息，请将以下账号信息提供给测试人员：

### 系统管理员
- 用户名：`system_admin`
- 密码：`admin123`
- 权限：最高权限，可管理所有店铺和用户

### 总公司
- 用户名：`company`
- 密码：`company123`
- 权限：查看所有店铺数据，生成报表

### 店长
- 用户名：`admin`
- 密码：`admin123`
- 权限：管理单个店铺的所有功能

### 厨师
- 用户名：`chef`
- 密码：`chef123`
- 权限：查看和处理订单，管理菜品

### 传菜员
- 用户名：`waiter`
- 密码：`waiter123`
- 权限：传菜，更新订单状态

### 收银员
- 用户名：`cashier`
- 密码：`cashier123`
- 权限：收银，处理支付

## 📱 测试流程

### 1. 顾客端测试流程

1. 访问首页：`https://your-site.netlify.app/`
2. 选择桌号（或使用 URL 参数：`?table=1`）
3. 浏览菜单，添加菜品到购物车
4. 选择支付方式：
   - 马上支付（immediate）
   - 柜台支付（counter）
5. 提交订单
6. 查看订单状态（通过 WebSocket 实时更新）

### 2. 工作人员端测试流程

1. 访问登录页面：`https://your-site.netlify.app/login`
2. 使用上述测试账号登录
3. 根据角色权限执行相应操作：
   - **店长**：管理店铺信息、桌号、订单流程配置
   - **厨师**：查看待制作订单，更新制作状态
   - **传菜员**：查看待传菜订单，更新传菜状态
   - **收银员**：处理支付，查看营收数据

## 🔍 功能测试清单

### 基础功能
- [ ] 顾客扫码进入点餐页面
- [ ] 选择桌号功能
- [ ] 浏览菜单分类和菜品
- [ ] 添加菜品到购物车
- [ ] 选择支付方式
- [ ] 提交订单成功
- [ ] 订单状态实时更新

### 工作人员功能
- [ ] 各角色登录验证
- [ ] 查看实时订单
- [ ] 更新订单状态
- [ ] 订单通知提醒
- [ ] 彩色二维码生成
- [ ] Logo 上传和显示

### 订单流程
- [ ] 逐项确认（per_item）
- [ ] 订单确认（per_order）
- [ ] 自动跳过（skip）
- [ ] 忽略不显示（ignore）

## 🐛 常见问题排查

### 1. API 请求失败

**症状**：页面显示"加载失败"或"提交失败"

**解决方案**：
1. 检查 Netlify 代理配置是否正确
2. 确认后端服务是否正常运行
3. 检查浏览器控制台的 Network 标签，查看具体错误
4. 确认 CORS 配置是否允许跨域请求

### 2. WebSocket 连接失败

**症状**：订单状态不实时更新

**解决方案**：
1. 检查 WebSocket URL 是否正确
2. 确认后端 WebSocket 服务是否启动
3. 检查防火墙是否允许 WebSocket 连接

### 3. 登录失败

**症状**：输入正确的账号密码后提示"登录失败"

**解决方案**：
1. 确认使用的是正确的账号密码
2. 检查浏览器控制台是否有 JavaScript 错误
3. 清除浏览器缓存和 localStorage 后重试

### 4. 二维码无法显示

**症状**：店铺设置页面二维码显示为空白

**解决方案**：
1. 检查 API `/api/generate-styled-qrcode` 是否可用
2. 确认后端安装了 `qrcode` 和 `Pillow` 库
3. 检查浏览器控制台的错误信息

## 📊 监控和日志

### Netlify 日志查看

1. 访问 Netlify 控制台
2. 选择你的站点
3. 点击 "Deploys" → 选择部署记录
4. 查看部署日志

### 后端日志查看

1. SSH 登录到后端服务器
2. 查看应用日志：`tail -f /var/log/restaurant-app.log`
3. 查看错误日志：`tail -f /var/log/restaurant-error.log`

## 🔄 更新部署

### 更新前端页面

1. 修改本地代码
2. 提交到 GitHub：`git push origin main`
3. Netlify 自动部署（如果是 GitHub 集成模式）
4. 或手动拖拽更新（拖拽部署模式）

### 更新后端 API

1. 更新后端代码
2. 重启后端服务
3. 清除 Netlify 缓存（可选）
   - 访问 Netlify 控制台
   - Site settings → Build & deploy → Clear cache

## 📞 技术支持

如有问题，请联系：
- 开发团队：[邮箱]
- 文档地址：[Wiki 链接]
- 问题反馈：[Issues 链接]

---

**最后更新**：2024-01-XX
**版本**：v1.0.0
