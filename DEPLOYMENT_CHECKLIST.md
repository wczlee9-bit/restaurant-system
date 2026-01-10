# 部署配置检查清单

按照这个清单，逐步完成所有配置，确保部署成功！

---

## ✅ 第一部分：沙盒环境配置

- [ ] 1.1 Git 已安装（运行 `git --version`）
- [ ] 1.2 Git 用户信息已配置
  ```bash
  git config --global user.name "Your Name"
  git config --global user.email "your.email@example.com"
  ```
- [ ] 1.3 Git 仓库已初始化
  ```bash
  cd /workspace/projects
  git init
  ```
- [ ] 1.4 代码已提交到 Git
  ```bash
  git add .
  git commit -m "feat: 初始化项目"
  ```

---

## ✅ 第二部分：GitHub 仓库配置

- [ ] 2.1 GitHub 仓库已创建（访问 https://github.com/new）
- [ ] 2.2 远程仓库已连接
  ```bash
  git remote add origin https://github.com/<用户名>/<仓库名>.git
  ```
- [ ] 2.3 Personal Access Token 已创建
  - 勾选 `repo` 和 `workflow` 权限
  - Token 已保存（只显示一次）
- [ ] 2.4 代码已推送到 GitHub
  ```bash
  git branch -M main
  git push -u origin main
  ```
- [ ] 2.5 在 GitHub 仓库页面能查看到代码

---

## ✅ 第三部分：GitHub Actions 配置

### 服务器端配置

- [ ] 3.1 SSH 密钥对已生成（在服务器 115.191.1.219 上）
  ```bash
  ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions -N ""
  ```
- [ ] 3.2 SSH 公钥已添加到 authorized_keys
  ```bash
  cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
  ```
- [ ] 3.3 SSH 连接测试成功
  ```bash
  ssh -i ~/.ssh/github_actions localhost "echo 'SSH 配置成功！'"
  ```

### GitHub 端配置

- [ ] 3.4 访问 GitHub Secrets 页面
  - URL: `https://github.com/<用户名>/<仓库名>/settings/secrets/actions`
- [ ] 3.5 SSH_PRIVATE_KEY 已配置
  - Name: `SSH_PRIVATE_KEY`
  - Value: 服务器的 SSH 私钥（包含 BEGIN 和 END 行）
- [ ] 3.6 SERVER_USER 已配置
  - Name: `SERVER_USER`
  - Value: `root`
- [ ] 3.7 SERVER_HOST 已配置
  - Name: `SERVER_HOST`
  - Value: `115.191.1.219`
- [ ] 3.8 GitHub Actions 工作流文件存在
  - 文件：`.github/workflows/deploy.yml`

### GitHub Actions 测试

- [ ] 3.9 推送测试代码触发 GitHub Actions
  ```bash
  git add .
  git commit -m "test: 测试 GitHub Actions"
  git push origin main
  ```
- [ ] 3.10 在 GitHub Actions 页面能看到工作流运行
  - URL: `https://github.com/<用户名>/<仓库名>/actions`
- [ ] 3.11 工作流执行成功（绿色 ✅）

---

## ✅ 第四部分：服务器环境配置

- [ ] 4.1 代码仓库已在服务器上克隆
  ```bash
  cd /workspace/projects
  git clone <GitHub 仓库地址> .
  ```
- [ ] 4.2 Python 虚拟环境已创建
  ```bash
  python3 -m venv venv
  ```
- [ ] 4.3 Python 依赖已安装
  ```bash
  source venv/bin/activate
  pip install -r requirements.txt
  ```
- [ ] 4.4 部署脚本有执行权限
  ```bash
  chmod +x scripts/auto_deploy.sh
  ```
- [ ] 4.5 首次启动服务成功
  ```bash
  bash scripts/auto_deploy.sh
  ```

---

## ✅ 第五部分：服务器服务验证

- [ ] 5.1 餐厅 API 服务运行正常（端口 8000）
  ```bash
  lsof -i :8000
  ```
- [ ] 5.2 增强 API 服务运行正常（端口 8007）
- [ ] 5.3 会员 API 服务运行正常（端口 8001）
- [ ] 5.4 总公司 API 服务运行正常（端口 8004）
- [ ] 5.5 结算 API 服务运行正常（端口 8006）
- [ ] 5.6 WebSocket API 服务运行正常（端口 8008）
- [ ] 5.7 后端 API 健康检查正常
  - 访问：`http://115.191.1.219:8000/api/health`

---

## ✅ 第六部分：Netlify 配置

- [ ] 6.1 Netlify 账号已注册（访问 https://app.netlify.com/）
- [ ] 6.2 Netlify 已连接到 GitHub 仓库
- [ ] 6.3 Netlify 配置文件存在
  - `netlify.toml`
  - `netlify-production.toml`
- [ ] 6.4 首次部署成功
- [ ] 6.5 Netlify 站点可访问
  - URL: `https://mellow-rabanadas-877f3e.netlify.app/`

---

## ✅ 第七部分：前端验证

- [ ] 7.1 Netlify 前端页面可正常访问
- [ ] 7.2 前端能正常加载
- [ ] 7.3 前端能连接到后端 API
- [ ] 7.4 点餐功能正常
- [ ] 7.5 菜品数据正常显示
- [ ] 7.6 订单提交功能正常

---

## ✅ 第八部分：完整流程验证

### 测试完整流程

- [ ] 8.1 在沙盒修改代码
- [ ] 8.2 提交代码到 Git
  ```bash
  git add .
  git commit -m "test: 测试完整部署流程"
  ```
- [ ] 8.3 推送到 GitHub
  ```bash
  git push origin main
  ```
- [ ] 8.4 GitHub Actions 执行成功（绿色 ✅）
- [ ] 8.5 Netlify 自动部署成功
- [ ] 8.6 后端服务已更新
- [ ] 8.7 前端页面已更新
- [ ] 8.8 功能验证正常

---

## 📊 配置完成统计

### 第一部分：沙盒环境配置
- 完成项目：`[ ] / [ ]`

### 第二部分：GitHub 仓库配置
- 完成项目：`[ ] / [ ]`

### 第三部分：GitHub Actions 配置
- 完成项目：`[ ] / [ ]`

### 第四部分：服务器环境配置
- 完成项目：`[ ] / [ ]`

### 第五部分：服务器服务验证
- 完成项目：`[ ] / [ ]`

### 第六部分：Netlify 配置
- 完成项目：`[ ] / [ ]`

### 第七部分：前端验证
- 完成项目：`[ ] / [ ]`

### 第八部分：完整流程验证
- 完成项目：`[ ] / [ ]`

---

## 🎯 完成条件

**当所有项目都打勾 ✅ 时，说明配置完成！**

### 配置完成后，日常开发流程如下：

```bash
# 1. 在沙盒开发
# 编辑文件...

# 2. 提交代码
git add .
git commit -m "feat: 添加新功能"

# 3. 推送到 GitHub
git push origin main

# 4. 等待自动部署（2-5分钟）
# - GitHub Actions 自动部署后端到服务器
# - Netlify 自动部署前端
```

就这么简单！✨

---

## 📚 相关文档

- [从沙盒到 Netlify 完整指南](SANDBOX_TO_NETLIFY_GUIDE.md)
- [快速命令清单](QUICK_START_SANDBOX_TO_NETLIFY.md)
- [GitHub Actions 详细教程](GITHUB_ACTIONS_STEP_BY_STEP.md)
- [GitHub Secrets 配置指南](GITHUB_SECRETS_SETUP.md)

---

**祝你配置顺利！** 🚀
