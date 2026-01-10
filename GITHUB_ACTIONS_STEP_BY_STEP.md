# GitHub Actions 自动部署 - 超简单一步一步指南

跟着这个文档操作，10分钟内完成配置！

---

## 📋 准备工作

你只需要：
- ✅ 能登录到你的服务器（115.191.1.219）
- ✅ 有一个 GitHub 仓库
- ✅ 能运行 git 命令

---

## 步骤 1：在服务器上生成 SSH 密钥（3分钟）

**在服务器上执行以下命令**（登录到 115.191.1.219）：

```bash
# 1. 生成 SSH 密钥
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions -N ""

# 2. 配置公钥
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys

# 3. 显示私钥（复制下面的内容）
echo "========================================="
echo "复制下面的私钥（从 -----BEGIN 到 -----END）："
echo "========================================="
cat ~/.ssh/github_actions
echo "========================================="
```

**验证是否成功**：
```bash
# 测试 SSH 连接
ssh -i ~/.ssh/github_actions localhost "echo 'SSH 配置成功！'"
```

如果看到 "SSH 配置成功！"，说明成功了！✅

---

## 步骤 2：在 GitHub 上配置 Secrets（3分钟）

### 2.1 打开 GitHub 仓库页面

在浏览器中打开你的 GitHub 仓库。

### 2.2 进入 Settings

点击仓库顶部的 **Settings** 标签。

### 2.3 进入 Secrets 配置

1. 在左侧菜单中找到 **Secrets and variables**
2. 点击 **Actions**
3. 点击右侧的 **New repository secret** 按钮

### 2.4 添加第一个 Secret：SSH_PRIVATE_KEY

- **Name**: 输入 `SSH_PRIVATE_KEY`（必须完全一致）
- **Secret**: 粘贴步骤 1 中显示的私钥
  - 注意：必须包含从 `-----BEGIN RSA PRIVATE KEY-----` 到 `-----END RSA PRIVATE KEY-----` 的所有内容
- 点击 **Add secret**

### 2.5 添加第二个 Secret：SERVER_USER

- **Name**: 输入 `SERVER_USER`
- **Secret**: 输入 `root`（或者你 SSH 登录使用的用户名）
- 点击 **Add secret**

### 2.6 添加第三个 Secret：SERVER_HOST

- **Name**: 输入 `SERVER_HOST`
- **Secret**: 输入 `115.191.1.219`（你的服务器 IP）
- 点击 **Add secret**

**验证是否成功**：
- 在 Secrets 页面应该能看到这 3 个 Secrets：
  - ✅ SSH_PRIVATE_KEY
  - ✅ SERVER_USER
  - ✅ SERVER_HOST

---

## 步骤 3：初始化服务器环境（3分钟）

**在服务器上执行以下命令**：

```bash
# 1. 进入项目目录
cd /workspace/projects

# 2. 确保代码仓库已克隆
# 如果还没有代码仓库，先克隆：
# git clone <你的GitHub仓库地址> /workspace/projects
# cd /workspace/projects

# 3. 创建虚拟环境（如果还没有）
python3 -m venv venv
source venv/bin/activate

# 4. 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 5. 检查项目结构
ls -la

# 应该能看到：
# - .github/workflows/deploy.yml
# - scripts/auto_deploy.sh
# - systemd/ 目录
# - src/api/ 目录
```

**验证是否成功**：
```bash
# 检查工作流文件
ls -l .github/workflows/deploy.yml
# 应该显示文件存在

# 检查部署脚本
ls -l scripts/auto_deploy.sh
# 应该显示文件存在
```

---

## 步骤 4：首次启动服务（1分钟）

**在服务器上执行以下命令**：

```bash
cd /workspace/projects

# 运行自动部署脚本
bash scripts/auto_deploy.sh
```

**验证是否成功**：
```bash
# 检查服务是否运行
for port in 8000 8001 8004 8006 8007 8008; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "✅ 端口 $port 运行正常"
    else
        echo "❌ 端口 $port 未运行"
    fi
done

# 应该看到所有端口都是 ✅
```

---

## 步骤 5：测试 GitHub Actions 自动部署（2分钟）

### 5.1 提交代码到 GitHub

**在你的本地电脑上执行**：

```bash
# 1. 添加所有文件
git add .

# 2. 提交更改
git commit -m "feat: 配置 GitHub Actions 自动部署"

# 3. 推送到 GitHub
git push origin main
```

### 5.2 观察 GitHub Actions 执行

1. 打开你的 GitHub 仓库
2. 点击顶部的 **Actions** 标签
3. 你会看到一个工作流正在运行（黄色圆点 ⏳）
4. 等待几分钟，工作流会变成绿色 ✅

### 5.3 查看部署日志

点击工作流名称（如 "Auto Deploy to Server"），然后点击具体的运行记录，可以查看：
- 每个步骤的执行情况
- 详细的日志输出
- 是否有错误信息

**验证是否成功**：
- GitHub Actions 页面显示绿色 ✅
- 服务器上的服务已更新并运行

---

## 步骤 6：验证自动部署（1分钟）

### 6.1 检查服务器服务

**在服务器上执行**：

```bash
# 检查服务状态
systemctl status restaurant-api

# 或使用验证脚本
bash scripts/verify_github_actions.sh
```

### 6.2 访问 API 服务

在浏览器中打开：

```
http://115.191.1.219:8000/api/health
```

如果能看到健康检查信息，说明部署成功！✅

---

## 🎉 完成！

现在你已经配置好了 GitHub Actions 自动部署！

### 以后如何使用？

**超级简单**，每次推送代码就自动部署：

```bash
git add .
git commit -m "添加新功能"
git push origin main
# 推送后自动部署 ✨
```

### 如何手动触发部署？

1. 打开 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 **"🚀 Auto Deploy to Server"**
4. 点击 **"Run workflow"** 按钮
5. 点击 **"Run workflow"** 确认

---

## ❓ 遇到问题？

### 问题 1：SSH 连接失败

**错误信息**：`Permission denied (publickey)`

**解决方法**：
- 确认私钥复制完整（包括 BEGIN 和 END 行）
- 在服务器上测试：`ssh -i ~/.ssh/github_actions localhost "echo 'test'"`

### 问题 2：部署脚本找不到

**错误信息**：`bash: scripts/auto_deploy.sh: No such file or directory`

**解决方法**：
- 在服务器上检查：`ls -la scripts/auto_deploy.sh`
- 如果文件不存在，从 GitHub 重新拉取代码：`git pull`

### 问题 3：服务启动失败

**错误信息**：`Port 8000 already in use`

**解决方法**：
```bash
# 查找占用端口的进程
lsof -i :8000

# 停止进程
pkill -f "uvicorn.*8000"

# 重新启动
bash scripts/auto_deploy.sh
```

### 问题 4：依赖安装失败

**错误信息**：`Module not found`

**解决方法**：
```bash
cd /workspace/projects
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📞 需要帮助？

查看详细文档：
- [GitHub Secrets 详细配置](GITHUB_SECRETS_SETUP.md)
- [GitHub Actions 使用指南](GITHUB_ACTIONS_USAGE.md)
- [故障排查指南](TROUBLESHOOTING.md)

---

**祝你使用愉快！** 🚀
