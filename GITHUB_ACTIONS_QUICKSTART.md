# GitHub Actions 快速配置指南

本指南帮助你在 10 分钟内完成 GitHub Actions 自动部署的配置。

## 🚀 快速开始

### 前置条件

- ✅ 服务器 IP: `115.191.1.219`
- ✅ 服务器用户: `root`
- ✅ 服务器上已安装 Python 3.8+ 和 Git
- ✅ GitHub 仓库已创建并关联本地代码

### 步骤 1: 配置 SSH 密钥（5 分钟）

在服务器上执行以下命令：

```bash
# 1. 生成 SSH 密钥对
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions -N ""

# 2. 配置公钥
mkdir -p ~/.ssh
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 3. 显示私钥（复制到 GitHub）
echo "复制以下私钥内容："
echo "========================================="
cat ~/.ssh/github_actions
echo "========================================="
```

### 步骤 2: 在 GitHub 配置 Secrets（3 分钟）

1. 打开 GitHub 仓库
2. 进入 **Settings** -> **Secrets and variables** -> **Actions**
3. 点击 **New repository secret**，添加以下 3 个 Secrets：

| Name | Value |
|------|-------|
| `SSH_PRIVATE_KEY` | 复制上一步显示的私钥（包括 BEGIN 和 END 行） |
| `SERVER_USER` | `root` |
| `SERVER_HOST` | `115.191.1.219` |

### 步骤 3: 初始化服务器环境（2 分钟）

在服务器上执行：

```bash
# 1. 克隆代码仓库（如果还没有）
git clone <你的仓库地址> /workspace/projects
cd /workspace/projects

# 2. 创建虚拟环境并安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env  # 如果存在
vi .env  # 根据实际情况修改配置

# 4. 首次启动服务
bash scripts/auto_deploy.sh
```

### 步骤 4: 测试自动部署（1 分钟）

在本地电脑上执行：

```bash
# 提交并推送代码
git add .
git commit -m "feat: 配置 GitHub Actions 自动部署"
git push origin main
```

然后：
1. 打开 GitHub 仓库
2. 点击 **Actions** 标签
3. 观察部署工作流的执行情况

## ✅ 验证部署成功

部署成功后，你可以：

1. **在 GitHub Actions 页面**：看到绿色 ✅ 标记
2. **在服务器上**：运行以下命令检查服务状态
   ```bash
   bash scripts/verify_github_actions.sh
   ```
3. **访问服务**：在浏览器访问 `http://115.191.1.219:8000/api/health`

## 📋 常见问题

### Q1: 部署失败，提示 SSH 连接错误

**原因**: GitHub Secrets 配置错误

**解决**:
1. 确认私钥复制完整（包括 BEGIN 和 END 行）
2. 在服务器上测试 SSH 连接：
   ```bash
   ssh -i ~/.ssh/github_actions root@115.191.1.219 "echo 'SSH 连接成功'"
   ```

### Q2: 部署成功但服务未启动

**原因**: 端口被占用或依赖未安装

**解决**:
```bash
# 检查端口占用
lsof -i :8000

# 停止占用端口的进程
pkill -f "uvicorn.*8000"

# 查看服务日志
tail -f /workspace/projects/logs/api.log
```

### Q3: 如何手动触发部署？

**方法**:
1. 打开 GitHub 仓库
2. 进入 **Actions** 标签
3. 选择 **"🚀 Auto Deploy to Server"** 工作流
4. 点击 **"Run workflow"** 按钮

### Q4: 如何回滚到上一个版本？

**方法**:
```bash
# 在服务器上
cd /workspace/projects
git log --oneline -5  # 查看最近 5 次提交
git reset --hard <上一个版本的提交号>
bash scripts/auto_deploy.sh
```

## 📚 更多文档

- [GitHub Secrets 详细配置](GITHUB_SECRETS_SETUP.md)
- [GitHub Actions 使用指南](GITHUB_ACTIONS_USAGE.md)
- [故障排查](TROUBLESHOOTING.md)

## 🎉 完成！

配置完成后，以后每次推送代码到 `main` 分支，GitHub Actions 都会自动部署到服务器。

祝你使用愉快！🚀
