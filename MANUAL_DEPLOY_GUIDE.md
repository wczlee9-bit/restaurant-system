# 手动部署指南 - 拖拽部署到 Netlify

如果 Git 自动部署一直失败，可以使用拖拽方式手动部署。

## 方法：拖拽部署（最简单、最快）

### 步骤 1: 准备 assets 文件夹

1. **压缩 assets 文件夹**：
   ```bash
   cd /workspace/projects
   zip -r restaurant-system.zip assets/*
   ```

2. **或者直接使用 assets 文件夹**：
   - 在文件管理器中找到 `assets` 文件夹
   - 确保包含所有 HTML 文件

### 步骤 2: 在 Netlify 上拖拽部署

1. **访问 Netlify 首页**：
   - https://app.netlify.com/sites

2. **创建新站点**：
   - 如果还没创建：点击 "Add new site" > "Deploy manually"
   - 如果已经有项目：删除当前失败的项目，重新创建

3. **拖拽部署**：
   - 将 `assets` 文件夹拖拽到 Netlify 的上传区域
   - 或者将 `restaurant-system.zip` 文件拖拽上传

4. **部署完成**：
   - Netlify 会立即部署
   - 1-2 分钟后即可访问

### 步骤 3: 配置重定向规则（可选）

拖拽部署后，可以添加 `netlify.toml` 文件来实现重定向：

1. 在 `assets` 文件夹中创建 `netlify.toml` 文件
2. 复制以下内容：

```toml
# 特殊路径重定向规则
[[redirects]]
  from = "/login"
  to = "/login_standalone.html"
  status = 200

[[redirects]]
  from = "/staff-workflow"
  to = "/staff_workflow.html"
  status = 200

[[redirects]]
  from = "/shop-settings"
  to = "/shop_settings.html"
  status = 200

[[redirects]]
  from = "/table-settings"
  to = "/table_settings.html"
  status = 200

[[redirects]]
  from = "/customer-order"
  to = "/customer_order.html"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

3. 重新上传 assets 文件夹

### 步骤 4: 访问部署后的站点

- 主页：`https://你的站点名.netlify.app/`
- 登录页：`https://你的站点名.netlify.app/login_standalone.html`
- 工作人员端：`https://你的站点名.netlify.app/staff_workflow.html`
- 店铺设置：`https://你的站点名.netlify.app/shop_settings.html`

## 方法：使用 Netlify CLI（开发者推荐）

### 步骤 1: 安装 Netlify CLI

```bash
npm install -g netlify-cli
```

### 步骤 2: 登录 Netlify

```bash
netlify login
```

### 步骤 3: 部署 assets 文件夹

```bash
cd assets
netlify deploy --prod
```

按照提示选择或创建站点，Netlify CLI 会直接上传并部署。

## 为什么 Git 自动部署一直失败？

Netlify 的自动构建系统会：
1. 检测到 `package.json` 文件
2. 尝试运行 `npm install` 或 `yarn install`
3. 即使配置了空的命令，某些情况下仍会尝试构建

拖拽部署方式会跳过整个构建过程，直接部署静态文件，是最可靠的方式。

## 对比 Git 部署和拖拽部署

| 特性 | Git 自动部署 | 拖拽部署 | Netlify CLI |
|------|-------------|----------|-------------|
| 设置复杂度 | 中 | 低 | 中 |
| 部署速度 | 快 | 快 | 快 |
| 自动化 | 高 | 低 | 中 |
| 适合项目 | 构建类项目 | 纯静态项目 | 开发者 |
| 修改后更新 | 推送代码即可 | 需重新拖拽 | 运行命令 |

## 推荐方案

对于本项目（纯静态 HTML），**推荐使用拖拽部署**，因为：
1. 设置简单，不需要配置构建环境
2. 部署快速，直接上传文件
3. 更新方便，需要更新时重新拖拽即可

## 注意事项

1. 拖拽部署后，Netlify 会分配一个随机站点名
2. 可以在 Site settings 中修改域名
3. 更新文件时，直接重新拖拽整个 assets 文件夹

---

**最后更新时间**: 2025-01-08
