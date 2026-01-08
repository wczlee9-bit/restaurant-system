# 🚀 快速修复指南 - 顾客扫码后无法显示菜品

## 问题描述

顾客扫码后进入点餐页面，但看不到桌号、菜品分类和菜品列表，导致无法下单测试。

## 根本原因

前端页面使用相对路径（如 `/api/tables/`）访问 API，但在 Netlify 部署环境下，这些请求被发送到 Netlify 服务器，而 Netlify 默认不会将这些请求转发到后端 API 服务器。

## 解决方案

已在代码中添加 Netlify API 代理配置，将所有 `/api/*` 请求转发到后端服务器。

## 快速部署步骤

### 步骤 1：修改 netlify.toml（如果后端 IP 不同）

打开 `netlify.toml` 文件，找到以下配置：

```toml
[[redirects]]
  from = "/api/*"
  to = "http://9.128.251.82:8000/api/:splat"
  status = 200
  force = true
```

如果后端服务器 IP 不是 `9.128.251.82`，请修改为正确的 IP 地址。例如：

```toml
[[redirects]]
  from = "/api/*"
  to = "http://YOUR_BACKEND_IP:8000/api/:splat"
  status = 200
  force = true
```

### 步骤 2：部署到 Netlify

**方法一：拖拽部署（推荐）**

1. 打开项目目录，将 `assets` 文件夹压缩为 zip 文件
2. 访问 https://app.netlify.com/
3. 点击 "Add new site" → "Deploy manually"
4. 将 `assets` 文件夹拖拽到部署区域
5. 等待部署完成（1-2 分钟）
6. 记录部署后的 URL，如：`https://random-name-12345.netlify.app`

**方法二：更新现有 Netlify 站点**

1. 在 Netlify 控制台选择你的站点
2. 点击 "Site settings" → "Build & deploy"
3. 向下滚动到 "Deploy settings"
4. 在 "Build command" 中输入：`echo "No build needed"`
5. 在 "Publish directory" 中输入：`assets`
6. 确保 `netlify.toml` 文件在项目根目录
7. 点击 "Deploy site"

### 步骤 3：测试 API 连接

1. 访问你的 Netlify 站点首页
2. 点击 "🔧 API连接测试" 按钮
3. 点击 "📱 测试顾客端流程"
4. 查看测试结果：
   - ✅ 所有测试通过：可以正常使用
   - ❌ 测试失败：检查后端服务器是否正常运行

### 步骤 4：测试顾客端点餐

1. 在首页点击任意桌号（如 8号桌）
2. 或直接访问：`https://your-site.netlify.app/customer_order.html?table=8`
3. 应该能看到：
   - 桌号信息显示
   - 菜品分类标签
   - 菜品列表和价格

## 常见问题排查

### 问题 1：API 测试失败

**症状**：所有 API 请求都显示 "❌ 失败"

**原因**：后端服务器未运行或 IP 地址配置错误

**解决方法**：
1. 确认后端服务器是否启动：`ssh user@YOUR_IP` → `curl http://localhost:8000/api/tables/`
2. 检查 `netlify.toml` 中的 IP 地址是否正确
3. 检查防火墙是否允许外部访问 8000 端口
4. 修改 `netlify.toml` 后需要重新部署 Netlify 站点

### 问题 2：CORS 错误

**症状**：浏览器控制台显示 CORS 相关错误

**原因**：后端未配置 CORS 允许 Netlify 域名访问

**解决方法**：
在后端 FastAPI 应用中添加 CORS 配置：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或指定具体的 Netlify 域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 问题 3：部分数据加载失败

**症状**：桌号能显示，但菜品列表为空

**原因**：数据库中没有菜品数据或菜单分类数据

**解决方法**：
1. 访问后端 API 文档：`http://YOUR_IP:8000/docs`
2. 手动调用 `/api/menu-items/` 检查数据
3. 如果没有数据，运行初始化脚本：
   ```bash
   python scripts/init_test_data.py
   ```

### 问题 4：页面空白或加载失败

**症状**：顾客端页面完全空白或报错

**原因**：CDN 资源加载失败或 JavaScript 错误

**解决方法**：
1. 按 F12 打开浏览器控制台查看错误信息
2. 检查网络连接是否正常
3. 尝试刷新页面或清除缓存
4. 检查 unpkg CDN 是否可访问：https://unpkg.com/vue@3/dist/vue.global.prod.js

## 验证完整流程

测试人员可以按以下流程进行测试：

### 1. 顾客端测试
- [ ] 访问首页并选择桌号
- [ ] 查看桌号信息
- [ ] 浏览菜品分类
- [ ] 查看菜品列表和价格
- [ ] 添加菜品到购物车
- [ ] 提交订单
- [ ] 查看订单状态

### 2. 工作人员端测试
- [ ] 访问登录页面
- [ ] 使用测试账号登录（参考 `docs/TEST_ACCOUNTS.md`）
- [ ] 查看订单列表
- [ ] 更新订单状态

### 3. API 连接测试
- [ ] 访问 API 测试页面
- [ ] 运行所有测试
- [ ] 确认所有测试通过

## 修改 netlify.toml 后重新部署

如果修改了 `netlify.toml` 文件，需要重新部署 Netlify 站点才能生效：

**拖拽部署模式**：
1. 修改本地 `netlify.toml` 文件
2. 重新将 `assets` 文件夹拖拽到 Netlify
3. 覆盖现有部署

**GitHub 自动部署模式**：
1. 提交 `netlify.toml` 的修改到 GitHub
2. Netlify 自动检测到更改并重新部署
3. 等待部署完成（约 1-2 分钟）

## 技术细节

### API 代理工作原理

```
浏览器 → Netlify → 后端服务器
  ↓
/api/tables/
  ↓
Netlify 代理
  ↓
http://9.128.251.82:8000/api/tables/
```

### 为什么需要代理

- Netlify 是静态网站托管服务，不支持后端 API
- 前端使用相对路径（`/api/*`）便于开发和部署
- 通过 Netlify 的 redirect 功能实现代理转发
- 保持前后端在同一域名下，避免 CORS 问题

## 联系支持

如果以上步骤都无法解决问题，请提供以下信息：
1. Netlify 站点 URL
2. 浏览器控制台的错误截图
3. API 测试页面的测试结果
4. 后端服务器的 IP 地址和状态

---

**最后更新**：2024-01-XX
**版本**：v1.0.1
