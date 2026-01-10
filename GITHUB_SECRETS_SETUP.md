# GitHub Secrets 配置指南

本文档指导如何在 GitHub 仓库中配置必要的 Secrets，以启用 GitHub Actions 自动部署功能。

## 📋 需要配置的 Secrets

### 1. SSH_PRIVATE_KEY
服务器的 SSH 私钥，用于 GitHub Actions 连接到服务器。

**生成 SSH 密钥对：**
```bash
# 在服务器上生成 SSH 密钥对
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions
```

**配置 SSH 公钥到服务器：**
```bash
# 将公钥添加到服务器的 authorized_keys
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**配置到 GitHub：**
- 复制私钥内容：`cat ~/.ssh/github_actions`
- 去到 GitHub 仓库 -> Settings -> Secrets and variables -> Actions
- 点击 "New repository secret"
- Name: `SSH_PRIVATE_KEY`
- Secret: 粘贴私钥的完整内容（包括 `-----BEGIN RSA PRIVATE KEY-----` 和 `-----END RSA PRIVATE KEY-----`）

### 2. SERVER_USER
连接服务器使用的用户名。

**配置到 GitHub：**
- Name: `SERVER_USER`
- Secret: `root` 或其他有权限的用户名

### 3. SERVER_HOST
服务器的 IP 地址或域名。

**配置到 GitHub：**
- Name: `SERVER_HOST`
- Secret: `115.191.1.219`（你的服务器 IP）

## 🔧 完整配置步骤

### 步骤 1: 在服务器上生成 SSH 密钥
```bash
# 1. 生成密钥对
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions -N ""

# 2. 配置公钥
mkdir -p ~/.ssh
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/github_actions

# 3. 验证 SSH 配置（在本地测试）
ssh -i ~/.ssh/github_actions root@115.191.1.219 "echo 'SSH 连接成功'"
```

### 步骤 2: 在 GitHub 仓库中配置 Secrets

1. 打开你的 GitHub 仓库
2. 点击 **Settings** 标签
3. 在左侧菜单中找到 **Secrets and variables** -> **Actions**
4. 点击 **New repository secret** 按钮
5. 按照上面的配置添加以下 Secrets：

| Name | Value | 说明 |
|------|-------|------|
| `SSH_PRIVATE_KEY` | 服务器的 SSH 私钥 | 从 `~/.ssh/github_actions` 复制 |
| `SERVER_USER` | `root` 或其他用户 | SSH 登录用户名 |
| `SERVER_HOST` | `115.191.1.219` | 服务器 IP 地址 |

### 步骤 3: 验证配置

1. 确保服务器上的代码仓库已初始化
2. 确保服务器上已安装必要的依赖（Python 3, git, 等）
3. 提交代码到 GitHub 的 main 分支
4. 观察GitHub Actions 的执行情况

## 🔍 故障排查

### 问题 1: SSH 连接失败
**错误信息：** `Permission denied (publickey)`

**解决方案：**
- 检查 SSH 私钥是否正确复制（包括完整的 BEGIN 和 END 标记）
- 检查服务器的 authorized_keys 是否包含对应的公钥
- 确认用户名和 IP 地址是否正确

### 问题 2: 部署脚本执行失败
**错误信息：** `bash: scripts/auto_deploy.sh: No such file or directory`

**解决方案：**
- 确保服务器上的代码仓库结构正确
- 确保 `scripts/auto_deploy.sh` 文件有执行权限
- 在服务器上运行：`chmod +x scripts/auto_deploy.sh`

### 问题 3: 服务启动失败
**错误信息：** `Port 8000 already in use`

**解决方案：**
- 检查是否有其他进程占用了端口
- 在服务器上运行：`lsof -i :8000` 查看端口占用情况
- 停止占用端口的进程：`kill -9 <PID>`

## 📝 安全建议

1. **定期轮换 SSH 密钥**：建议每 3-6 个月更换一次 SSH 密钥
2. **限制 IP 访问**：在服务器的防火墙中配置规则，只允许 GitHub Actions 的 IP 访问
3. **使用专用部署用户**：创建一个专门的部署用户，而不是使用 root
4. **监控部署日志**：定期检查 GitHub Actions 的执行日志，确保没有异常

## 🚀 快速配置命令

在服务器上执行以下命令，快速完成配置：

```bash
#!/bin/bash
# 快速配置 GitHub Actions SSH 访问

# 1. 生成 SSH 密钥对
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions -N ""

# 2. 配置公钥
mkdir -p ~/.ssh
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/github_actions

# 3. 显示私钥（复制到 GitHub）
echo "========================================="
echo "复制以下私钥到 GitHub -> SSH_PRIVATE_KEY"
echo "========================================="
cat ~/.ssh/github_actions
echo "========================================="

# 4. 显示公钥（用于验证）
echo "公钥（已添加到 authorized_keys）:"
echo "========================================="
cat ~/.ssh/github_actions.pub
echo "========================================="

# 5. 测试 SSH 连接
echo "测试 SSH 连接..."
ssh -i ~/.ssh/github_actions localhost "echo '✅ SSH 配置成功！'"
```

## 📚 相关文档

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [GitHub Secrets 文档](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [SSH 密钥管理](https://www.ssh.com/academy/ssh/key)

---

**配置完成后，当你推送代码到 main 分支时，GitHub Actions 将自动触发部署流程。**
