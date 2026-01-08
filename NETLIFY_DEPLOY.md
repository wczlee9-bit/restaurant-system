# 🚀 Netlify 部署指南

## 📋 概述

本指南将帮助您将扫码点餐系统的前端部分部署到 Netlify，实现快速访问和测试。

## 🎯 部署目标

- ✅ 将前端静态文件部署到 Netlify
- ✅ 配置自定义域名（可选）
- ✅ 实现HTTPS访问
- ✅ 提供稳定的测试环境

## 📦 准备工作

### 1. Netlify 账号

如果您还没有 Netlify 账号，请先注册：
- 访问 https://www.netlify.com
- 使用 GitHub、GitLab、Bitbucket 或邮箱注册

### 2. 项目文件结构

确认项目包含以下关键文件：
```
/workspace/projects/
├── netlify.toml          # Netlify 配置文件
├── assets/               # 前端静态文件目录
│   ├── index.html
│   ├── ACCESS_GUIDE.html
│   ├── restaurant_full_test.html
│   └── qrcodes/
└── README.md
```

## 🚀 部署方法

### 方法一：通过 Netlify Dashboard 手动部署（推荐）

#### 步骤 1：准备部署文件

将 `assets/` 目录打包为 zip 文件：
```bash
cd /workspace/projects
zip -r restaurant-system.zip assets/ netlify.toml
```

#### 步骤 2：登录 Netlify

1. 访问 https://app.netlify.com
2. 登录您的账号

#### 步骤 3：创建新站点

1. 点击 "Add new site" → "Deploy manually"
2. 点击 "Choose folder" 或拖拽 `restaurant-system.zip` 到上传区域
3. 等待上传和部署完成（通常需要 1-2 分钟）

#### 步骤 4：验证部署

部署完成后，Netlify 会提供一个默认域名，例如：
```
https://random-name-12345.netlify.app
```

访问这个地址，您应该能看到主页面。

### 方法二：通过 Git 部署（适合持续更新）

#### 步骤 1：准备 Git 仓库

```bash
cd /workspace/projects
git init
git add netlify.toml assets/
git commit -m "Initial Netlify deployment"
```

#### 步骤 2：推送到 GitHub/GitLab

```bash
# 推送到 GitHub
git remote add origin https://github.com/yourusername/restaurant-system.git
git push -u origin main
```

#### 步骤 3：在 Netlify 中连接仓库

1. 登录 Netlify Dashboard
2. 点击 "Add new site" → "Import an existing project"
3. 选择您的 Git 提供商（GitHub/GitLab/Bitbucket）
4. 选择仓库并导入
5. 配置构建设置：
   - **Build command**:（留空）
   - **Publish directory**: `assets`
6. 点击 "Deploy site"

#### 步骤 4：验证部署

访问 Netlify 提供的域名，确认部署成功。

### 方法三：使用 Netlify CLI（自动化部署）

#### 步骤 1：安装 Netlify CLI

```bash
npm install -g netlify-cli
```

#### 步骤 2：登录 Netlify

```bash
netlify login
```

#### 步骤 3：初始化项目

```bash
cd /workspace/projects
netlify init
```

按照提示操作，选择：
- "Create & configure a new site"
- 选择团队和站点名称

#### 步骤 4：部署

```bash
netlify deploy --prod --dir=assets
```

## ⚙️ 配置说明

### netlify.toml 配置文件

```toml
[build]
  publish = "assets"
  command = "# No build command needed"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
```

### 重要配置说明

1. **publish 目录**: 设置为 `assets`，因为前端文件都在这个目录
2. **redirects**: 所有路由重定向到 `index.html`，支持单页应用
3. **headers**: 添加安全头，保护网站安全
4. **Cache-Control**: 对静态资源设置长期缓存，提高加载速度

## 🔗 配置 API 地址

部署到 Netlify 后，需要修改 API 地址配置。

### 当前 API 配置

API 服务运行在云端沙盒环境：
- 主地址：`http://9.128.251.82:8000`
- 备用地址：`http://169.254.100.163:8000`

### 修改 API 地址

在 `assets/restaurant_full_test.html` 中找到 API 配置部分：

```javascript
// 自动检测API地址
const detectApiBase = () => {
    // 在 Netlify 环境中，使用云端API地址
    if (window.location.hostname.includes('netlify.app')) {
        return 'http://9.128.251.82:8000/api';  // 使用云端API
    }
    // 本地开发环境
    return 'http://localhost:8000/api';
};
```

### 注意事项

⚠️ **跨域问题（CORS）**

如果遇到跨域问题，需要在后端 API 服务中添加 CORS 配置：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（生产环境应限制为特定域名）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🌐 自定义域名（可选）

### 步骤 1：购买域名

在 GoDaddy、Namecheap 或阿里云购买域名。

### 步骤 2：在 Netlify 中添加域名

1. 进入 Site Settings → Domain management
2. 点击 "Add custom domain"
3. 输入您的域名（例如：`restaurant.yourdomain.com`）

### 步骤 3：配置 DNS

Netlify 会提供 DNS 配置信息，按照提示在域名提供商处配置：
- 添加 CNAME 记录指向 Netlify

### 步骤 4：启用 HTTPS

1. 进入 Site Settings → Domain management → HTTPS
2. 点击 "Verify DNS configuration"
3. 等待 SSL 证书生成（通常需要几分钟）

## 📊 部署后测试

### 1. 访问主页

访问 Netlify 提供的域名或自定义域名：
```
https://your-site.netlify.app
```

### 2. 测试点餐流程

1. 选择桌号（推荐 8 号桌）
2. 浏览菜单
3. 添加商品到购物车
4. 选择支付方式
5. 提交订单
6. 检查订单状态

### 3. 测试角色切换

在测试平台中切换不同角色：
- 顾客：点餐、支付
- 厨师：接单、烹饪
- 传菜员：传菜
- 收银员：结算
- 店长：查看数据

### 4. 检查 API 连接

打开浏览器控制台（F12），检查：
- API 请求是否成功
- 数据是否正常返回
- 是否有 CORS 错误

## 🔄 更新部署

### 方法一：通过 Netlify Dashboard

1. 修改本地文件
2. 在 Netlify Dashboard 中点击 "Deploys"
3. 点击 "Trigger deploy" → "Deploy site"

### 方法二：通过 Git

```bash
# 修改文件后
git add .
git commit -m "Update features"
git push
```

Netlify 会自动检测到 Git 推送并触发部署。

### 方法三：使用 Netlify CLI

```bash
netlify deploy --prod --dir=assets
```

## 🐛 常见问题

### Q1: 部署后页面空白

**解决方案：**
- 检查浏览器控制台是否有错误
- 确认 `assets/` 目录已正确上传
- 检查 `netlify.toml` 配置是否正确

### Q2: API 请求失败

**解决方案：**
- 确认 API 服务地址配置正确
- 检查后端 API 是否运行
- 查看 CORS 配置是否正确

### Q3: 图片无法加载

**解决方案：**
- 检查图片路径是否正确
- 确认 `qrcodes/` 目录已上传
- 检查文件名大小写

### Q4: 部署后样式丢失

**解决方案：**
- 确认 CDN 链接可访问（Element Plus、Vue）
- 检查网络连接
- 清除浏览器缓存

### Q5: 如何回滚到之前的版本

**解决方案：**
1. 进入 Netlify Dashboard
2. 点击 "Deploys"
3. 找到要回滚的版本
4. 点击 "Publish deploy"

## 📈 性能优化

### 1. 启用缓存

已在 `netlify.toml` 中配置了静态资源缓存：
- 图片：1年
- JS/CSS：1年

### 2. 启用压缩

Netlify 默认启用 Gzip/Brotli 压缩。

### 3. 使用 CDN

Netlify 自动使用全球 CDN 加速访问。

### 4. 图片优化

对于大图片，建议先压缩后再上传。

## 🔐 安全建议

1. **使用 HTTPS**：Netlify 默认提供免费 SSL 证书
2. **限制 CORS**：生产环境应限制允许的域名
3. **添加安全头**：已在 `netlify.toml` 中配置
4. **定期更新**：保持依赖库最新版本

## 📞 技术支持

如果遇到问题：
1. 查看 Netlify 部署日志
2. 检查浏览器控制台错误
3. 参考 Netlify 官方文档：https://docs.netlify.com
4. 联系技术支持团队

## 🎉 部署完成后

部署成功后，您将获得：
- ✅ 一个可以公开访问的网站
- ✅ 自动 HTTPS 加密
- ✅ 全球 CDN 加速
- ✅ 自动部署和更新
- ✅ 详细的部署日志

现在您可以：
1. 分享网站链接给他人测试
2. 在任何设备上访问（手机、平板、电脑）
3. 随时更新功能，自动部署
4. 查看访问统计和分析

---

**祝您部署成功！🚀**
