# GitHub Pages 部署指南

本指南说明如何将餐饮系统前端部署到 GitHub Pages。

## 为什么选择 GitHub Pages？

- ✅ **完全免费**：无带宽限制，无构建分钟数限制
- ✅ **稳定可靠**：基于 GitHub 全球 CDN
- ✅ **自动化部署**：推送代码即自动部署
- ✅ **HTTPS 支持**：自动提供 HTTPS 证书
- ✅ **自定义域名**：支持绑定自定义域名

## 部署步骤

### 步骤 1：推送代码到 GitHub

确保你的代码已经推送到 GitHub 仓库的 `main` 或 `master` 分支。

```bash
git add .
git commit -m "chore: 添加 GitHub Pages 自动化部署配置"
git push origin main
```

### 步骤 2：启用 GitHub Pages

1. 进入你的 GitHub 仓库
2. 点击 **Settings**（设置）
3. 在左侧菜单找到 **Pages**
4. 在 **Build and deployment** 部分：
   - **Source** 选择：`GitHub Actions`
   - （不要选择 Deploy from a branch）
5. 点击 **Save** 保存

### 步骤 3：等待自动部署

配置完成后，当你推送代码时，GitHub Actions 会自动：
1. 触发 `.github/workflows/deploy.yml` 工作流
2. 将 `assets` 目录部署到 GitHub Pages
3. 访问：`https://<你的用户名>.github.io/<仓库名>/`

### 步骤 4：验证部署

部署完成后，你可以在以下位置查看：
- 仓库的 **Actions** 标签页：查看部署进度和日志
- **Settings -> Pages**：查看部署的 URL

## 访问地址

部署成功后，你的前端地址为：

```
https://<你的用户名>.github.io/<仓库名>/
```

例如，如果用户名是 `example`，仓库名是 `restaurant-system`，地址就是：
```
https://example.github.io/restaurant-system/
```

## API 代理配置

`assets/_redirects` 文件已配置 API 代理规则：
- `/api/*` -> Render 后端
- `/ws/*` -> Render WebSocket
- `/health` -> 健康检查端点

GitHub Pages 会自动识别 `_redirects` 文件并应用这些规则。

## 自定义域名（可选）

如果你有自定义域名，可以：

1. 在 `assets` 目录创建 `CNAME` 文件，内容为你的域名：
   ```
   www.yourdomain.com
   ```

2. 在域名 DNS 设置中添加 CNAME 记录，指向：
   ```
   <你的用户名>.github.io
   ```

3. 在 **Settings -> Pages** 中配置自定义域名

## 故障排查

### 问题 1：Actions 工作流失败

检查：
- 仓库权限是否启用 Actions（Settings -> Actions -> General）
- 工作流权限是否正确（Settings -> Actions -> General -> Workflow permissions）

### 问题 2：页面 404

检查：
- `assets` 目录下是否有 `portal.html` 等入口文件
- GitHub Actions 工作流是否成功完成
- 访问的 URL 是否正确（注意仓库名）

### 问题 3：API 调用失败

检查：
- `_redirects` 文件是否在 `assets` 目录下
- Render 后端是否正常运行
- 浏览器控制台的网络请求是否正确代理到 Render

## 本地测试

在推送前，你可以本地测试前端：

```bash
# 进入 assets 目录
cd assets

# 使用 Python 启动简单的 HTTP 服务器
python3 -m http.server 8080

# 访问 http://localhost:8080
```

## 总结

- ✅ 后端：Render (`https://restaurant-system-vzj0.onrender.com`)
- ✅ 数据库：Render PostgreSQL（60个菜品，43个桌号）
- 🔄 前端：GitHub Pages（配置后自动部署）

配置完成后，整个系统将完全免费运行！
