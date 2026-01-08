# Netlify 404 错误修复指南

## 问题描述
访问 Netlify 部署的站点时出现 404 错误。

## 根本原因
Netlify 的重定向规则顺序不正确，通用的 `/*` 规则会在特殊路径规则之前匹配，导致 `/login` 等路径无法正确重定向。

## 已修复内容
✅ 调整了 `netlify.toml` 中的重定向规则顺序
✅ 将特殊路径规则放在通用规则之前
✅ 添加了更多的路径映射规则

## 需要手动完成的步骤

### 1. 配置 Git 远程仓库
如果还没有配置 Git 远程仓库，请执行：

```bash
# 添加远程仓库（替换为你的 GitHub 仓库地址）
git remote add origin https://github.com/your-username/your-repo.git

# 或使用 SSH
git remote add origin git@github.com:your-username/your-repo.git
```

### 2. 推送到 GitHub
```bash
git push origin main
```

### 3. 等待 Netlify 自动部署
- 登录 Netlify 控制台
- 查看部署状态（通常需要 1-2 分钟）
- 确保部署成功

## 可访问的 URL

部署成功后，可以通过以下 URL 访问系统：

### 主要页面
- **登录页面**: `https://restaurant-system.netlify.app/login`
- **首页**: `https://restaurant-system.netlify.app/`
- **工作人员端**: `https://restaurant-system.netlify.app/staff-workflow`
- **店铺设置**: `https://restaurant-system.netlify.app/shop-settings`

### 测试页面
- **完整测试系统**: `https://restaurant-system.netlify.app/restaurant_full_test.html`
- **快速测试**: `https://restaurant-system.netlify.app/restaurant_test_system.html`

### 直接访问 HTML 文件（备用方案）
如果重定向规则仍有问题，可以直接访问 HTML 文件：
- `https://restaurant-system.netlify.app/login_standalone.html`
- `https://restaurant-system.netlify.app/index.html`
- `https://restaurant-system.netlify.app/staff_workflow.html`
- `https://restaurant-system.netlify.app/shop_settings.html`

## 测试登录功能

### 演示账号
**系统管理员**
- 用户名: `admin`
- 密码: `admin123`

**总公司账号**
- 用户名: `headquarters`
- 密码: `hq123456`

### 测试步骤
1. 访问 `https://restaurant-system.netlify.app/login`
2. 点击语言切换按钮选择中文/英文
3. 点击"使用管理员登录"或"使用总公司账号登录"
4. 应该能成功登录并跳转到工作人员端

## 如果仍然出现 404

### 检查 Netlify 配置
1. 登录 Netlify
2. 进入站点设置
3. 检查以下配置：
   - **Build & deploy > Build settings**:
     - Base directory: 留空或设置为根目录
     - Publish directory: `assets`
     - Build command: 留空

### 检查部署文件
在 Netlify 的部署日志中，确认以下文件已成功部署：
- `assets/login_standalone.html`
- `assets/index.html`
- `assets/staff_workflow.html`
- `assets/shop_settings.html`

### 清除缓存
1. Netlify 控制台 > Site settings > Build & deploy
2. 找到 "Purge cache" 按钮
3. 清除所有缓存
4. 重新部署

### 本地测试
在推送前，可以本地测试静态文件：
```bash
# 安装 http-server（如果还没有）
npm install -g http-server

# 在 assets 目录启动服务器
cd assets
http-server -p 8080

# 访问 http://localhost:8080/login_standalone.html
```

## 常见问题

### Q: 为什么不直接使用 `/login_standalone.html`？
A: 使用 `/login` 作为友好 URL 更符合用户体验，也便于后续维护。重定向规则允许我们保持简洁的 URL 结构。

### Q: 如果 GitHub 已经配置了远程仓库怎么办？
A: 只需要执行 `git push origin main` 即可推送代码。

### Q: 如何检查 Netlify 部署是否成功？
A:
1. 登录 Netlify 控制台
2. 查看站点主页的 "Deploys" 标签
3. 绿色的 "Published" 状态表示部署成功
4. 点击部署可以查看详细日志

### Q: 如何查看重定向规则是否生效？
A:
1. Netlify 控制台 > Site settings
2. "Edge handlers" 或 "Redirects" 标签
3. 查看重定向规则列表和测试工具

## 联系支持
如果按照以上步骤操作后仍有问题，请检查：
- Netlify 部署日志中的错误信息
- 浏览器开发者工具中的 Network 标签
- 浏览器控制台中的 JavaScript 错误

---

**最后更新时间**: 2025-01-08
**修复版本**: v1.1.0
