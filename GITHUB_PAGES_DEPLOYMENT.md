# 🚀 GitHub Pages 部署指南

## 📋 快速部署步骤

### 第一步：启用GitHub Pages

1. 访问你的GitHub仓库：
   ```
   https://github.com/wczlee9-bit/restaurant-system
   ```

2. 进入仓库设置：
   - 点击仓库顶部的 **"Settings"** 标签

3. 配置Pages：
   - 在左侧菜单中找到 **"Pages"** 选项
   - 在 **"Build and deployment"** 部分：
     - **Source**: 选择 **"GitHub Actions"** （推荐，已配置自动部署）
     - 或者选择 **"Deploy from a branch"**：
       - **Branch**: 选择 `main`
       - **Folder**: 选择 `/assets`
   - 点击 **"Save"** 保存设置

4. 等待部署完成（通常需要1-3分钟）

5. 部署成功后，访问：
   ```
   https://wczlee9-bit.github.io/restaurant-system/
   ```

---

## 🌐 访问地址

### 主门户页面
```
https://wczlee9-bit.github.io/restaurant-system/portal.html
```

### 各功能页面

| 功能模块 | 访问URL |
|---------|---------|
| 🏠 门户首页 | `/portal.html` |
| 👤 顾客点餐 | `/customer_order_v3.html` |
| 🏪 工作人员登录 | `/login_standalone.html` |
| 👨‍🍳 厨师工作台 | `/kitchen_display.html` |
| 🍽️ 订单管理 | `/staff_workflow.html` |
| 📋 菜品管理 | `/menu_management.html` |
| 📦 库存管理 | `/inventory_management.html` |
| 🏬 店铺设置 | `/shop_settings.html` |
| 👥 会员中心 | `/member_center.html` |
| 🏢 总公司后台 | `/headquarters_dashboard.html` |
| 💰 结算管理 | `/settlement_management.html` |
| 🎁 优惠管理 | `/discount_management.html` |

---

## ⚙️ GitHub Actions 自动部署（已配置）

项目已配置自动部署工作流（`.github/workflows/deploy-pages.yml`），每次推送到main分支会自动触发部署。

### 工作流特点：
- ✅ 自动部署assets目录到GitHub Pages
- ✅ 支持手动触发部署
- ✅ 并发控制，避免冲突
- ✅ 完整的权限配置

### 查看部署状态：
1. 进入仓库的 **"Actions"** 标签
2. 查看最新的部署工作流
3. 点击可查看详细日志

---

## 🔄 手动触发部署

如果你想手动触发部署（不推送代码）：

1. 进入仓库 **Actions** 标签
2. 选择 **"Deploy to GitHub Pages"** 工作流
3. 点击右侧的 **"Run workflow"** 按钮
4. 选择分支 `main`，点击 **"Run workflow"** 绿色按钮

---

## 📝 自定义域名（可选）

如果你想使用自定义域名：

### 方法1：CNAME文件方式
1. 在 `assets/` 目录下创建 `CNAME` 文件
2. 文件内容为你的域名，例如：`restaurant.yourdomain.com`
3. 提交并推送到GitHub
4. 在域名DNS配置中添加CNAME记录：
   ```
   restaurant.yourdomain.com → wczlee9-bit.github.io
   ```

### 方法2：GitHub Settings方式
1. 在 **Settings → Pages** 中找到 **"Custom domain"**
2. 输入你的域名并保存
3. 根据提示配置DNS记录
4. 启用 **"Enforce HTTPS"** （推荐）

---

## ⚠️ 重要配置说明

### API代理配置

GitHub Pages只托管静态前端文件，后端API请求需要通过代理或CORS配置。

**当前配置**：所有HTML文件中的API请求直接指向后端服务器：
```
http://115.191.1.219:8000
http://115.191.1.219:8001
http://115.191.1.219:8004
http://115.191.1.219:8006
http://115.191.1.219:8007
```

**注意事项**：
- 确保后端API服务器对外开放（防火墙允许外部访问）
- 确保后端API配置了CORS允许跨域请求
- 如果有HTTPS域名，建议配置HTTPS API

### CORS配置示例（后端）

如果后端使用FastAPI，需要配置CORS中间件：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://wczlee9-bit.github.io",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🧪 测试部署

部署完成后，按以下步骤测试：

### 1. 验证主页面
访问：`https://wczlee9-bit.github.io/restaurant-system/portal.html`
- ✅ 页面正常加载
- ✅ 所有链接可点击

### 2. 测试顾客点餐
访问：`https://wczlee9-bit.github.io/restaurant-system/customer_order_v3.html`
- ✅ 菜单列表加载
- ✅ API请求成功（检查浏览器控制台）
- ✅ 下单功能正常

### 3. 测试工作人员登录
访问：`https://wczlee9-bit.github.io/restaurant-system/login_standalone.html`
- ✅ 登录页面正常
- ✅ 登录后进入工作台

### 4. 测试API连接
打开浏览器开发者工具（F12）→ Network标签：
- 查看API请求状态（应该为200）
- 检查是否有CORS错误

---

## 🆚 GitHub Pages vs Netlify

| 特性 | GitHub Pages | Netlify |
|-----|-------------|---------|
| 免费额度 | ✅ 无限制 | ✅ 100GB/月 |
| 自定义域名 | ✅ 支持 | ✅ 支持 |
| HTTPS | ✅ 自动证书 | ✅ 自动证书 |
| 构建工具 | ✅ GitHub Actions | ✅ 内置 |
| 表单处理 | ❌ 不支持 | ✅ 支持 |
| 服务器函数 | ❌ 不支持 | ✅ 支持 |
| API代理 | ❌ 需后端配置 | ✅ 支持 |
| CDN | ✅ 全球CDN | ✅ 全球CDN |
| 部署速度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**推荐**：对于纯静态前端站点，GitHub Pages完全够用且稳定。

---

## 🛠️ 常见问题

### Q1: 部署后页面显示404？
**A**: 检查Settings → Pages的发布目录是否设置为 `/assets`

### Q2: API请求失败？
**A**:
1. 确认后端服务器运行正常
2. 检查浏览器控制台是否有CORS错误
3. 确认防火墙允许外部访问

### Q3: 页面样式异常？
**A**: 清除浏览器缓存，按Ctrl+F5强制刷新

### Q4: WebSocket连接失败？
**A**: GitHub Pages仅支持HTTPS，需要确保WebSocket也使用wss://协议

### Q5: 自定义域名不生效？
**A**:
1. DNS记录需要时间生效（最长48小时）
2. 检查DNS配置是否正确
3. 确认CNAME文件存在（如使用）

---

## 📞 获取帮助

遇到问题？查看以下资源：

- [GitHub Pages 官方文档](https://docs.github.com/en/pages)
- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- 本项目其他部署文档：
  - `NETLIFY_DEPLOYMENT.md`
  - `COMMERCIAL_DEPLOYMENT.md`
  - `QUICK_DEPLOYMENT.md`

---

## ✅ 部署检查清单

- [ ] GitHub仓库已创建
- [ ] 代码已推送到main分支
- [ ] GitHub Pages已启用
- [ ] 发布目录设置为 /assets
- [ ] 部署成功完成
- [ ] 访问主页面验证
- [ ] 测试所有功能模块
- [ ] API连接正常
- [ ] WebSocket实时推送正常
- [ ] （可选）自定义域名配置完成

---

**祝部署顺利！🎉**
