# 🚀 GitHub 部署到 Netlify 完整指南

## 📋 前置准备

### 1. GitHub 账号
- ✅ 确认您已有 GitHub 账号
- ✅ 登录 GitHub：https://github.com

### 2. Netlify 账号
- ✅ 确认您已有 Netlify 账号（用户名和密码）
- ✅ 登录 Netlify：https://app.netlify.com

### 3. 本地 Git 配置
```bash
# 检查 Git 是否安装
git --version

# 配置 Git 用户信息（如果还没配置）
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 🎯 完整部署流程

### 第一步：创建 GitHub 仓库

1. **访问 GitHub**
   - 打开浏览器，访问：https://github.com/new

2. **创建新仓库**
   - Repository name: `restaurant-system`（或您喜欢的名称）
   - Description: `扫码点餐系统`
   - Public/Private: 选择 **Private**（推荐，保护用户凭据）
   - 不要勾选 "Add a README file"
   - 不要勾选其他选项
   - 点击 **Create repository**

3. **记录仓库地址**
   - 仓库创建后，复制仓库 URL，例如：
     ```
     https://github.com/yourusername/restaurant-system.git
     ```

---

### 第二步：初始化本地 Git 仓库

```bash
# 进入项目目录
cd /workspace/projects

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交初始版本
git commit -m "Initial commit: 扫码点餐系统 - 初始化"
```

---

### 第三步：连接远程仓库并推送

```bash
# 添加远程仓库（替换为您的仓库地址）
git remote add origin https://github.com/yourusername/restaurant-system.git

# 设置主分支名称
git branch -M main

# 首次推送
git push -u origin main
```

**如果需要认证**：
- 选项 A：使用 GitHub Personal Access Token（推荐）
  1. 访问：https://github.com/settings/tokens
  2. 点击 "Generate new token (classic)"
  3. 设置权限：选中 "repo"
  4. 生成 token 并复制
  5. 推送时，用户名输入 GitHub 用户名，密码输入 token

- 选项 B：使用 SSH 密钥
  ```bash
  # 生成 SSH 密钥
  ssh-keygen -t ed25519 -C "your.email@example.com"
  
  # 复制公钥
  cat ~/.ssh/id_ed25519.pub
  
  # 添加到 GitHub: Settings → SSH and GPG keys → New SSH key
  
  # 切换为 SSH 远程地址
  git remote set-url origin git@github.com:yourusername/restaurant-system.git
  
  # 推送
  git push -u origin main
  ```

---

### 第四步：在 Netlify 中连接 GitHub 仓库

1. **登录 Netlify**
   - 访问：https://app.netlify.com
   - 使用您的账号密码登录

2. **创建新站点**
   - 点击 **"Add new site"**
   - 选择 **"Import an existing project"**

3. **选择 Git 提供商**
   - 点击 **"GitHub"**
   - 如果需要授权，点击 **"Authorize Netlify"**
   - 选择您的账户
   - 授予权限（读取仓库权限）

4. **选择仓库**
   - 在列表中找到并选择 `restaurant-system` 仓库
   - 点击 **"Import site"**

5. **配置构建设置**

   **基本设置**：
   - **Branch to deploy**: `main`
   - **Build command**:（留空）
   - **Publish directory**: `assets`

   **高级设置**（可选）：
   - **Site name**: `restaurant-system`（会生成 URL：restaurant-system.netlify.app）
   - 或者自定义：`my-restaurant`

6. **部署站点**
   - 点击 **"Deploy site"**
   - 等待 1-2 分钟

7. **访问您的网站**
   - 部署完成后，Netlify 会提供一个 URL
   - 例如：`https://restaurant-system.netlify.app`
   - 点击 "Visit site" 或直接复制 URL 访问

---

## 🔄 持续更新流程

### 提交新更改

```bash
# 1. 查看当前状态
git status

# 2. 添加修改的文件
git add .

# 3. 提交更改（写清楚做了什么）
git commit -m "feat: 添加XX功能"

# 4. 推送到 GitHub
git push
```

### Netlify 自动部署

- ✅ 推送到 GitHub 后，Netlify 会自动检测到新的提交
- ✅ 自动触发部署（通常需要 1-2 分钟）
- ✅ 部署完成后，网站自动更新

### 查看部署日志

1. 访问 Netlify Dashboard
2. 进入您的站点
3. 点击 **"Deploys"** 标签
4. 查看最新部署的详细日志

### 回滚到之前的版本

1. 进入 Netlify Dashboard
2. 点击 **"Deploys"**
3. 找到要回滚的版本
4. 点击 **"Publish deploy"**

---

## ⚙️ Netlify 高级配置

### 1. 配置环境变量（推荐）

在 Netlify 中存储敏感信息（如 API 地址）：

1. 进入 Site Settings → Build & deploy → Environment variables
2. 点击 **"Add a variable"**
3. 添加：
   - Key: `VUE_APP_API_BASE`
   - Value: `http://9.128.251.82:8000/api`
4. 保存

### 2. 配置自定义域名

**方式一：Netlify 子域名**
1. Site Settings → Domain management
2. 在 "Netlify subdomain" 中输入自定义名称
3. 点击 "Save"

**方式二：自定义域名**
1. 购买域名（GoDaddy、阿里云等）
2. Site Settings → Domain management → Add custom domain
3. 输入您的域名
4. 按照提示配置 DNS：
   - 添加 CNAME 记录指向 `your-site.netlify.app`
5. 等待 SSL 证书生成（几分钟）

### 3. 配置 HTTPS

Netlify 默认提供免费 SSL 证书（Let's Encrypt）：
1. Site Settings → Domain management → HTTPS
2. 点击 "Verify DNS configuration"
3. 等待证书生成
4. 强制 HTTPS 开关打开

### 4. 配置重定向规则

在 `netlify.toml` 中已配置基本重定向规则，如需修改：

```toml
[[redirects]]
  from = "/old-path"
  to = "/new-path"
  status = 301
```

---

## 🔐 保护用户凭据

### 重要：不要将 `USER_CREDENTIALS.md` 提交到公开仓库！

**方法一：添加到 .gitignore**

编辑 `.gitignore` 文件，添加：
```
USER_CREDENTIALS.md
```

**方法二：仅提交到私有仓库**

- ✅ 如果您的 GitHub 仓库是 **Private**，可以提交 `USER_CREDENTIALS.md`
- ❌ 如果是 **Public**，务必添加到 `.gitignore`

**方法三：使用环境变量**

更安全的方式是使用 Netlify 环境变量存储敏感信息：

1. 在 `assets/config/users.json` 中使用占位符：
```json
{
  "users": [
    {
      "username": "{{CUSTOMER_USERNAME}}",
      "password": "{{CUSTOMER_PASSWORD}}"
    }
  ]
}
```

2. 在 Netlify 中配置环境变量：
   - Key: `CUSTOMER_USERNAME`
   - Value: `customer`

3. 在代码中读取环境变量（需要使用 Netlify Functions 或在构建时替换）

---

## 🧪 部署后测试

### 基本功能测试

1. **访问主页**
   - URL: `https://your-site.netlify.app`
   - 检查页面是否正常显示

2. **测试点餐流程**
   - URL: `https://your-site.netlify.app/restaurant_full_test.html?table=8`
   - 浏览菜单、添加商品、提交订单

3. **测试 API 连接**
   - 打开浏览器控制台（F12）
   - 查看 Network 标签
   - 确认 API 请求返回 200 OK

4. **测试角色登录**
   - 使用提供的用户名和密码登录
   - 测试每个角色的功能

### 多设备测试

- ✅ PC 浏览器测试
- ✅ 手机浏览器测试
- ✅ 平板浏览器测试
- ✅ 不同浏览器测试（Chrome、Safari、Firefox、Edge）

---

## 🐛 常见问题

### Q1: Git 推送失败？

**A**: 检查以下几点：
1. 确认远程仓库地址正确：`git remote -v`
2. 确认有权限推送仓库
3. 如果使用 HTTPS，可能需要使用 Personal Access Token
4. 如果使用 SSH，确认 SSH 密钥已添加到 GitHub

### Q2: Netlify 部署失败？

**A**: 查看部署日志：
1. 进入 Netlify Dashboard
2. 点击 "Deploys"
3. 查看最新部署的详细日志
4. 常见原因：
   - 构建命令错误（应为空）
   - 发布目录错误（应为 `assets`）
   - 文件损坏

### Q3: 页面空白或样式丢失？

**A**: 检查：
1. CDN 链接是否可访问（Element Plus、Vue）
2. 浏览器控制台是否有错误（F12）
3. 文件路径是否正确

### Q4: API 请求失败？

**A**: 检查：
1. API 地址配置是否正确
2. 后端 API 服务是否运行
3. 是否有跨域问题（CORS）

### Q5: 推送后 Netlify 没有自动部署？

**A**: 检查：
1. Netlify 是否正确连接到 GitHub 仓库
2. 推送的分支是否正确（应为 `main`）
3. Netlify 是否开启了自动部署（默认开启）

---

## 📈 性能优化建议

### 1. 启用图片优化

Netlify 会自动优化图片，但建议：
- 使用 WebP 格式
- 压缩图片大小
- 使用懒加载

### 2. 启用缓存

`netlify.toml` 中已配置静态资源缓存：
- JS/CSS：1年
- 图片：1年

### 3. 使用 CDN

Netlify 默认使用全球 CDN，无需额外配置。

### 4. 代码分割

Vue 项目建议：
- 使用动态导入（`import()`）
- 路由懒加载
- 组件懒加载

---

## 📊 监控和分析

### Netlify Analytics

1. 进入 Site Settings → Analytics
2. 开启 Netlify Analytics
3. 查看访问量、页面浏览量、地理位置等

### 添加 Google Analytics

1. 在 `assets/index.html` 中添加 Google Analytics 代码
2. 或在 Netlify 中配置（Site Settings → Analytics）

---

## 🎯 下一步

部署成功后，您可以：

1. ✅ 持续开发新功能
2. ✅ 提交代码到 GitHub
3. ✅ 自动部署到 Netlify
4. ✅ 实时查看效果
5. ✅ 收集用户反馈
6. ✅ 快速迭代优化

---

## 📞 需要帮助？

- **Netlify 文档**: https://docs.netlify.com
- **GitHub 文档**: https://docs.github.com
- **联系技术支持**

---

**祝您部署顺利！** 🚀
