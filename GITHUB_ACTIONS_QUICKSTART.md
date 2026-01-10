# GitHub Actions 自动部署 - 快速开始

## 🚀 5 分钟快速配置

### 前置条件

- ✅ 有 GitHub 仓库的访问权限
- ✅ 有服务器的 SSH 访问权限
- ✅ 服务器已安装 systemd

---

## 步骤 1：生成 SSH 密钥（1 分钟）

在**服务器**上执行：

```bash
# 生成 SSH 密钥对
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_key -N ""

# 添加公钥到 authorized_keys
cat ~/.ssh/github_actions_key.pub >> ~/.ssh/authorized_keys

# 设置权限
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

---

## 步骤 2：配置 GitHub Secrets（2 分钟）

1. 进入 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**，添加以下 4 个 Secrets：

### Secret 1: SSH_PRIVATE_KEY

在**服务器**上执行，复制输出内容：

```bash
cat ~/.ssh/github_actions_key
```

粘贴到 GitHub 的 Secret 中。

### Secret 2: SERVER_IP

```
115.191.1.219
```

### Secret 3: SERVER_USER

```
root
```

### Secret 4: PROJECT_PATH

```
/workspace/projects
```

---

## 步骤 3：安装 systemd 服务（1 分钟）

在**服务器**上执行：

```bash
cd /workspace/projects
bash scripts/install_systemd_services.sh
```

等待脚本完成，看到以下输出说明成功：

```
✅ 端口 8000 运行正常
✅ 端口 8001 运行正常
✅ 端口 8004 运行正常
✅ 端口 8006 运行正常
✅ 端口 8007 运行正常
✅ 端口 8008 运行正常
```

---

## 步骤 4：测试自动部署（1 分钟）

在**本地电脑**执行：

```bash
# 拉取最新代码
git pull origin main

# 创建测试提交
git commit --allow-empty -m "test: 测试 GitHub Actions 自动部署"

# 推送到 GitHub（触发自动部署）
git push origin main
```

然后在 GitHub 仓库查看 **Actions** 标签页，应该看到工作流正在运行。

---

## ✅ 验证部署成功

### 方式 1：查看 GitHub Actions

1. 进入 GitHub 仓库
2. 点击 **Actions** 标签页
3. 查看最新的工作流运行记录
4. 应该看到绿色的 ✅ 标记

### 方式 2：查看服务状态

在**服务器**上执行：

```bash
# 查看服务状态
systemctl status restaurant-api

# 检查端口
lsof -i :8000,8001,8004,8006,8007,8008
```

### 方式 3：测试 API

在浏览器或使用 curl 测试：

```bash
curl http://115.191.1.219:8000/api/health
```

应该返回类似：

```json
{"status": "healthy"}
```

---

## 🎉 完成！

现在你推送代码到 GitHub，就会自动部署到服务器了！

### 日常使用

```bash
# 1. 修改代码
vim src/api/restaurant_api.py

# 2. 提交并推送（自动触发部署）
git add .
git commit -m "feat: 添加新功能"
git push origin main
```

就这么简单！🚀

---

## 📝 常见问题

### Q1: GitHub Actions 报错 "Permission denied"

**A**: 检查 SSH_PRIVATE_KEY 是否正确复制，确保包含完整的 BEGIN/END 行。

### Q2: 服务启动失败

**A**: 在服务器上执行：
```bash
systemctl status restaurant-api
journalctl -u restaurant-api -n 50
```

### Q3: 如何手动部署？

**A**: 在服务器上执行：
```bash
cd /workspace/projects
bash scripts/auto_deploy.sh
```

---

## 🔗 相关链接

- [详细文档](./GITHUB_ACTIONS_DEPLOYMENT.md)
- [故障排查](./TROUBLESHOOTING_GUIDE.md)
- [系统架构](./COMMERCIAL_DEPLOYMENT.md)

---

**快速配置完成时间**: 约 5 分钟
