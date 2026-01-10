# 从沙盒到 Netlify - 快速命令清单

复制粘贴执行，15分钟完成配置！

---

## 📋 准备工作

- ✅ GitHub 账号
- ✅ Netlify 账号
- ✅ 服务器访问权限（115.191.1.219）

---

## 🚀 步骤 1：沙盒 Git 配置（1分钟）

在沙盒终端执行：

```bash
# 配置 Git 用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 验证配置
git config --global --list
```

---

## 🔗 步骤 2：创建 GitHub 仓库（2分钟）

1. 打开 https://github.com/new
2. 填写：
   - Repository name: `restaurant-system`
   - Public 或 Private
   - **不要**勾选任何选项
3. 点击 **Create repository**

---

## 📤 步骤 3：推送到 GitHub（3分钟）

在沙盒终端执行：

```bash
# 进入项目目录
cd /workspace/projects

# 初始化 Git
git init

# 添加所有文件
git add .

# 首次提交
git commit -m "feat: 初始化餐饮点餐系统"

# 连接到 GitHub（替换为你的实际信息）
git remote add origin https://github.com/<你的用户名>/restaurant-system.git

# 设置主分支
git branch -M main

# 推送到 GitHub
git push -u origin main
```

**如果提示输入密码**：
- 用户名：GitHub 用户名
- 密码：使用 Personal Access Token（不是 GitHub 密码）

**创建 Personal Access Token**：
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → 勾选 `repo` 和 `workflow`
3. 复制 token（只显示一次！）

---

## ⚙️ 步骤 4：配置 GitHub Secrets（3分钟）

### 4.1 在服务器上生成 SSH 密钥

在服务器（115.191.1.219）执行：

```bash
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions -N ""
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
cat ~/.ssh/github_actions
```
**复制上面的私钥输出**

### 4.2 在 GitHub 配置 Secrets

访问：`https://github.com/<你的用户名>/<仓库名>/settings/secrets/actions`

添加 3 个 Secrets：

| Name | Value |
|------|-------|
| `SSH_PRIVATE_KEY` | 粘贴步骤 4.1 的私钥 |
| `SERVER_USER` | `root` |
| `SERVER_HOST` | `115.191.1.219` |

---

## 🚀 步骤 5：测试 GitHub Actions（2分钟）

在沙盒终端执行：

```bash
# 修改一个文件测试
echo "# 测试 GitHub Actions" >> README.md

# 提交并推送
git add .
git commit -m "test: 测试 GitHub Actions 自动部署"
git push origin main
```

然后在 GitHub 查看 Actions 执行：
1. 打开 GitHub 仓库
2. 点击 **Actions** 标签
3. 等待工作流完成（绿色 ✅）

---

## 🌐 步骤 6：配置 Netlify（2分钟）

### 6.1 连接 Netlify 到 GitHub

1. 打开 https://app.netlify.com/
2. 点击 **Add new site** → **Import an existing project**
3. 选择 **GitHub**
4. 授权并选择你的仓库
5. 配置：
   - Build command: 留空
   - Publish directory: `.`
   - Branch: `main`
6. 点击 **Deploy site**

**注意**：如果你已经使用拖拽部署到 Netlify，可以跳过此步骤。

---

## ✅ 步骤 7：验证部署（2分钟）

### 7.1 验证后端 API

在浏览器访问：

```
http://115.191.1.219:8000/api/health
```

应该看到健康检查信息。

### 7.2 验证前端

在浏览器访问：

```
https://mellow-rabanadas-877f3e.netlify.app/
```

应该能看到餐饮系统前端页面。

---

## 🔄 日常开发流程

以后每次开发，只需要：

```bash
# 1. 拉取最新代码（可选）
git pull origin main

# 2. 开发和测试
# 编辑文件...

# 3. 提交并推送
git add .
git commit -m "feat: 描述你的更改"
git push origin main

# 4. 等待自动部署（2-5分钟）
# - GitHub Actions 自动部署后端
# - Netlify 自动部署前端
```

就这么简单！✨

---

## 📊 部署流程图

```
沙盒开发
  ↓ git push
GitHub 仓库
  ├─→ GitHub Actions → 服务器 115.191.1.219（后端）
  └─→ Netlify → mellow-rabanadas-877f3e.netlify.app（前端）
```

---

## ❓ 常见问题

### Q: Git 推送失败
**解决**: 使用 Personal Access Token 代替密码

### Q: GitHub Actions 失败
**解决**: 检查 GitHub Secrets 配置是否正确

### Q: Netlify 前端无数据
**解决**: 检查后端服务是否运行：`systemctl status restaurant-api`

---

## 📚 详细文档

- [完整详细指南](SANDBOX_TO_NETLIFY_GUIDE.md) - 每一步都有详细说明
- [GitHub Actions 教程](GITHUB_ACTIONS_STEP_BY_STEP.md)
- [Netlify 部署指南](NETLIFY_DEPLOYMENT.md)

---

## 🎉 完成！

现在你有了完整的开发流程：

✅ 沙盒开发 → GitHub → 自动部署（后端+前端）

推送代码就自动部署！🚀
