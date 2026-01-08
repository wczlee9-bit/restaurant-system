# 🚀 GitHub + Netlify 部署完整教程

本教程将手把手教你如何使用 GitHub 将扫码点餐系统部署到 Netlify。

---

## 📋 准备工作

### ✅ 第一步：确认账号

1. **GitHub 账号**
   - 如果没有，访问 https://github.com 注册（免费）
   - 确保记住用户名和密码

2. **Netlify 账号**
   - 如果没有，访问 https://www.netlify.com 注册（免费）
   - 可以使用 GitHub 账号直接登录 Netlify（推荐）

---

## 🌐 第二步：创建 GitHub 仓库

### 2.1 登录 GitHub

1. 打开浏览器，访问 https://github.com
2. 点击右上角 **"Sign in"** 登录你的 GitHub 账号

### 2.2 创建新仓库

1. 登录后，点击右上角的 **"+"** 图标
2. 选择 **"New repository"**

### 2.3 填写仓库信息

在创建页面填写：

| 选项 | 填写内容 |
|------|---------|
| **Repository name** | `restaurant-system`（或你喜欢的名字） |
| **Description** | 扫码点餐系统（可留空） |
| **Public/Private** | 选择 **Private**（私有）⭐ 重要！ |
| **Add a README file** | ❌ 不要勾选 |
| **Add .gitignore** | ❌ 不要勾选 |
| **Choose a license** | ❌ 不要勾选 |

**为什么选择 Private？**
- 保护用户凭据（config/users.json）
- 避免敏感信息泄露
- 只有你能访问

### 2.4 创建仓库

点击页面底部的 **"Create repository"** 绿色按钮

### 2.5 保存仓库地址

创建成功后，你会看到类似这样的地址：
```
https://github.com/你的用户名/restaurant-system.git
```

**把这个地址复制保存下来，后面需要用到！**

---

## 💻 第三步：配置 Git 并推送代码

### 3.1 进入项目目录

打开终端（或命令行），进入项目目录：

```bash
cd /workspace/projects
```

### 3.2 检查 Git 配置

检查 Git 是否已配置用户信息：

```bash
git config user.name
git config user.email
```

如果有输出，说明已配置，跳过下一步。
如果没有输出，执行：

```bash
# 配置你的名字
git config --global user.name "Your Name"

# 配置你的邮箱（与 GitHub 邮箱一致）
git config --global user.email "your.email@example.com"
```

### 3.3 初始化 Git 仓库

```bash
git init
```

这会在当前目录创建一个 `.git` 文件夹。

### 3.4 添加所有文件

```bash
git add .
```

这会将所有文件添加到暂存区。

**⚠️ 重要：确保 netlify.toml 和 assets/ 目录都被添加！**

### 3.5 提交更改

```bash
git commit -m "Initial commit: 扫码点餐系统 - 初始化"
```

这会创建第一个提交。

### 3.6 添加远程仓库

将你的 GitHub 仓库地址添加为远程仓库：

```bash
# 替换为你的仓库地址
git remote add origin https://github.com/你的用户名/restaurant-system.git
```

**示例**：
```bash
git remote add origin https://github.com/zhangsan/restaurant-system.git
```

### 3.7 设置主分支

```bash
git branch -M main
```

这会将主分支命名为 `main`。

### 3.8 推送代码到 GitHub

```bash
git push -u origin main
```

### 3.9 认证（重要！）

**GitHub 不再支持密码登录**，需要使用 Personal Access Token。

#### 方式 A：使用 Personal Access Token（推荐）

1. **生成 Token**

   - 访问：https://github.com/settings/tokens
   - 点击 **"Generate new token"** → **"Generate new token (classic)"**
   - 填写：
     - **Note**: `Netlify Deploy`
     - **Expiration**: 选择 `90 days` 或 `No expiration`
     - **Select scopes**: 勾选 **`repo`**（这很重要！）
   - 点击 **"Generate token"**

2. **复制 Token**

   ⚠️ **只出现一次，立即复制并保存！**

   Token 看起来像这样：
   ```
   ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **使用 Token 登录**

   当执行 `git push` 时：
   - **Username**: 输入你的 GitHub 用户名
   - **Password**: 粘贴刚才生成的 Token（不是你的 GitHub 密码！）

   ```
   Username: zhangsan
   Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

#### 方式 B：配置 Git 凭据缓存（避免每次输入）

如果你不想每次都输入 Token，可以配置 Git 记住凭据：

```bash
# 配置 Git 记住凭据（缓存1小时）
git config --global credential.helper cache

# 或者永久记住（不推荐共享电脑）
git config --global credential.helper store
```

这样，第一次输入后，后续推送就不需要重复输入了。

#### 方式 C：使用 SSH 密钥（更安全，但配置复杂）

如果你熟悉 SSH，可以配置 SSH 密钥：

```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your.email@example.com"

# 复制公钥
cat ~/.ssh/id_ed25519.pub

# 添加到 GitHub: Settings → SSH and GPG keys → New SSH key

# 切换远程地址为 SSH
git remote set-url origin git@github.com:你的用户名/restaurant-system.git

# 推送（无需密码）
git push -u origin main
```

### 3.10 确认推送成功

推送成功后，你应该看到类似这样的输出：

```
Enumerating objects: XXX, done.
Counting objects: 100% (XXX/XXX), done.
Delta compression using up to 8 threads
Compressing objects: 100% (XXX/XXX), done.
Writing objects: 100% (XXX/XXX), done.
Total XXX (delta XX), reused 0 (delta 0), pack-reused 0
To https://github.com/你的用户名/restaurant-system.git
 * [new branch]      main -> main
```

### 3.11 验证 GitHub 仓库

刷新你的 GitHub 仓库页面，你应该能看到所有文件已经上传成功！

---

## 🔗 第四步：在 Netlify 中连接 GitHub 仓库

### 4.1 登录 Netlify

1. 打开浏览器，访问 https://app.netlify.com
2. 使用你的账号登录（可以用 GitHub 账号登录）

### 4.2 创建新站点

1. 登录后，点击左上角的 **"Add new site"** 按钮
2. 选择 **"Import an existing project"**

### 4.3 选择 Git 提供商

1. 点击 **"GitHub"** 图标
2. 如果是第一次使用，Netlify 会请求授权

### 4.4 授权 Netlify 访问 GitHub

1. 点击 **"Authorize Netlify"** 按钮
2. GitHub 会跳转到授权页面
3. 选择 **"Only select repositories"**（只选择特定仓库）
4. 找到并选择你刚才创建的 `restaurant-system` 仓库
5. 确认授权（需要你的 GitHub 密码或 Token）

### 4.5 选择仓库

授权成功后，Netlify 会显示你的仓库列表：

1. 找到并点击 **`restaurant-system`** 仓库
2. 点击 **"Import site"**

---

## ⚙️ 第五步：配置构建设置

### 5.1 基本设置

在配置页面，填写：

| 选项 | 填写内容 |
|------|---------|
| **Branch to deploy** | `main`（默认即可） |
| **Build command** | （留空，不填写）⭐ |
| **Publish directory** | `assets` ⭐ 重要！ |

**说明**：
- **Build command**: 我们的项目是静态文件，不需要构建，所以留空
- **Publish directory**: 前端文件都在 `assets` 目录下

### 5.2 高级设置（可选）

如果你需要修改站点名称：

1. 点击 **"Show advanced"** 展开
2. **Site name**: 输入你想要的名称
   - 例如：`restaurant-system`
   - Netlify 会生成 URL：`https://restaurant-system.netlify.app`
   - 或者自定义：`my-restaurant`

### 5.3 环境变量（可选）

如果需要配置 API 地址等环境变量：

1. 点击 **"Advanced"** → **"New variable"**
2. 添加：
   - **Key**: `API_BASE_URL`
   - **Value**: `http://9.128.251.82:8000/api`
3. 点击 **"Save"**

⚠️ **当前系统已自动配置 API 地址，此步骤可以跳过。**

### 5.4 部署站点

点击页面底部的 **"Deploy site"** 绿色按钮

---

## ⏳ 第六步：等待部署完成

### 6.1 查看部署进度

点击 **"Deploy site"** 后，Netlify 会开始部署：

1. 你会看到部署进度条
2. 显示正在执行的操作：
   - "Cloning repository"（克隆仓库）
   - "Installing dependencies"（安装依赖）
   - "Building site"（构建网站）
   - "Deploying site"（部署网站）

### 6.2 等待时间

- 首次部署：通常需要 1-3 分钟
- 后续更新：通常需要 1-2 分钟

### 6.3 部署成功标志

当看到以下标志，说明部署成功：

✅ 绿色的 **"Deployed!"** 标记
✅ 显示部署时间（例如：2s ago）

如果看到红色的 **"Failed!"**，说明部署失败，点击查看错误信息。

---

## 🎉 第七步：访问你的网站

### 7.1 获取网站 URL

部署成功后，Netlify 会显示你的网站地址：

```
https://restaurant-system.netlify.app
```

或者（如果你修改了站点名称）：
```
https://your-site-name.netlify.app
```

### 7.2 访问网站

1. 点击 **"Visit site"** 按钮
2. 或直接复制 URL 到浏览器打开
3. 恭喜！你的网站已经部署成功！

### 7.3 分享链接

现在你可以将这个链接分享给任何人：
- 在手机上访问
- 在平板上访问
- 在任何设备上访问

---

## 🔄 第八步：后续更新（自动部署）

部署成功后，每次你推送代码到 GitHub，Netlify 会自动部署！

### 8.1 修改代码

在本地修改代码后：

```bash
# 1. 查看修改状态
git status

# 2. 添加修改的文件
git add .

# 3. 提交修改（写清楚你改了什么）
git commit -m "feat: 添加XX功能"
# 或
git commit -m "fix: 修复XX问题"

# 4. 推送到 GitHub
git push
```

### 8.2 Netlify 自动部署

推送成功后：
1. Netlify 会自动检测到新的提交
2. 自动触发部署（通常 1-2 分钟）
3. 部署完成后，网站自动更新

### 8.3 查看部署历史

1. 进入 Netlify Dashboard
2. 点击你的站点
3. 点击 **"Deploys"** 标签
4. 可以看到所有的部署记录

### 8.4 回滚到之前的版本

如果新版本有问题，可以快速回滚：

1. 进入 **"Deploys"** 标签
2. 找到要回滚的版本
3. 点击 **"Publish deploy"**

---

## ✅ 第九步：测试网站功能

部署完成后，请在浏览器中测试以下功能：

### 9.1 基础功能测试

- [ ] 打开网站，页面正常显示
- [ ] 点击 "开始点餐" 按钮
- [ ] 选择桌号（例如：8号桌）
- [ ] 浏览菜单

### 9.2 点餐流程测试

- [ ] 添加商品到购物车
- [ ] 修改商品数量
- [ ] 提交订单
- [ ] 查看订单状态

### 9.3 多角色测试

- [ ] 切换到"厨师"角色，查看待制作订单
- [ ] 切换到"传菜员"角色，查看待传菜订单
- [ ] 切换到"收银员"角色，查看待支付订单
- [ ] 切换到"店长"角色，查看营收数据

### 9.4 实时通知测试

- [ ] 打开两个浏览器窗口（不同角色）
- [ ] 顾客提交订单，检查其他角色是否收到通知
- [ ] 查看订单状态是否实时更新

### 9.5 多设备测试

- [ ] 在手机上访问网站
- [ ] 在平板上访问网站
- [ ] 确认在不同设备上都能正常使用

---

## 🎨 第十步：自定义配置（可选）

### 10.1 自定义域名

如果你有自己的域名，可以配置：

1. 进入 Netlify Dashboard
2. 点击 **"Site configuration"**
3. 点击 **"Domain management"**
4. 点击 **"Add custom domain"**
5. 输入你的域名（例如：`restaurant.example.com`）
6. 按照提示配置 DNS

### 10.2 修改站点名称

如果你想修改网站 URL：

1. 进入 **"Site configuration"**
2. 修改 **"Site name"**
3. Netlify 会自动更新 URL

### 10.3 配置 HTTPS（默认已启用）

Netlify 默认提供 HTTPS，无需额外配置。

### 10.4 添加环境变量

如果需要配置敏感信息：

1. 进入 **"Site settings"** → **"Build & deploy"** → **"Environment variables"**
2. 点击 **"Add a variable"**
3. 添加变量
4. 保存并重新部署

---

## 🔍 常见问题

### Q1: 推送时提示 "Authentication failed"？

**原因**：密码错误或 Token 过期

**解决方法**：
1. 重新生成 Personal Access Token
2. 使用 Token 而不是密码
3. 参考 "3.9 认证" 章节

### Q2: 部署失败，显示错误信息？

**解决方法**：
1. 在 Netlify Dashboard 点击 **"Deploys"**
2. 查看最新部署的详细日志
3. 根据错误信息修复代码
4. 重新推送触发部署

### Q3: 部署后页面空白？

**解决方法**：
1. 按 `F12` 打开浏览器控制台
2. 查看 Console 标签的错误信息
3. 查看 Network 标签，检查 API 请求
4. 检查 Publish directory 是否配置为 `assets`

### Q4: API 请求失败，提示 CORS 错误？

**原因**：跨域访问被限制

**解决方法**：
1. 确认后端 API 服务运行正常
2. 检查 API 地址配置
3. 联系开发者在 API 中添加 CORS 配置

### Q5: 推送后 Netlify 没有自动部署？

**解决方法**：
1. 检查是否推送到正确的分支（main）
2. 检查 Netlify 的 GitHub 授权是否有效
3. 在 Netlify Dashboard 手动触发部署
4. 检查 Netlify 的 webhook 设置

### Q6: 如何修改部署分支？

**解决方法**：
1. 进入 Netlify Dashboard
2. 点击 **"Site configuration"**
3. 修改 **"Branch to deploy"**
4. 保存并重新部署

---

## 🎉 完成！

恭喜你！你已经成功通过 GitHub 将项目部署到 Netlify！

现在你可以：
✅ 分享你的网站链接给任何人
✅ 在任何设备上访问
✅ 通过 `git push` 自动更新
✅ 随时回滚到之前的版本
✅ 查看部署历史

---

## 📚 相关文档

- [Netlify 官方文档](https://docs.netlify.com)
- [GitHub 官方文档](https://docs.github.com)
- [项目总体说明](README.md)
- [实时工作流系统指南](WORKFLOW_GUIDE.md)

---

## 💡 提示

- **首次部署**：建议仔细阅读每一步
- **后续更新**：只需 `git push`，自动部署
- **团队协作**：邀请团队成员到 GitHub 仓库
- **版本管理**：定期推送，保持代码同步

---

**祝你使用愉快！🚀**
