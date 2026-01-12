# 🍽️ 餐饮点餐系统 - 多店铺扫码点餐系统

## 🎯 系统概述

支持多角色权限管理、扫码点餐、订单流转、库存管理、会员积分、营收分析、实时通信及小票打印的全流程餐饮管理系统。

**最新版本**: v2.0.0

**核心功能**:
- ✅ 扫码点餐（支持多店铺）
- ✅ 多角色管理（顾客、厨师、传菜员、收银员、店长、系统管理员、总公司）
- ✅ 订单状态流转（待确认→制作中→待传菜→上菜中→已完成）
- ✅ 会员系统（积分、等级、二维码）
- ✅ 库存管理
- ✅ 营收分析
- ✅ 实时通信（WebSocket）
- ✅ 小票打印
- ✅ 跨店铺结算
- ✅ 菜品图片上传
- ✅ 优惠配置系统

---

## 🚀 在线部署地址（推荐）

### 当前部署状态

✅ **后端服务**：Render (https://restaurant-system-vzj0.onrender.com)
- PostgreSQL 数据库已连接
- 包含完整数据（60个菜品，43个桌号，4个公司，5个店铺）
- API 健康检查：https://restaurant-system-vzj0.onrender.com/health

🔄 **前端服务**：GitHub Pages（配置后自动部署）
- 完全免费，无带宽限制
- 自动 HTTPS，稳定可靠

### 快速部署到 GitHub Pages

**3 分钟完成部署**：[查看快速开始指南](QUICK_START.md)

**完整配置指南**：[查看 GitHub Pages 部署指南](GITHUB_PAGES_SETUP.md)

**部署步骤**：
1. 推送代码到 GitHub
2. 在 Settings → Pages 中选择 Source 为 `GitHub Actions`
3. 自动部署完成，访问你的 GitHub Pages URL

---

## 🚀 从沙盒到生产环境

### 架构说明

```
沙盒环境（开发）
    ↓ git push
GitHub（代码仓库）
    ├─→ GitHub Actions → Render 后端 API
    └─→ GitHub Pages → 前端（完全免费）
```

### 部署选项

| 部署方式 | 状态 | 说明 |
|---------|------|------|
| **GitHub Pages** | ✅ 推荐 | 完全免费，自动 HTTPS，CDN 加速 |
| **Netlify** | ⚠️ 受限 | 免费计划带宽已用完，需升级或下月重置 |
| **本地环境** | ✅ 可用 | 适合开发和测试 |

### 日常开发流程

```bash
git add .
git commit -m "更新功能"
git push origin main
# 自动部署到 GitHub Pages ✨
```

---

## 🚀 GitHub Actions 自动部署（后端）

### 为什么使用 GitHub Actions？

✅ **一键部署**：推送代码自动部署，无需手动操作
✅ **自动化流程**：拉取代码、更新依赖、重启服务全自动
✅ **可追溯**：完整的部署日志和历史记录
✅ **团队协作**：统一的部署流程
✅ **服务稳定**：systemd 自动重启，崩溃自动恢复
✅ **配置安全**：使用 GitHub Secrets 保护敏感信息

### 快速开始（10分钟配置）

**选择一个指南跟着做**：

1. 🎯 **[一步一步超详细教程](GITHUB_ACTIONS_STEP_BY_STEP.md)** - 最详细，每一步都有说明和验证
2. ⚡ **[快速命令清单](QUICK_COMMANDS.md)** - 直接复制粘贴命令执行
3. 📖 **[快速开始](GITHUB_ACTIONS_QUICKSTART.md)** - 5分钟快速配置

**配置步骤**：
1. 在服务器上生成 SSH 密钥
2. 在 GitHub 配置 3 个 Secrets（SSH_PRIVATE_KEY, SERVER_USER, SERVER_HOST）
3. 推送代码触发自动部署
4. 验证部署成功

### 配置 Secrets

在 GitHub 仓库中配置以下 Secrets：

| Name | Value | 说明 |
|------|-------|------|
| `SSH_PRIVATE_KEY` | 服务器SSH私钥 | 参考 [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md) |
| `SERVER_USER` | `root` | SSH登录用户名 |
| `SERVER_HOST` | `115.191.1.219` | 服务器IP地址 |

### 使用方法

**自动部署**（推荐）：
```bash
git add .
git commit -m "描述你的更改"
git push origin main
# 推送后自动触发部署 ✨
```

**手动触发部署**：
1. 打开 GitHub 仓库
2. 进入 **Actions** 标签
3. 选择 **"🚀 Auto Deploy to Server"** 工作流
4. 点击 **"Run workflow"** 按钮

### 验证部署

**GitHub Actions 页面**：
- 查看工作流执行状态
- 查看详细日志

**服务器端验证**：
```bash
# 检查服务状态
bash scripts/verify_github_actions.sh

# 查看日志
tail -f /workspace/projects/logs/api.log
```

### 详细文档

- ⭐ [GitHub Actions 快速开始](GITHUB_ACTIONS_QUICKSTART.md) - 5分钟快速配置
- 📖 [GitHub Secrets 配置指南](GITHUB_SECRETS_SETUP.md) - 详细配置步骤
- 📘 [GitHub Actions 使用指南](GITHUB_ACTIONS_USAGE.md) - 完整使用文档
- 🔍 [系统验证脚本](scripts/verify_github_actions.sh) - 配置验证工具

---

## 🌐 Netlify 部署（前端）

---

## 📚 文档索引

### 快速开始
- [GitHub Pages 快速开始](QUICK_START.md) - 3 分钟部署到 GitHub Pages ⭐⭐⭐
- [GitHub Pages 完整配置](GITHUB_PAGES_SETUP.md) - GitHub Pages 详细配置指南
- [本地快速测试](LOCALHOST_START.md) - 本地环境快速测试

### 部署文档
- [GitHub Pages 部署指南](GITHUB_PAGES_SETUP.md) - 前端部署到 GitHub Pages ⭐
- [Render 后端部署](RENDER_DEPLOYMENT.md) - 后端部署到 Render
- [GitHub Actions 自动部署](GITHUB_ACTIONS_DEPLOYMENT.md) - 自动部署到生产服务器
- [Netlify 部署指南](NETLIFY_DEPLOYMENT.md) - 前端部署到 Netlify（当前受限）
- [服务器部署指南](SERVER_FRONTEND_DEPLOYMENT.md) - 服务器端部署
- [商用部署文档](COMMERCIAL_DEPLOYMENT.md) - 完整部署架构

### 系统文档
- [系统架构文档](COMMERCIAL_DEPLOYMENT.md) - 系统架构和技术栈
- [用户使用手册](USER_MANUAL.md) - 系统使用指南
- [故障排查指南](TROUBLESHOOTING_GUIDE.md) - 常见问题解决
- [跨店铺结算系统](CROSS_STORE_SETTLEMENT.md) - 结算系统说明

### 功能文档
- [会员系统](USER_MANUAL.md#会员中心) - 会员功能说明
- [优惠配置系统](VERSION_2.0.0_UPDATE_SUMMARY.md) - v2.0.0 新功能
- [订单流程](NEW_ORDER_FLOW.md) - 订单流程说明
- [权限管理](SYSTEM_ADMIN_COMPANY_ACCOUNTS.md) - 角色权限说明

### 测试相关
- [测试指南](TESTING_GUIDE.md) - 系统测试指南
- [账号快速参考](ACCOUNTS_QUICK_REFERENCE.md) - 测试账号信息

---

## ⚠️ 重要提示

**外部IP无法访问（502错误），请使用localhost访问！**

---

## ⚡ 立即开始测试（本地）

**复制这个URL到浏览器打开**：

```
http://localhost:8080/assets/restaurant_full_test.html?table=8
```

**就这么简单！开始测试吧！** 🎮

---

## 📋 核心文件

| 文件 | 用途 |
|------|------|
| **LOCALHOST_START.md** | ⭐ 使用localhost开始测试 |
| **LOCALHOST_ACCESS.html** | 可视化访问页面 |
| **FIXED_ACCESS_GUIDE.md** | 完整的访问指南 |
| **START_TESTING.md** | 最简单的开始指南 |

---

## 🎯 测试流程

打开页面后，按照以下顺序切换角色（顶部按钮）：

```
👤 顾客 → 点餐（添加菜品→提交订单）
👨‍🍳 厨师 → 制作（开始制作→完成制作）
🤵 传菜员 → 上菜（确认上菜）
💰 收银员 → 结账（处理支付→打印小票）
👔 店长 → 查看数据（订单统计、营收数据）
```

---

## 📱 其他访问方式（localhost）

| 用途 | URL |
|------|-----|
| **主入口** | http://localhost:8080/assets/index.html |
| **测试页面** | http://localhost:8080/assets/restaurant_full_test.html |
| **API文档** | http://localhost:8000/docs |

---

## 💡 为什么用localhost？

**原因**：
- 外部IP（9.128.251.82）访问被防火墙阻止（502错误）
- localhost 访问无需通过网络，直接连接本地服务
- 速度更快，更稳定

**适用场景**：
- ✅ 您在沙盒环境中
- ✅ 浏览器和服务在同一台机器上
- ✅ 外部IP无法访问

---

## ❓ 如果localhost也无法访问

### 检查服务

```bash
netstat -tlnp | grep -E ":(8000|8080)"
```

### 重启服务

```bash
cd /workspace/projects
python -m http.server 8080 --bind 0.0.0.0 &
python -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000 &
```

### 使用127.0.0.1

如果localhost不行，尝试：
```
http://127.0.0.1:8080/assets/restaurant_full_test.html?table=8
```

---

## 🎉 立即开始

**复制这个URL到浏览器**：

```
http://localhost:8080/assets/restaurant_full_test.html?table=8
```

---

# 项目结构说明（开发者参考）

# 本地运行
## 运行流程
bash scripts/local_run.sh -m flow

## 运行节点
bash scripts/local_run.sh -m node -n node_name

# 启动HTTP服务
bash scripts/http_run.sh -m http -p 5000

