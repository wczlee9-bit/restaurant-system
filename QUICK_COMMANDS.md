# GitHub Actions 自动部署 - 快速命令清单

直接复制粘贴执行！

---

## 🚀 服务器端配置（在 115.191.1.219 上执行）

### 1. 生成 SSH 密钥
```bash
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions -N ""
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
cat ~/.ssh/github_actions
```
**复制上面的私钥输出（从 -----BEGIN 到 -----END），保存到记事本**

### 2. 测试 SSH
```bash
ssh -i ~/.ssh/github_actions localhost "echo 'SSH 配置成功！'"
```

### 3. 初始化环境
```bash
cd /workspace/projects
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 首次启动
```bash
cd /workspace/projects
bash scripts/auto_deploy.sh
```

### 5. 验证服务
```bash
for port in 8000 8001 8004 8006 8007 8008; do
    lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 && echo "✅ $port" || echo "❌ $port"
done
```

---

## 🔧 GitHub 网页配置

访问：`https://github.com/<你的用户名>/<你的仓库名>/settings/secrets/actions`

添加 3 个 Secrets：

| Name | Value |
|------|-------|
| `SSH_PRIVATE_KEY` | 粘贴步骤 1 中复制的私钥 |
| `SERVER_USER` | `root` |
| `SERVER_HOST` | `115.191.1.219` |

---

## 💻 本地电脑操作

### 1. 提交代码并推送
```bash
git add .
git commit -m "feat: 配置 GitHub Actions 自动部署"
git push origin main
```

### 2. 观察 GitHub Actions
访问：`https://github.com/<你的用户名>/<你的仓库名>/actions`

等待工作流执行完成（变绿 ✅）

---

## ✅ 验证部署

### 在服务器上
```bash
bash scripts/verify_github_actions.sh
```

### 在浏览器中
访问：`http://115.191.1.219:8000/api/health`

---

## 🎉 完成！

以后每次推送代码就自动部署：

```bash
git add .
git commit -m "更新功能"
git push origin main
```

就这么简单！✨
