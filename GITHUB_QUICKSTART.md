# ⚡ GitHub 部署到 Netlify - 快速开始

## ✅ 准备工作已完成！

您已有：
- ✅ GitHub 账号
- ✅ Netlify 账号（用户名和密码）
- ✅ 本地 Git 仓库已初始化并提交

---

## 🚀 立即开始（10分钟）

### 第 1 步：创建 GitHub 仓库（2分钟）

1. 访问：https://github.com/new
2. Repository name: `restaurant-system`
3. 选择 **Private**（保护用户凭据）
4. 点击 **Create repository**
5. 复制仓库 URL，例如：`https://github.com/yourusername/restaurant-system.git`

---

### 第 2 步：推送代码到 GitHub（3分钟）

```bash
# 进入项目目录
cd /workspace/projects

# 添加远程仓库（替换为您的仓库地址）
git remote add origin https://github.com/yourusername/restaurant-system.git

# 首次推送（如果需要认证，输入 GitHub 用户名和密码或 Token）
git push -u origin main
```

**如果使用 Personal Access Token**：
1. 访问：https://github.com/settings/tokens
2. Generate new token (classic) → 权限选择 `repo`
3. 推送时，用户名输入 GitHub 用户名，密码输入 token

**如果使用 SSH**：
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

### 第 3 步：在 Netlify 中连接 GitHub（3分钟）

1. 访问：https://app.netlify.com
2. 使用您的 Netlify 账号密码登录
3. 点击 **"Add new site"** → **"Import an existing project"**
4. 点击 **"GitHub"**，授权 Netlify 访问 GitHub
5. 选择 `restaurant-system` 仓库
6. 点击 **"Import site"**

---

### 第 4 步：配置构建设置（1分钟）

在 Netlify 部署配置页面：

- **Branch to deploy**: `main`
- **Build command**:（留空）
- **Publish directory**: `assets`
- **Site name**: `restaurant-system`（可选，自定义名称）

点击 **"Deploy site"**

---

### 第 5 步：访问您的网站（1分钟）

- 等待 1-2 分钟部署完成
- Netlify 会提供 URL：`https://restaurant-system.netlify.app`
- 点击 **"Visit site"** 或直接复制 URL 访问

**🎉 恭喜！您的网站已上线！**

---

## 🔐 用户账号信息

**重要：请妥善保管，不要泄露！**

### 角色账号

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 顾客 | customer | customer123 | 浏览菜单、点餐、支付 |
| 厨师 | chef | chef123 | 查看订单、制作菜品 |
| 传菜员 | waiter | waiter123 | 传菜、确认上桌 |
| 收银员 | cashier | cashier123 | 处理支付、打印小票 |
| 店长 | manager | manager123 | 管理店铺、查看数据 |

### 配置文件位置

- **用户配置**：`assets/config/users.json`
- **详细说明**：`USER_CREDENTIALS.md`（仅在本地，未提交到 GitHub）

**安全提示**：
- ✅ `USER_CREDENTIALS.md` 已添加到 `.gitignore`，不会提交到 GitHub
- ✅ 如果使用私有仓库，可以提交 `users.json`
- ❌ 如果使用公开仓库，务必将 `users.json` 添加到 `.gitignore`

---

## 🔄 持续更新（发现问题，快速调整）

### 提交更改的流程

```bash
# 1. 查看当前状态
git status

# 2. 添加修改的文件
git add .

# 3. 提交更改
git commit -m "feat: 添加XX功能"

# 4. 推送到 GitHub
git push
```

### Netlify 自动部署

- ✅ 推送到 GitHub 后，Netlify 会自动部署
- ✅ 通常需要 1-2 分钟
- ✅ 网站自动更新

### 查看部署日志

1. 访问 Netlify Dashboard
2. 进入您的站点
3. 点击 **"Deploys"** 标签
4. 查看最新部署的日志

### 回滚版本

如果发现问题需要回滚：

1. 进入 Netlify Dashboard → **Deploys**
2. 找到之前的版本
3. 点击 **"Publish deploy"**

---

## 🧪 部署后测试

### 测试清单

- [ ] 访问主页：`https://restaurant-system.netlify.app`
- [ ] 测试点餐流程：`https://restaurant-system.netlify.app/restaurant_full_test.html?table=8`
- [ ] 打开浏览器控制台（F12），查看 Network 标签
- [ ] 确认 API 请求返回 200 OK
- [ ] 使用不同角色账号登录
- [ ] 测试每个角色的功能

### 测试角色登录

1. **顾客**：
   - 用户名：`customer`
   - 密码：`customer123`
   - 测试：浏览菜单、点餐、支付

2. **厨师**：
   - 用户名：`chef`
   - 密码：`chef123`
   - 测试：查看订单、制作菜品

3. **传菜员**：
   - 用户名：`waiter`
   - 密码：`waiter123`
   - 测试：传菜、确认上桌

4. **收银员**：
   - 用户名：`cashier`
   - 密码：`cashier123`
   - 测试：处理支付、打印小票

5. **店长**：
   - 用户名：`manager`
   - 密码：`manager123`
   - 测试：查看数据、管理店铺

---

## 🎯 配置 API 地址

部署到 Netlify 后，需要配置 API 地址。

### 方法一：在 Netlify 中配置环境变量（推荐）

1. Netlify Dashboard → Site Settings → Build & deploy → Environment variables
2. 点击 **"Add a variable"**
3. 添加：
   - Key: `VUE_APP_API_BASE`
   - Value: `http://9.128.251.82:8000/api`
4. 保存

### 方法二：在代码中硬编码（临时方案）

在 `assets/restaurant_full_test.html` 中：

```javascript
const detectApiBase = () => {
    // Netlify 环境
    return 'http://9.128.251.82:8000/api';
};
```

**注意**：每次部署到 Netlify 后需要手动修改，推荐使用方法一。

---

## ❓ 常见问题

### Q: Git 推送失败？

**A**: 
1. 确认远程仓库地址：`git remote -v`
2. 如果使用 HTTPS，可能需要 Personal Access Token
3. 如果使用 SSH，确认密钥已添加到 GitHub

### Q: Netlify 部署失败？

**A**: 
1. 查看 Netlify Dashboard → Deploys 中的日志
2. 检查构建命令和发布目录配置是否正确
3. 确认文件格式正确

### Q: API 请求失败？

**A**: 
1. 确认 API 地址配置正确
2. 打开浏览器控制台（F12）查看 Network 标签
3. 检查后端 API 服务是否运行
4. 确认没有跨域问题（CORS）

### Q: 如何修改用户密码？

**A**: 
1. 编辑 `assets/config/users.json`
2. 修改对应角色的密码
3. 提交并推送：`git add . && git commit -m "update: 修改用户密码" && git push`

---

## 📚 详细文档

- **完整 GitHub 部署指南**：[GITHUB_DEPLOY.md](GITHUB_DEPLOY.md)
- **Netlify 部署指南**：[NETLIFY_DEPLOY.md](NETLIFY_DEPLOY.md)
- **用户凭据详细说明**：[USER_CREDENTIALS.md](USER_CREDENTIALS.md)

---

## 🎊 部署成功！

现在您可以：

✅ 持续开发新功能  
✅ 提交代码到 GitHub  
✅ 自动部署到 Netlify  
✅ 实时查看效果  
✅ 快速修复问题  

---

**开始部署吧！** 🚀

1. 创建 GitHub 仓库：https://github.com/new
2. 推送代码：`git push -u origin main`
3. 连接 Netlify：https://app.netlify.com

祝您部署顺利！
