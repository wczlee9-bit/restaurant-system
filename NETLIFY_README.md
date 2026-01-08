# 🚀 Netlify 部署 - 快速上手

## 📖 概述

本指南将帮助你快速将扫码点餐系统部署到 Netlify，实现公网访问。

## 🎯 三种部署方式

### 方式一：手动上传（最简单，2分钟）⭐ 推荐

适合：第一次部署、快速测试

**步骤**：
1. 执行打包脚本
   ```bash
   cd /workspace/projects
   bash scripts/deploy_netlify.sh
   ```

2. 访问 Netlify
   - 打开 https://app.netlify.com
   - 登录账号

3. 上传文件
   - 点击 "Add new site" → "Deploy manually"
   - 上传生成的 `restaurant-system.zip` 文件

4. 等待部署完成（1-2分钟）

5. 访问你的网站！

---

### 方式二：Netlify CLI（推荐开发者，5分钟）

适合：频繁更新、喜欢命令行操作

**步骤**：
1. 安装 CLI
   ```bash
   npm install -g netlify-cli
   ```

2. 登录
   ```bash
   netlify login
   ```

3. 部署
   ```bash
   cd /workspace/projects
   netlify deploy --prod --dir=assets
   ```

---

### 方式三：Git 部署（适合团队协作，10分钟）

适合：团队协作、持续集成

**步骤**：
1. 创建 GitHub 仓库
   - 访问 https://github.com/new
   - 创建 `restaurant-system` 仓库

2. 推送代码
   ```bash
   cd /workspace/projects
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/你的用户名/restaurant-system.git
   git push -u origin main
   ```

3. 连接 Netlify
   - Netlify Dashboard → "Add new site" → "Import an existing project"
   - 选择 GitHub 仓库
   - 配置：
     - Build command: (留空)
     - Publish directory: assets

4. 自动部署！

**后续更新**：
```bash
git add .
git commit -m "feat: 新功能"
git push
# Netlify 自动部署
```

---

## ✅ 部署后检查清单

部署完成后，请测试以下功能：

- [ ] 访问主页，页面正常显示
- [ ] 选择桌号，浏览菜单
- [ ] 添加商品到购物车
- [ ] 提交订单，查看状态
- [ ] 切换角色（顾客→厨师→传菜员→收银员→店长）
- [ ] 检查实时通知是否正常
- [ ] 在手机上测试访问

---

## 📚 详细文档

- **快速参考**: [assets/netlify_deployment_quickref.html](assets/netlify_deployment_quickref.html)
- **详细指南**: [NETLIFY_STEP_BY_STEP.md](NETLIFY_STEP_BY_STEP.md)
- **完整文档**: [NETLIFY_DEPLOY.md](NETLIFY_DEPLOY.md)
- **Git 部署**: [GITHUB_DEPLOY.md](GITHUB_DEPLOY.md)
- **快速开始**: [NETLIFY_QUICKSTART.md](NETLIFY_QUICKSTART.md)

---

## 🔧 配置说明

### API 地址

系统已自动配置 API 地址：
- Netlify 环境：使用云端 API
- 本地环境：使用 localhost

无需手动配置，系统会自动检测。

### 安全建议

- ✅ Netlify 默认提供 HTTPS
- ✅ 建议生产环境配置 CORS 限制
- ✅ 定期更新依赖库

---

## 🎉 部署成功后，你将获得

✅ 公开可访问的网站 URL
✅ 自动 HTTPS 加密
✅ 全球 CDN 加速
✅ 支持手机、平板、电脑访问
✅ 持续更新能力
✅ 版本管理（可回滚）

---

## 🆘 常见问题

### Q1: 部署后页面空白？

**解决方法**：
1. 按 `F12` 打开浏览器控制台
2. 查看 Console 标签的错误信息
3. 查看 Network 标签的 API 请求

### Q2: API 请求失败？

**解决方法**：
1. 确认云端 API 服务运行正常
2. 检查 API 地址配置
3. 查看是否有 CORS 错误

### Q3: 如何更新部署？

**解决方法**：
- 手动上传：重新上传 zip 文件
- CLI 部署：`netlify deploy --prod --dir=assets`
- Git 部署：推送代码，自动部署

---

## 💡 快速访问

- **部署快速参考**: 打开 [assets/index.html](assets/index.html)，点击 "🚀 部署指南" 按钮
- **在线查看部署指南**: [assets/netlify_deployment_quickref.html](assets/netlify_deployment_quickref.html)

---

**祝你部署顺利！🚀**
