# Netlify 手动部署配置指南

如果自动部署继续失败，请按照以下步骤在 Netlify 控制台手动配置：

## 问题症状
```
Failed during stage 'Install dependencies': dependency_installation script returned non-zero exit code: 1
```

## 解决方案

### 方法 1：在 Netlify 控制台配置构建设置

1. 登录 [Netlify Dashboard](https://app.netlify.com/)
2. 选择项目：`mellow-rabanadas-877f3e`
3. 进入 `Site configuration` -> `Build & deploy` -> `Continuous deployment`
4. 找到 `Build settings` 部分
5. 点击 `Edit settings`
6. 配置以下设置：

```
Build directory: assets
Build command: (留空)
Publish directory: (留空，自动检测)
```

7. 点击 `Save` 保存

### 方法 2：手动部署

1. 进入 `Deploys` 页面
2. 点击 `New manual deploy`
3. 选择分支：`main`
4. 点击 `Deploy branch`

### 方法 3：拖拽部署

1. 在本地将 `assets` 文件夹打包为 zip
2. 登录 Netlify Dashboard
3. 点击 `Add new site` -> `Deploy manually`
4. 拖拽 zip 文件到部署区域

### 方法 4：删除并重新连接仓库

1. 在 Netlify 项目页面，进入 `Site configuration` -> `Build & deploy` -> `Continuous deployment`
2. 找到 `Connected repository` 部分
3. 点击 `Disconnect repository`
4. 点击 `Connect to repository`
5. 重新连接 GitHub 仓库：`wczlee9-bit/restaurant-system`
6. 选择 `main` 分支
7. **重要**：在构建配置中，确保 `Build directory` 设置为 `assets`，`Build command` 留空

### 验证部署

部署成功后，验证以下内容：

1. **文件大小检查**：
   - 访问：`https://mellow-rabanadas-877f3e.netlify.app/customer_order_v3.html`
   - 右键 -> 检查 -> Network 标签
   - 刷新页面，查看 `customer_order_v3.html` 文件大小
   - 应该为 **42KB**（旧版本是 36KB）

2. **功能测试**：
   - 访问：`https://mellow-rabanadas-877f3e.netlify.app/customer_order_v3.html?table=1`
   - 确认能看到菜品列表
   - 测试桌号选择和重试按钮

## 常见问题

### Q: 为什么一直提示 "Install dependencies" 失败？
A: Netlify 可能在检测到某些配置时尝试安装依赖。最简单的解决方法是在控制台手动配置，将 `Build command` 留空。

### Q: 如何确认部署成功了？
A: 检查 `customer_order_v3.html` 文件大小是否为 42KB，并测试页面功能是否正常。

### Q: 之前的配置文件怎么办？
A: `netlify.toml` 和 `assets/_redirects` 会自动生效。手动配置会覆盖这些设置。

## 技术支持

如果以上方法都无法解决问题，请提供以下信息：

1. Netlify 部署日志的完整输出
2. Netlify 项目的 Build settings 截图
3. 浏览器控制台的错误信息（按 F12 查看）

---

最后更新：2026-01-12
