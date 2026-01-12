# Netlify 手动部署配置指南

如果自动部署继续失败，请按照以下步骤在 Netlify 控制台手动配置：

## 问题症状
```
Failed during stage 'Install dependencies': dependency_installation script returned non-zero exit code: 1
```

## 解决方案（按推荐顺序）

### 方法 1：在 Netlify 控制台配置构建设置 ⭐ 推荐

这是最简单且最可能成功的方法。

**步骤：**

1. 登录 [Netlify Dashboard](https://app.netlify.com/)
2. 在左侧找到项目列表，点击 `mellow-rabanadas-877f3e`
3. 在顶部导航栏找到 `Site configuration`（或直接在页面左侧）
4. 点击 `Build & deploy`
5. 在左侧菜单点击 `Continuous deployment`
6. 找到 `Build settings` 部分（可能需要向下滚动）
7. 点击 `Edit settings` 或铅笔图标
8. 配置以下设置：

```
Build directory: assets
Build command: (留空，不要填写任何内容)
```

9. 点击 `Save` 保存

**保存后，Netlify 会自动触发新的部署。**

---

### 方法 2：手动触发部署

如果方法 1 配置后没有自动部署，可以手动触发：

**步骤：**

1. 在项目页面顶部点击 `Deploys` 标签
2. 向下滚动到 `Trigger deploy` 部分
3. 点击 `Deploy site` 按钮
4. 或者找到 `Branch deploy` 选项，选择 `main` 分支
5. 点击触发部署

**注意：** 新版 Netlify 的界面可能有所不同，关键是找到 "Deploy" 或 "Trigger" 相关的按钮。

---

### 方法 3：重新连接仓库

如果上述方法都无效，可以尝试重新连接 GitHub：

**步骤：**

1. 进入 `Site configuration` -> `Build & deploy` -> `Continuous deployment`
2. 找到 `Connected repository` 部分
3. 点击 `Disconnect repository`（可能有三个点菜单）
4. 确认断开
5. 点击 `Connect to repository` 或 `Add new repository`
6. 选择 GitHub
7. 搜索并选择仓库：`wczlee9-bit/restaurant-system`
8. 选择 `main` 分支
9. **关键步骤**：在构建配置页面，设置：
   ```
   Build directory: assets
   Build command: (留空)
   ```
10. 点击 `Deploy site`

---

### 方法 4：清空 Netlify 缓存

有时缓存会导致问题：

1. 进入 `Deploys` 页面
2. 找到最近一次失败的部署
3. 点击右侧的三个点菜单（⋮）
4. 选择 `Deploy site` -> `Clear cache and retry`

---

### 方法 5：删除并重新创建站点（最后手段）

如果以上方法都无效：

1. **警告：** 这会删除当前的站点配置和部署历史
2. 在 Netlify Dashboard 中，找到 `mellow-rabanadas-877f3e` 项目
3. 点击 `Site settings`（齿轮图标）
4. 滚动到底部，找到 `Danger zone` 部分
5. 点击 `Delete site`
6. 点击 `Add new site` -> `Import an existing project`
7. 选择 GitHub
8. 选择仓库 `wczlee9-bit/restaurant-system`
9. 配置构建设置：
   ```
   Build directory: assets
   Build command: (留空)
   ```
10. 点击 `Deploy site`

### 验证部署

部署成功后，验证以下内容：

### 1. 检查部署状态

1. 进入 `Deploys` 页面
2. 查看最新的部署记录
3. 状态应该是绿色勾号（✓ Published）

### 2. 文件大小检查

- 访问：`https://mellow-rabanadas-877f3e.netlify.app/customer_order_v3.html`
- 按 F12 打开开发者工具
- 切换到 `Network` 标签
- 刷新页面（F5）
- 在列表中找到 `customer_order_v3.html`
- 查看文件大小，应该为 **42KB**（旧版本是 36KB）

### 3. 功能测试

- 访问：`https://mellow-rabanadas-877f3e.netlify.app/customer_order_v3.html?table=1`
- 确认能看到菜品列表
- 测试桌号选择功能
- 测试重试按钮

### 4. 检查构建日志

如果部署成功，构建日志应该显示类似：
```
3:53:36 PM: Build ready to start
3:53:40 PM: Build ready to start
3:53:41 PM: Finished processing build request in 4.865s
3:53:44 PM: Starting to deploy site from 'assets'
3:53:46 PM: Finished processing build request in 2.567s
3:53:46 PM: Site is live
```

## 常见问题

### Q: 为什么一直提示 "Install dependencies" 失败？
**A:** Netlify 可能在检测到某些配置时尝试安装依赖（即使没有 package.json）。最简单的解决方法是在控制台手动配置，将 `Build command` 留空。

### Q: 如何确认部署成功了？
**A:** 检查 `customer_order_v3.html` 文件大小是否为 42KB，并测试页面功能是否正常。

### Q: 之前的配置文件怎么办？
**A:** `netlify.toml` 和 `assets/_redirects` 会自动生效。手动配置会覆盖这些设置。如果手动配置后仍然失败，可以考虑删除 `netlify.toml` 试试。

### Q: 找不到 "Edit settings" 按钮怎么办？
**A:** 新版 Netlify 界面可能有所不同。寻找任何可以编辑构建设置的地方，或者直接点击 `Disconnect repository` 重新连接仓库。

### Q: Build directory 应该填什么？
**A:** 应该填写 `assets`，这是项目中的静态文件目录。

### Q: Build command 应该填什么？
**A:** 应该留空，不要填写任何内容。这是因为这是一个纯静态 HTML 站点，不需要构建步骤。

## 技术支持

如果以上方法都无法解决问题，请提供以下信息：

1. Netlify 部署日志的完整输出
2. Netlify 项目的 Build settings 截图
3. 浏览器控制台的错误信息（按 F12 查看）

---

最后更新：2026-01-12
