# 🌐 Netlify 部署指南 - 餐饮点餐系统

本指南详细介绍如何将餐饮点餐系统的前端部署到 Netlify。

---

## 📋 目录
- [Netlify 简介](#netlify-简介)
- [准备工作](#准备工作)
- [部署方法](#部署方法)
- [配置自定义域名](#配置自定义域名)
- [API 代理配置](#api-代理配置)
- [部署验证](#部署验证)
- [常见问题](#常见问题)

---

## Netlify 简介

Netlify 是一个现代化的静态网站托管平台，提供：
- ✅ 免费额度：100GB带宽/月
- ✅ 自动 HTTPS
- ✅ 全球 CDN 加速
- ✅ 持续部署（CD）
- ✅ 自定义域名支持
- ✅ API 代理功能

---

## 准备工作

### 1. 账号准备

- 注册 Netlify 账号：https://app.netlify.com/signup
- 可以使用 GitHub、GitLab、Bitbucket 或 Email 注册

### 2. 代码准备

确保项目包含以下文件：
```
restaurant-system/
├── assets/                  # 前端静态文件
│   ├── portal.html
│   ├── member_center.html
│   ├── headquarters_dashboard.html
│   ├── customer_order_v3.html
│   ├── staff_workflow.html
│   └── ...
├── netlify.toml             # Netlify 配置文件
└── README.md
```

### 3. 后端准备

确保后端 API 服务已经部署并正常运行：
- 顾客 API: `http://9.128.251.82:8000`
- 店员 API: `http://9.128.251.82:8001`
- 会员 API: `http://9.128.251.82:8004`
- 总公司 API: `http://9.128.251.82:8006`

---

## 部署方法

Netlify 提供多种部署方式，我们推荐以下几种：

### 方法 1: GitHub 集成部署 (推荐)

**优点**：
- 自动化部署
- 支持持续部署
- 代码管理方便
- 可以回滚版本

**步骤**：

#### 1. 推送代码到 GitHub

```bash
# 在本地项目目录执行
cd restaurant-system

# 初始化 Git 仓库（如果还没有）
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit - Restaurant ordering system"

# 添加远程仓库（将YOUR_USERNAME替换为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/restaurant-system.git

# 推送到 GitHub
git push -u origin main
```

#### 2. 在 Netlify 导入项目

1. 登录 Netlify: https://app.netlify.com
2. 点击 **"Add new site"** → **"Import an existing project"**
3. 选择 **"GitHub"**，点击 "Connect to GitHub" 授权
4. 在仓库列表中找到 `restaurant-system`，点击 "Import site"
5. 配置构建设置：
   - **Branch to deploy**: `main` (或 `master`)
   - **Build command**: (留空，因为我们是静态网站)
   - **Publish directory**: `assets`
6. 点击 **"Deploy site"**

#### 3. 等待部署完成

- 部署通常需要 1-3 分钟
- 部署完成后会显示一个随机站点地址，如：
  - `https://random-name-12345.netlify.app`

#### 4. 测试访问

打开浏览器访问：`https://random-name-12345.netlify.app`

---

### 方法 2: 拖拽部署 (快速测试)

**优点**：
- 最简单快速
- 无需 Git
- 适合临时测试

**缺点**：
- 无版本控制
- 需要手动上传

**步骤**：

1. 打开 Netlify 拖拽页面：https://app.netlify.com/drop
2. 在本地打开 `restaurant-system/assets/` 文件夹
3. 将整个 `assets/` 文件夹拖拽到 Netlify 页面
4. 等待上传和部署完成
5. 获得随机站点地址

#### 注意事项

拖拽部署后，记得上传 `netlify.toml` 配置文件：
1. 在 Netlify Dashboard 中进入 "Site settings"
2. 点击 "Build & deploy"
3. 在 "Post processing" → "Custom headers" 中手动添加配置

---

### 方法 3: Netlify CLI (命令行部署)

**优点**：
- 自动化脚本支持
- 适合 CI/CD 集成

**步骤**：

#### 1. 安装 Netlify CLI

```bash
# 使用 npm 安装
npm install -g netlify-cli

# 或使用 yarn
yarn global add netlify-cli

# 验证安装
netlify --version
```

#### 2. 登录 Netlify

```bash
netlify login
```

浏览器会自动打开，授权登录。

#### 3. 初始化项目

```bash
cd restaurant-system

# 初始化 Netlify 项目
netlify init
```

按提示选择：
- 创建新站点或连接现有站点
- 设置发布目录：`assets`

#### 4. 部署

```bash
# 部署到 Netlify
netlify deploy --prod
```

---

## 配置自定义域名

### 步骤 1: 添加自定义域名

1. 登录 Netlify Dashboard
2. 进入站点设置：**Site settings** → **Domain management**
3. 点击 **"Add custom domain"**
4. 输入域名，例如：
   - `restaurant.example.com` (子域名)
   - `example.com` (根域名)
5. 点击 **"Verify DNS configuration"**

### 步骤 2: 配置 DNS 解析

#### 对于子域名（如 restaurant.example.com）

在你的域名管理面板（阿里云、腾讯云等）添加 CNAME 记录：

```
类型: CNAME
主机记录: restaurant
记录值: your-site-name.netlify.app
TTL: 600
```

#### 对于根域名（如 example.com）

添加 A 记录：

```
类型: A
主机记录: @
记录值: 75.2.70.75 (Netlify的IP)
TTL: 600
```

或添加 CNAME 记录（推荐）：

```
类型: CNAME
主机记录: @
记录值: your-site-name.netlify.app
TTL: 600
```

### 步骤 3: 等待 DNS 生效

- DNS 生效通常需要 5-15 分钟
- 最长可能需要 48 小时
- 可以使用 `nslookup` 或 `dig` 命令检查

```bash
# 检查 DNS 解析
nslookup restaurant.example.com
```

### 步骤 4: 启用 HTTPS

Netlify 会自动为自定义域名配置 HTTPS 证书（Let's Encrypt）。

1. 在 **Domain management** 页面
2. 确保 **"HTTPS"** 已启用
3. 等待证书签发（通常几分钟）

---

## API 代理配置

Netlify 可以作为前端和后端之间的代理，解决跨域问题。

### 当前配置说明

在 `netlify.toml` 中已经配置了 API 代理：

```toml
# 会员 API (端口 8004)
[[redirects]]
  from = "/api/member*"
  to = "http://9.128.251.82:8004/api/member:splat"
  status = 200
  force = true

# 总公司管理 API (端口 8006)
[[redirects]]
  from = "/api/headquarters*"
  to = "http://9.128.251.82:8006/api/headquarters:splat"
  status = 200
  force = true

# 订单相关接口 (端口 8001)
[[redirects]]
  from = "/api/orders*"
  to = "http://9.128.251.82:8001/api/orders:splat"
  status = 200
  force = true

# 其他 API 接口 (端口 8000)
[[redirects]]
  from = "/api/*"
  to = "http://9.128.251.82:8000/api/:splat"
  status = 200
  force = true
```

### 修改后端 IP 地址

如果后端 IP 地址发生变化，需要修改 `netlify.toml`：

```bash
# 在本地编辑 netlify.toml
# 将 YOUR_BACKEND_IP 替换为新的 IP 地址

# 提交更改
git add netlify.toml
git commit -m "Update backend API IP"
git push origin main

# Netlify 会自动重新部署
```

### 测试 API 代理

打开浏览器开发者工具（F12），在 Console 中执行：

```javascript
// 测试健康检查接口
fetch('/api/health')
  .then(r => r.text())
  .then(console.log)

// 测试会员接口
fetch('/api/member/info?phone=13800138000')
  .then(r => r.json())
  .then(console.log)
```

---

## 部署验证

### 1. 基础功能测试

在浏览器中测试以下功能：

#### 门户页面
```
URL: https://your-site.netlify.app
验证: 页面正常显示，所有入口可点击
```

#### 顾客端
```
URL: https://your-site.netlify.app/customer-order-v3.html?table=1
验证: 能够选择菜品、提交订单
```

#### 工作人员端
```
URL: https://your-site.netlify.app/login_standalone.html
验证: 能够登录、查看订单
```

#### 会员中心
```
URL: https://your-site.netlify.app/member_center.html
验证: 能够登录、查看积分
```

#### 总公司后台
```
URL: https://your-site.netlify.app/headquarters_dashboard.html
验证: 能够查看统计数据
```

### 2. API 代理测试

使用浏览器开发者工具测试：

```javascript
// 测试 API 连通性
const testAPI = async () => {
  try {
    const res = await fetch('/api/health');
    console.log('API代理正常:', await res.text());
  } catch (err) {
    console.error('API代理失败:', err);
  }
};

testAPI();
```

### 3. 跨域测试

```javascript
// 测试 CORS
fetch('http://9.128.251.82:8000/api/health', {
  mode: 'cors'
})
  .then(r => r.text())
  .then(console.log);
```

### 4. 性能测试

使用 Lighthouse 或 PageSpeed Insights 测试网站性能：

1. 打开 Chrome DevTools
2. 切换到 **Lighthouse** 标签
3. 点击 **"Analyze page load"**
4. 查看性能报告

目标：
- Performance: > 90
- Accessibility: > 95
- Best Practices: > 95
- SEO: > 90

### 5. 移动端测试

使用 Chrome DevTools 设备模拟器测试：
- iPhone 12 Pro
- iPad Pro
- Samsung Galaxy S21

确保所有页面在移动端都能正常显示和操作。

---

## 常见问题

### Q1: 部署后页面显示空白

**原因**：
- 构建配置错误
- JavaScript 加载失败

**解决方案**：
1. 检查 Publish directory 是否设置为 `assets`
2. 打开浏览器控制台查看错误信息
3. 确认 `netlify.toml` 配置正确

### Q2: API 请求失败 (CORS 错误)

**原因**：
- 后端 CORS 配置问题
- API 代理配置错误
- 后端服务未运行

**解决方案**：
1. 检查后端服务是否运行
2. 检查 `netlify.toml` 中的 API 代理配置
3. 确认后端 API 配置了 CORS

### Q3: 自定义域名无法访问

**原因**：
- DNS 解析未生效
- DNS 配置错误

**解决方案**：
1. 使用 `nslookup` 检查 DNS 解析
2. 等待 DNS 生效（最多 48 小时）
3. 检查 DNS 记录是否正确

### Q4: HTTPS 证书未生成

**原因**：
- DNS 未正确解析到 Netlify
- 域名配置错误

**解决方案**：
1. 确认 DNS 已正确解析
2. 等待 DNS 完全生效
3. 在 Netlify Dashboard 中重新申请证书

### Q5: WebSocket 连接失败

**原因**：
- Netlify 不支持 WebSocket 代理
- 需要直接连接后端

**解决方案**：
在代码中直接使用后端 WebSocket 地址：

```javascript
// 错误（Netlify 不支持）
const ws = new WebSocket('wss://your-site.netlify.app/ws');

// 正确（直接连接后端）
const ws = new WebSocket('ws://9.128.251.82:8001/ws');
```

### Q6: 部署速度慢

**原因**：
- 文件过大
- 网络问题

**解决方案**：
1. 压缩图片资源
2. 使用 Netlify 的 CDN 加速
3. 考虑使用 Netlify 的付费版获得更快速度

### Q7: 如何回滚到上一个版本？

**步骤**：
1. 进入 Netlify Dashboard
2. 点击 **"Deploys"**
3. 找到要回滚的部署版本
4. 点击 **"Publish deploy"** → **"Restore this deploy"**

### Q8: 如何查看部署日志？

**步骤**：
1. 进入 Netlify Dashboard
2. 点击 **"Deploys"**
3. 点击最近的部署记录
4. 点击 **"Deploy log"**

---

## 进阶配置

### 1. 环境变量

在 Netlify Dashboard 中设置环境变量：
1. **Site settings** → **Environment variables**
2. 点击 **"Add a variable"**
3. 添加变量，例如：
   - `API_BASE_URL`: `http://9.128.251.82:8000`
   - `WS_BASE_URL`: `ws://9.128.251.82:8001`

### 2. 表单处理

Netlify 内置表单处理功能：

```html
<form name="contact" method="POST" data-netlify="true">
  <input type="email" name="email" />
  <button type="submit">Submit</button>
</form>
```

### 3. Functions (无服务器函数)

如果需要后端逻辑，可以使用 Netlify Functions：

```javascript
// netlify/functions/hello.js
exports.handler = async (event, context) => {
  return {
    statusCode: 200,
    body: JSON.stringify({ message: "Hello from Netlify!" })
  };
};
```

### 4. 插件

Netlify 支持多种插件：
- Image CDN (图片优化)
- Optimized Images (图片压缩)
- Prerender (预渲染)

---

## 总结

Netlify 部署流程总结：

```
1. 准备代码 (assets/ + netlify.toml)
   ↓
2. 推送到 GitHub
   ↓
3. 在 Netlify 导入项目
   ↓
4. 配置构建设置
   ↓
5. 部署成功
   ↓
6. (可选) 配置自定义域名
   ↓
7. (可选) 启用 HTTPS
   ↓
8. 测试验证
```

---

**相关文档**：
- [Netlify 官方文档](https://docs.netlify.com/)
- [完整商用部署指南](./COMMERCIAL_DEPLOYMENT.md)
- [系统使用手册](./USER_MANUAL.md)

---

**技术支持**：
如遇到问题，请查看 Netlify 社区论坛或联系技术支持。
