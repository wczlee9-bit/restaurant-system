# 🚀 Netlify 部署逐步指南

本指南将手把手教你如何在 Netlify 上部署扫码点餐系统。

---

## 📋 前置条件

### ✅ 准备工作

1. **Netlify 账号**
   - 如果还没有，访问 https://www.netlify.com 注册（免费）
   - 可以使用 GitHub、GitLab 或邮箱注册

2. **确认项目文件已就绪**
   - 位置：`/workspace/projects/`
   - 关键文件：
     - `netlify.toml`（配置文件）
     - `assets/` 目录（前端文件）

---

## 🎯 方法一：手动上传（最简单，推荐新手）

### 步骤 1：准备部署包

在项目目录执行以下命令：

```bash
cd /workspace/projects

# 方法A：使用部署脚本
bash scripts/deploy_netlify.sh

# 方法B：手动打包
zip -r restaurant-system.zip assets/ netlify.toml
```

执行后会生成 `restaurant-system.zip` 文件。

---

### 步骤 2：上传到 Netlify

1. **登录 Netlify**
   - 访问：https://app.netlify.com
   - 使用你的账号密码登录

2. **创建新站点**
   - 点击左上角 **"Add new site"** 按钮
   - 选择 **"Deploy manually"**（手动部署）

3. **上传文件**
   - 点击 **"Choose folder"** 按钮
   - 或直接将 `restaurant-system.zip` 文件拖拽到上传区域
   - 等待上传完成

4. **等待部署**
   - 上传后，Netlify 会自动开始部署
   - 通常需要 1-2 分钟
   - 看到绿色 "Deployed!" 标记表示成功

5. **获取访问地址**
   - 部署完成后，Netlify 会提供一个 URL
   - 例如：`https://random-name-12345.netlify.app`
   - 你可以点击 "Visit site" 直接访问

---

## 🔄 方法二：使用 Netlify CLI（推荐开发者）

### 步骤 1：安装 Netlify CLI

```bash
# 全局安装 Netlify CLI（需要先安装 Node.js）
npm install -g netlify-cli

# 验证安装
netlify --version
```

如果没有 Node.js，访问 https://nodejs.org 下载安装。

---

### 步骤 2：登录 Netlify

```bash
netlify login
```

这会打开浏览器，让你授权 Netlify CLI 访问你的账号。

---

### 步骤 3：部署

```bash
# 进入项目目录
cd /workspace/projects

# 执行部署
netlify deploy --prod --dir=assets
```

按照提示操作：
1. 选择创建新站点或使用现有站点
2. 确认部署设置（默认即可）
3. 等待部署完成

---

### 步骤 4：访问网站

部署成功后，终端会显示你的网站 URL，直接访问即可。

---

## 🌐 方法三：通过 Git 部署（适合持续更新）

### 步骤 1：创建 GitHub 仓库

1. **访问 GitHub**
   - 打开浏览器，访问：https://github.com/new

2. **创建新仓库**
   - Repository name（仓库名）：`restaurant-system`
   - Description（描述）：扫码点餐系统
   - Public/Private（公开/私有）：选择 **Private**（保护用户凭据）
   - 点击 **Create repository** 创建

3. **复制仓库地址**
   - 仓库创建后会显示 URL
   - 例如：`https://github.com/yourusername/restaurant-system.git`

---

### 步骤 2：推送代码到 GitHub

在项目目录执行：

```bash
cd /workspace/projects

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 扫码点餐系统"

# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/yourusername/restaurant-system.git

# 设置主分支
git branch -M main

# 推送到 GitHub
git push -u origin main
```

**如果需要认证**：
- GitHub 不再支持密码登录，需要使用 Personal Access Token
- 获取方法：https://github.com/settings/tokens
- 推送时，用户名输入你的 GitHub 用户名，密码输入 Token

---

### 步骤 3：在 Netlify 中连接 GitHub 仓库

1. **登录 Netlify**
   - 访问：https://app.netlify.com

2. **创建新站点**
   - 点击 **"Add new site"**
   - 选择 **"Import an existing project"**

3. **选择 Git 提供商**
   - 点击 **"GitHub"**
   - 如果需要授权，点击 **"Authorize Netlify"**

4. **选择仓库**
   - 在列表中找到并选择 `restaurant-system` 仓库
   - 点击 **"Import site"**

5. **配置构建设置**
   - **Branch to deploy**（部署分支）：`main`
   - **Build command**（构建命令）：留空（不需要构建）
   - **Publish directory**（发布目录）：`assets`

6. **部署站点**
   - 点击 **"Deploy site"**
   - 等待 1-2 分钟

7. **访问网站**
   - 部署完成后，点击 **"Visit site"**
   - 访问你的新网站

---

## 🔄 后续更新（Git 部署方式）

推送代码后，Netlify 会自动部署：

```bash
# 1. 修改文件
# ... 做一些修改 ...

# 2. 查看修改
git status

# 3. 添加修改
git add .

# 4. 提交修改
git commit -m "feat: 添加新功能"

# 5. 推送到 GitHub
git push

# 6. Netlify 自动检测并部署（1-2分钟）
```

---

## ⚙️ 部署后配置

### 1. 配置 API 地址（重要！）

部署到 Netlify 后，需要确保 API 地址配置正确。

当前系统已支持自动检测 API 地址：
- Netlify 环境：自动使用云端 API
- 本地环境：使用 localhost

**验证 API 配置**：

在浏览器中打开网站，按 `F12` 打开开发者工具，查看 Console 标签：
- 如果看到 "API地址已更新: http://9.128.251.82:8000/api"，说明配置正确
- 如果看到错误，可能需要手动修改 API 地址

**手动修改 API 地址**（如果需要）：

编辑 `assets/restaurant_full_test.html`，找到 `detectApiBase()` 函数，确认包含：

```javascript
const detectApiBase = () => {
    // Netlify 环境
    if (window.location.hostname.includes('netlify.app')) {
        return 'http://9.128.251.82:8000/api';  // 云端 API
    }
    // 本地环境
    return 'http://localhost:8000/api';
};
```

---

### 2. 测试系统功能

部署完成后，请测试以下功能：

#### ✅ 基础测试
- [ ] 访问主页，页面正常显示
- [ ] 点击 "开始点餐" 按钮
- [ ] 选择桌号（例如：8号桌）
- [ ] 浏览菜单

#### ✅ 点餐流程测试
- [ ] 添加商品到购物车
- [ ] 修改商品数量
- [ ] 提交订单
- [ ] 查看订单状态

#### ✅ 多角色测试
- [ ] 切换到"厨师"角色
- [ ] 查看待制作订单
- [ ] 更新订单状态

- [ ] 切换到"传菜员"角色
- [ ] 查看待传菜订单
- [ ] 完成传菜

- [ ] 切换到"收银员"角色
- [ ] 查看待支付订单
- [ ] 完成支付

- [ ] 切换到"店长"角色
- [ ] 查看营收数据
- [ ] 查看订单统计

#### ✅ WebSocket 实时通知测试
- [ ] 打开多个浏览器窗口（不同角色）
- [ ] 顾客提交订单，检查其他角色是否收到通知
- [ ] 查看订单状态是否实时更新

---

## 🎨 自定义配置（可选）

### 1. 自定义域名

1. 进入 Netlify Dashboard
2. 点击 **"Site configuration"**
3. 点击 **"Domain management"**
4. 点击 **"Add custom domain"**
5. 输入你的域名（例如：`restaurant.example.com`）
6. 按照提示配置 DNS

### 2. 修改站点名称

1. 进入 Netlify Dashboard
2. 点击 **"Site configuration"**
3. 修改 **"Site name"**
4. Netlify 会自动更新 URL

### 3. 环境变量

在 Netlify 中配置敏感信息：

1. 进入 **"Site settings"** → **"Build & deploy"** → **"Environment variables"**
2. 点击 **"Add a variable"**
3. 添加变量：
   - Key: `API_BASE_URL`
   - Value: `http://9.128.251.82:8000/api`

---

## 🔍 常见问题

### Q1: 部署后页面空白？

**原因**：可能是 JS 文件加载失败或 API 请求失败

**解决方法**：
1. 按 `F12` 打开开发者工具
2. 查看 **Console** 标签，查找错误信息
3. 查看 **Network** 标签，检查 API 请求是否成功

---

### Q2: API 请求失败，提示 CORS 错误？

**原因**：跨域访问被限制

**解决方法**：
1. 确认后端 API 服务已启动
2. 检查 API 地址配置是否正确
3. 联系开发者在 API 服务中添加 CORS 配置

---

### Q3: 图片无法加载？

**原因**：二维码图片路径错误

**解决方法**：
1. 确认 `assets/qrcodes/` 目录已上传
2. 检查图片路径是否正确（应为 `qrcodes/table_1.png`）

---

### Q4: 如何更新部署？

**解决方法**：

- **方法一（手动上传）**：重新上传 zip 文件
- **方法二（Netlify CLI）**：执行 `netlify deploy --prod --dir=assets`
- **方法三（Git）**：推送代码，Netlify 自动部署

---

### Q5: 部署需要多长时间？

**答案**：
- 首次部署：1-3 分钟
- 后续更新：1-2 分钟
- 如果文件很多，可能需要更长时间

---

## 🎉 部署成功！

恭喜你！部署成功后，你将获得：

✅ **公开可访问的网站 URL**
   - 例如：`https://restaurant-system.netlify.app`

✅ **自动 HTTPS 加密**
   - Netlify 自动提供 HTTPS 证书

✅ **全球 CDN 加速**
   - 用户访问速度更快

✅ **多设备支持**
   - 手机、平板、电脑均可访问

✅ **持续更新能力**
   - 推送代码自动部署

✅ **版本管理**
   - 可随时回滚到之前版本

---

## 📚 更多资源

- **Netlify 官方文档**：https://docs.netlify.com
- **完整部署指南**：[NETLIFY_DEPLOY.md](NETLIFY_DEPLOY.md)
- **快速开始指南**：[NETLIFY_QUICKSTART.md](NETLIFY_QUICKSTART.md)
- **GitHub 部署指南**：[GITHUB_DEPLOY.md](GITHUB_DEPLOY.md)

---

## 🆘 需要帮助？

如果遇到问题，可以：

1. 查看浏览器控制台（F12）的错误信息
2. 查看 Netlify 部署日志
3. 检查 API 服务是否正常运行
4. 参考本文档的"常见问题"部分

---

**祝你部署顺利！🚀**
