# Netlify 部署步骤指南

## 🚀 快速开始 - 拖拽部署（推荐）

这是最简单、最快速的部署方法，适合快速部署和测试。

### 步骤 1：准备文件

确保你有以下文件：
- `assets/` 目录及其所有HTML文件
- `netlify.toml` 配置文件

### 步骤 2：登录 Netlify

1. 访问 [https://app.netlify.com/](https://app.netlify.com/)
2. 点击 "Log in" 登录或注册账户
3. 可以使用 GitHub、GitLab、Bitbucket 或邮箱登录

### 步骤 3：创建新站点

1. 登录后，点击 "Add new site" 按钮
2. 选择 "Deploy manually"（手动部署）

### 步骤 4：上传文件

**重要：先上传 `assets/` 目录**

1. 在上传区域，你会看到一个虚线框 "Drag and drop your site output folder here"
2. 将整个 `assets/` 文件夹拖拽到上传区域
3. 等待文件上传完成（显示蓝色对勾）

**然后上传 `netlify.toml` 配置文件**

1. 将 `netlify.toml` 文件拖拽到相同的上传区域
2. 等待上传完成

### 步骤 5：部署完成

1. 上传完成后，Netlify会自动开始部署
2. 等待 1-2 分钟，状态变为 "Published"
3. 点击生成的随机网址访问你的站点（例如：`https://amazing-coder-123456.netlify.app/`）

### 步骤 6：自定义域名（可选）

1. 在站点页面，点击 "Site settings"
2. 找到 "Domain management" → "Change site name"
3. 输入你想要的站点名称（例如：`my-restaurant`）
4. 点击 "Save"
5. 新地址变为：`https://my-restaurant.netlify.app/`

## 📦 部署检查清单

部署完成后，请检查以下项目：

- [ ] 门户页面可以访问
- [ ] 顾客点餐页面可以正常加载
- [ ] 工作人员登录页面可以访问
- [ ] API代理配置正确（netlify.toml）
- [ ] 所有页面的样式正常加载
- [ ] Vue 3 和 Element Plus 加载成功

## 🔧 配置修改

### 修改后端服务器地址

如果你的后端API服务器地址不是 `115.191.1.219`，需要修改 `netlify.toml`：

```toml
# 修改所有API代理配置中的IP地址
[[redirects]]
  from = "/api/*"
  to = "http://YOUR_NEW_IP:8000/api/:splat"
  status = 200
  force = true
```

修改后，重新上传 `netlify.toml` 文件到Netlify。

### 添加自定义域名

1. 在 Netlify 站点设置中，点击 "Domain management"
2. 点击 "Add custom domain"
3. 输入你的域名（例如：`restaurant.example.com`）
4. Netlify会显示DNS配置信息
5. 到你的域名注册商处添加DNS记录：
   - 类型：CNAME
   - 名称：restaurant（或你想要的子域名）
   - 值：`your-site-name.netlify.app`
6. 等待DNS生效（通常 24-48 小时）

## 🔄 更新部署

当你修改了代码后，需要更新部署：

### 方法 1：覆盖部署

1. 重复上面的步骤 4（拖拽上传）
2. 上传新的 `assets/` 文件夹
3. 上传新的 `netlify.toml` 文件
4. 等待部署完成

### 方法 2：Git集成（推荐用于持续开发）

1. 将代码推送到GitHub
2. 在Netlify中点击 "New site from Git"
3. 连接GitHub仓库
4. 配置构建设置：
   - Branch to deploy: `main` 或 `master`
   - Build command: `# No build command`
   - Publish directory: `assets`
5. 点击 "Deploy site"
6. 之后每次推送到GitHub，Netlify会自动部署

## 🐛 常见问题

### Q1: 页面显示 "404 Not Found"

**原因：** 文件未正确上传或路径错误

**解决方案：**
1. 确认 `assets/` 目录中的所有文件都已上传
2. 检查 `netlify.toml` 中的重定向规则
3. 在 Netlify 站点设置中查看部署日志

### Q2: API 请求失败

**原因：** API代理配置错误或后端服务未启动

**解决方案：**
1. 检查 `netlify.toml` 中的API地址是否正确
2. 确认后端API服务已启动（端口 8000, 8004, 8006, 8007）
3. 在浏览器中直接访问API地址测试连通性

### Q3: 样式显示异常

**原因：** CDN资源加载失败

**解决方案：**
1. 检查HTML文件中的CDN链接
2. 确认网络可以访问 unpkg.com
3. 查看浏览器控制台的错误信息

### Q4: 部署失败

**原因：** 文件上传过程中出错

**解决方案：**
1. 重新上传所有文件
2. 确保文件名符合规范（无空格、特殊字符）
3. 检查文件大小（单个文件 < 25MB）

## 📊 监控和维护

### 查看部署日志

1. 在 Netlify 站点页面，点击 "Deploys"
2. 点击最近的部署记录
3. 查看 "Deploy log" 了解详细信息

### 启用函数日志

1. 在站点设置中，点击 "Functions"
2. 点击 "Function logs"
3. 实时查看函数执行日志

### 设置表单通知（如果使用表单功能）

1. 在站点设置中，点击 "Forms"
2. 配置表单通知邮箱
3. 查看表单提交记录

## 🔐 安全配置

### 启用密码保护（可选）

1. 在站点设置中，点击 "Site protection"
2. 启用密码保护
3. 设置用户名和密码
4. 访问站点时需要输入凭证

### 配置访问控制

在 `netlify.toml` 中添加：
```toml
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "SAMEORIGIN"
    X-Content-Type-Options = "nosniff"
```

## 📈 性能优化

Netlify自动提供以下优化：
- ✅ 全球CDN加速
- ✅ 自动压缩
- ✅ HTTP/2 支持
- ✅ 自动HTTPS证书

### 手动优化建议

1. **图片优化**
   - 使用 WebP 格式
   - 控制图片大小（< 300KB）
   - 提供多种尺寸（响应式图片）

2. **代码优化**
   - 压缩 JavaScript 和 CSS
   - 使用懒加载
   - 减少 HTTP 请求

3. **缓存策略**
   - 静态资源设置长期缓存
   - HTML文件不缓存

## 🎉 完成！

恭喜你成功部署了餐饮点餐系统！

现在你可以：
- 顾客扫码点餐
- 管理员管理订单
- 会员查看积分
- 店长配置优惠
- ...

如有问题，请参考 `PRODUCTION_DEPLOYMENT.md` 或联系技术支持。

---

**最后更新：** 2024-01-15
**版本：** v2.0.0
