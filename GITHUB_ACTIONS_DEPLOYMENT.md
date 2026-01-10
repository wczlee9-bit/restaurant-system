# GitHub Actions 自动部署指南

本文档说明如何使用 GitHub Actions 实现代码推送到 GitHub 后自动部署到服务器。

## 📋 目录

1. [架构说明](#架构说明)
2. [配置步骤](#配置步骤)
3. [使用方法](#使用方法)
4. [故障排查](#故障排查)

## 🏗️ 架构说明

### 部署架构

```
GitHub 仓库
    │
    │ 1. 推送代码 (git push)
    │
    ▼
GitHub Actions
    │
    │ 2. 触发工作流
    │
    ▼
服务器 (115.191.1.219)
    │
    ├─ 前端: Netlify (静态资源托管)
    │   └─ mellow-rabanadas-877f3e.netlify.app
    │
    └─ 后端: systemd 服务
        ├─ 端口 8000: 餐厅主 API
        ├─ 端口 8007: 增强 API
        ├─ 端口 8001: 会员 API
        ├─ 端口 8004: 总公司 API
        ├─ 端口 8006: 结算 API
        └─ 端口 8008: WebSocket API
```

### 自动化流程

1. **代码推送** → 推送到 GitHub 的 main/master/develop 分支
2. **触发工作流** → GitHub Actions 自动检测推送事件
3. **连接服务器** → 使用 SSH 连接到生产服务器
4. **拉取代码** → 在服务器上执行 `git pull`
5. **更新依赖** → 安装/更新 Python 依赖
6. **重启服务** → 重启所有 API 服务
7. **验证状态** → 检查服务运行状态

## ⚙️ 配置步骤

### 第一步：生成 SSH 密钥对

在**本地电脑**或**服务器**上执行：

```bash
# 生成 SSH 密钥对
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_key
```

这会生成两个文件：
- `github_actions_key` (私钥)
- `github_actions_key.pub` (公钥)

### 第二步：配置服务器 SSH

在**服务器**上执行：

```bash
# 将公钥添加到服务器的 authorized_keys
cat ~/.ssh/github_actions_key.pub >> ~/.ssh/authorized_keys

# 确保权限正确
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### 第三步：配置 GitHub Secrets

在你的 GitHub 仓库中配置 Secrets：

1. 进入仓库的 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret** 添加以下密钥：

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `SSH_PRIVATE_KEY` | SSH 私钥内容 | 整个私钥文件的内容（包括 BEGIN/END 行） |
| `SERVER_IP` | 服务器 IP 地址 | `115.191.1.219` |
| `SERVER_USER` | 服务器用户名 | `root` |
| `PROJECT_PATH` | 项目路径（可选） | `/workspace/projects` |

**获取私钥内容**：
```bash
# 在本地电脑或服务器上执行
cat ~/.ssh/github_actions_key
```
复制输出内容（包括 `-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----` 行），粘贴到 GitHub 的 Secret 中。

### 第四步：安装 systemd 服务（首次部署）

在**服务器**上执行：

```bash
cd /workspace/projects
sudo bash scripts/install_systemd_services.sh
```

这会：
- 复制 systemd 服务配置文件到 `/etc/systemd/system/`
- 启用并启动所有 API 服务
- 配置开机自启动

**验证服务状态**：
```bash
# 查看所有服务状态
systemctl status restaurant-api
systemctl status restaurant-enhanced-api
systemctl status member-api
systemctl status headquarters-api
systemctl status settlement-api
systemctl status websocket-api

# 查看所有端口
lsof -i :8000,8001,8004,8006,8007,8008
```

## 🚀 使用方法

### 方式一：自动部署（推荐）

推送代码到 GitHub，自动触发部署：

```bash
# 推送到 main 分支（自动触发部署）
git add .
git commit -m "feat: 更新功能"
git push origin main
```

**触发条件**：
- 推送到 `main` 分支
- 推送到 `master` 分支
- 推送到 `develop` 分支

### 方式二：手动触发

在 GitHub 仓库中：
1. 进入 **Actions** 标签页
2. 选择 **Deploy to Server** 工作流
3. 点击 **Run workflow** → **Run workflow** 按钮

### 方式三：服务器上手动部署

在**服务器**上执行：

```bash
cd /workspace/projects
bash scripts/auto_deploy.sh
```

## 🔍 故障排查

### 问题 1：GitHub Actions 失败 - SSH 连接超时

**错误信息**：
```
ssh: connect to host xxx.xxx.xxx.xxx port 22: Connection timed out
```

**解决方案**：
1. 检查服务器防火墙是否开放 22 端口
2. 检查 GitHub Secrets 中的 `SERVER_IP` 是否正确
3. 尝试在本地电脑手动连接：
   ```bash
   ssh root@115.191.1.219
   ```

### 问题 2：GitHub Actions 失败 - 权限被拒绝

**错误信息**：
```
Permission denied (publickey)
```

**解决方案**：
1. 检查私钥是否正确复制到 GitHub Secrets
2. 确保私钥包含完整的 `BEGIN/END` 行
3. 检查服务器 `authorized_keys` 文件权限：
   ```bash
   chmod 600 ~/.ssh/authorized_keys
   chmod 700 ~/.ssh
   ```

### 问题 3：服务启动失败

**错误信息**：
```
❌ 端口 8000 启动失败
```

**解决方案**：

1. 查看服务日志：
   ```bash
   # systemd 日志
   journalctl -u restaurant-api -f
   
   # 应用日志
   tail -f logs/api.log
   tail -f logs/api.error.log
   ```

2. 手动重启服务：
   ```bash
   systemctl restart restaurant-api
   ```

3. 检查端口占用：
   ```bash
   lsof -i :8000
   ```

4. 查看详细错误：
   ```bash
   systemctl status restaurant-api
   ```

### 问题 4：依赖安装失败

**错误信息**：
```
ERROR: Could not find a version that satisfies the requirement xxx
```

**解决方案**：
1. 更新 `requirements.txt`
2. 检查 Python 版本兼容性
3. 手动在服务器上安装依赖：
   ```bash
   cd /workspace/projects
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 📊 监控和日志

### 查看 GitHub Actions 日志

在 GitHub 仓库的 **Actions** 标签页中：
1. 点击对应的工作流运行记录
2. 展开 **Deploy to server** 步骤
3. 查看详细日志输出

### 查看服务器日志

```bash
# systemd 服务日志
journalctl -u restaurant-api -f          # 实时查看
journalctl -u restaurant-api -n 100       # 查看最近 100 行

# 应用日志
tail -f logs/api.log
tail -f logs/enhanced_api.log
tail -f logs/member_api.log
tail -f logs/headquarters_api.log
tail -f logs/settlement_api.log
tail -f logs/websocket.log
```

### 查看服务状态

```bash
# 单个服务状态
systemctl status restaurant-api

# 所有服务状态
systemctl status restaurant-api restaurant-enhanced-api member-api headquarters-api settlement-api websocket-api

# 检查端口占用
lsof -i :8000,8001,8004,8006,8007,8008
```

## 🔧 常用命令

### systemd 服务管理

```bash
# 重启所有服务
systemctl restart restaurant-api
systemctl restart restaurant-enhanced-api
systemctl restart member-api
systemctl restart headquarters-api
systemctl restart settlement-api
systemctl restart websocket-api

# 停止所有服务
systemctl stop restaurant-api
systemctl stop restaurant-enhanced-api
systemctl stop member-api
systemctl stop headquarters-api
systemctl stop settlement-api
systemctl stop websocket-api

# 启用开机自启
systemctl enable restaurant-api

# 禁用开机自启
systemctl disable restaurant-api
```

### 手动部署脚本

```bash
# 完整自动化部署（拉取代码 + 更新依赖 + 重启服务）
cd /workspace/projects
bash scripts/auto_deploy.sh

# 仅重启服务
systemctl restart restaurant-api

# 仅更新代码
git pull origin main
```

## 📝 工作流配置说明

### 触发条件

```yaml
on:
  push:
    branches:
      - main        # 推送到 main 分支
      - master      # 推送到 master 分支
      - develop     # 推送到 develop 分支
  workflow_dispatch:  # 支持手动触发
```

### 环境变量

工作流支持以下环境变量（通过 GitHub Secrets 配置）：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SERVER_IP` | 服务器 IP 地址 | 必填 |
| `SERVER_USER` | 服务器用户名 | 必填 |
| `PROJECT_PATH` | 项目路径 | `/workspace/projects` |

### 部署步骤

1. **Checkout code** - 检出代码
2. **Setup SSH** - 配置 SSH 连接
3. **Deploy to server** - 连接服务器并部署：
   - 拉取最新代码
   - 更新 Python 依赖
   - 重启 API 服务
   - 验证服务状态
4. **Notify deployment status** - 通知部署状态

## 🎯 最佳实践

1. **分支管理**：
   - `main`: 生产环境，自动部署
   - `develop`: 开发环境，自动部署到测试服务器
   - `feature/*`: 功能分支，不自动部署

2. **提交信息规范**：
   ```
   feat: 新功能
   fix: 修复 bug
   docs: 文档更新
   refactor: 代码重构
   chore: 构建/工具变更
   ```

3. **部署前检查**：
   - 本地测试通过
   - 代码审查完成
   - 更新相关文档

4. **回滚方案**：
   ```bash
   # 查看提交历史
   git log --oneline

   # 回滚到指定版本
   git reset --hard <commit-hash>
   git push origin main --force
   ```

## 📚 相关文档

- [Netlify 部署指南](./NETLIFY_DEPLOYMENT.md)
- [系统架构文档](./COMMERCIAL_DEPLOYMENT.md)
- [用户使用手册](./USER_MANUAL.md)
- [故障排查指南](./TROUBLESHOOTING_GUIDE.md)

## 🆘 获取帮助

如有问题，请：
1. 查看 [故障排查指南](./TROUBLESHOOTING_GUIDE.md)
2. 检查 GitHub Actions 日志
3. 查看服务器日志文件
4. 联系技术支持

---

**最后更新**: 2025-01-10
