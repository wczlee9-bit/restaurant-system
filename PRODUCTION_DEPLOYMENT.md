# 🚀 正式上线部署指南

## 📋 部署概述

本指南将帮助你将餐饮点餐系统正式部署到 Netlify 生产环境。

---

## ✅ 已修复的问题

### 1. 顾客支付确认流程 ✅
- ✅ 实现两步结算流程（确认订单→选择支付方式）
- ✅ 支持两种支付方式：
  - 💳 **马上支付**（immediate）- 在线支付
  - 🏪 **柜台支付**（counter）- 饭后结账
- ✅ 文件：`assets/customer_order_v3.html`

### 2. 提交订单失败 ✅
- ✅ 增强错误日志输出
- ✅ 优化错误提示信息
- ✅ 检查 API 数据格式
- ✅ 文件：`assets/customer_order_v3.html`

### 3. 二维码打印功能 ✅
- ✅ 修复打印窗口弹窗问题
- ✅ 增加打印按钮（用户手动触发）
- ✅ 优化打印样式（A4 纸张适配）
- ✅ 支持批量打印
- ✅ 说明：`assets/shop_settings_v2.html`

### 4. 生产环境配置 ✅
- ✅ 创建生产环境配置文件
- ✅ 优化缓存策略
- ✅ 配置安全头部
- ✅ 文件：`netlify-production.toml`

---

## 📦 正式部署包文件清单

### 核心文件（必须上传）

| 文件名 | 大小 | 用途 | 说明 |
|--------|------|------|------|
| **portal.html** | 8.5K | 主门户页面 | 四大功能入口 |
| **index.html** | 12K | 默认首页 | 备用入口 |
| **login_standalone.html** | 16K | 工作人员登录 | 独立登录页面 |
| **customer_order_v3.html** | 32K | 顾客点餐（新版） | ⭐ 生产版，包含所有修复 |
| **staff_workflow.html** | 51K | 工作人员端 | 多角色管理 |
| **shop_settings.html** | 53K | 店铺设置 | 桌号、二维码管理 |
| **api_test.html** | 14K | API 测试工具 | 验证后端连接 |
| **test.html** | 469B | 基础测试页面 | 部署验证 |

### 配置文件（必须上传）

| 文件名 | 用途 | 说明 |
|--------|------|------|
| **netlify-production.toml** | 生产环境配置 | ⭐ 正式环境专用 |

### 可选文件（根据需要上传）

| 文件名 | 大小 | 用途 |
|--------|------|------|
| menu_management.html | 28K | 菜品管理 |
| inventory_management.html | 40K | 库存管理 |
| order_flow_config.html | 23K | 订单流程配置 |

### 不要上传的文件

- ❌ 所有 `.bak` 备份文件
- ❌ 所有 `.md` 文档文件（本地参考用）
- ❌ `*.html.bak` 文件
- ❌ `shop_settings_v2.html`（仅作为参考）
- ❌ `customer_order.html`（旧版，已被 v3 替代）
- ❌ `customer_order_v2.html`（旧版，已被 v3 替代）

---

## 🚀 部署步骤（5分钟）

### 第1步：准备部署文件

**方式A：从 GitHub 下载（推荐）**

1. 访问：https://github.com/wczlee9-bit/restaurant-system
2. 点击绿色的 "Code" 按钮
3. 点击 "Download ZIP"
4. 解压到本地

**方式B：使用本地项目**

直接使用 `/workspace/projects/assets/` 目录下的文件

---

### 第2步：选择文件并重命名配置

1. **打开 `assets` 文件夹**

2. **选中以下 8 个核心文件：**
   ```
   ✓ portal.html
   ✓ index.html
   ✓ login_standalone.html
   ✓ customer_order_v3.html
   ✓ staff_workflow.html
   ✓ shop_settings.html
   ✓ api_test.html
   ✓ test.html
   ```

3. **重命名配置文件：**
   - 将 `netlify-production.toml` 重命名为 `netlify.toml`

---

### 第3步：上传到 Netlify

**1. 创建新站点**
- 访问：https://app.netlify.com
- 点击 "Add new site" → "Deploy manually"

**2. 拖拽上传**
- 同时拖拽选中的 8 个 HTML 文件
- 同时拖拽 `netlify.toml` 配置文件
- 等待 1-2 分钟完成部署

**3. 记下域名**
- 部署成功后，Netlify 会提供一个随机域名
- 例如：`https://your-site-name.netlify.app`

---

### 第4步：配置 API 地址（重要！）

**1. 修改 `netlify.toml` 中的 API 地址**

找到以下部分并修改为实际的后端地址：

```toml
# 订单相关接口代理到 customer_api
[[redirects]]
  from = "/api/orders*"
  to = "http://YOUR_BACKEND_IP:8001/api/orders:splat"
  status = 200
  force = true

# WebSocket 代理
[[redirects]]
  from = "/ws/*"
  to = "http://YOUR_BACKEND_IP:8001/ws/:splat"
  status = 200
  force = true

# 其他 API 接口代理到 restaurant_api
[[redirects]]
  from = "/api/*"
  to = "http://YOUR_BACKEND_IP:8000/api/:splat"
  status = 200
  force = true
```

**2. 重新上传 `netlify.toml`**
- 修改完成后，重新上传到 Netlify
- 或在 Netlify Dashboard 中直接编辑文件

---

### 第5步：测试验证

**测试清单：**

1. **基础部署测试**
   ```
   访问：https://your-site.netlify.app/test.html
   预期：显示 "✅ 部署成功！"
   ```

2. **门户页面测试**
   ```
   访问：https://your-site.netlify.app/portal.html
   预期：显示四大功能入口
   ```

3. **顾客点餐测试**
   ```
   访问：https://your-site.netlify.app/customer_order_v3.html
   测试：
   - 选择桌号
   - 添加菜品到购物车
   - 点击去结算
   - 确认订单（步骤1）
   - 选择支付方式（步骤2）
   - 提交订单
   预期：订单提交成功，显示订单号
   ```

4. **工作人员端测试**
   ```
   访问：https://your-site.netlify.app/staff_workflow.html
   测试：
   - 登录（使用演示账号）
   - 查看订单
   - 接单
   - 处理订单
   预期：订单状态实时更新
   ```

5. **API 连接测试**
   ```
   访问：https://your-site.netlify.app/api_test.html
   测试：
   - 测试 API 连接
   - 查看 API 响应
   预期：所有 API 测试通过
   ```

---

## 🎯 功能测试清单

### 顾客端测试

- [ ] 扫码后自动识别桌号
- [ ] 菜品分类显示正常
- [ ] 添加菜品到购物车
- [ ] 修改购物车数量
- [ ] 结算步骤1：确认订单
- [ ] 结算步骤2：选择支付方式
- [ ] 支付方式：马上支付
- [ ] 支付方式：柜台支付
- [ ] 提交订单成功
- [ ] 显示订单号
- [ ] 订单状态实时更新

### 工作人员端测试

- [ ] 登录功能正常
- [ ] 角色切换（店长、厨师、传菜员、收银员）
- [ ] 接收新订单通知
- [ ] 查看订单详情
- [ ] 更新订单状态
- [ ] 打印订单小票

### 店铺设置测试

- [ ] 店铺信息配置
- [ ] 添加/删除桌号
- [ ] 生成桌号二维码
- [ ] 自定义二维码颜色
- [ ] 添加 Logo
- [ ] 打印二维码（单个）
- [ ] 批量打印二维码
- [ ] 配置支付方式

---

## 🔧 后端服务要求

### 必须启动的服务

**1. 餐厅管理 API (restaurant_api)**
```bash
cd /workspace/projects
python -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000
```
- 地址：`http://YOUR_IP:8000`
- 文档：`http://YOUR_IP:8000/docs`

**2. 顾客订单 API (customer_api)**
```bash
cd /workspace/projects
python -m uvicorn src.api.customer_api:app --host 0.0.0.0 --port 8001
```
- 地址：`http://YOUR_IP:8001`
- 文档：`http://YOUR_IP:8001/docs`

**3. WebSocket 服务**（已集成在 customer_api 中）
- 地址：`ws://YOUR_IP:8001/ws/orders/table/{table_id}`

---

## 🔒 安全建议

### 生产环境安全配置

1. **CORS 配置**
   - 在后端 API 中配置允许的域名
   - 限制跨域访问

2. **API 认证**
   - 添加 API Key 验证
   - 使用 JWT Token

3. **HTTPS 强制**
   - Netlify 已自动配置 HTTPS
   - 确保 API 地址使用 HTTPS

4. **防火墙规则**
   - 限制 API 端口访问
   - 使用安全组规则

5. **数据备份**
   - 定期备份数据库
   - 配置自动备份策略

---

## 📊 性能优化

### 已实施的优化

1. ✅ 静态资源 CDN 加速
2. ✅ 图片自动压缩
3. ✅ 长期缓存策略（JS/CSS）
4. ✅ 不缓存 HTML 文件（确保最新版本）

### 额外建议

1. 使用自定义域名（提升品牌形象）
2. 配置 CDN 边缘节点
3. 启用 Gzip 压缩
4. 优化图片格式（WebP）

---

## 🆘 常见问题

### Q1: 提交订单失败？

**A: 检查以下几点：**
1. 后端服务是否启动（端口 8000/8001）
2. `netlify.toml` 中的 API 地址是否正确
3. 浏览器控制台是否有错误信息（F12）
4. 使用 `api_test.html` 测试 API 连接

### Q2: 订单状态不更新？

**A: 检查 WebSocket：**
1. WebSocket 服务是否启动
2. 浏览器控制台查看 WebSocket 连接状态
3. 防火墙是否允许 WebSocket 连接

### Q3: 打印二维码不工作？

**A: 解决方案：**
1. 允许浏览器弹出窗口
2. 确保二维码图片已生成
3. 使用 Chrome/Edge 浏览器（最佳兼容性）

### Q4: 支付方式不显示？

**A: 检查配置：**
1. 在店铺设置中配置支付方式
2. 清除浏览器缓存
3. 检查 localStorage 中的 shopInfo

---

## 📞 技术支持

### 遇到问题？

1. **查看日志**
   - Netlify Dashboard → Deploys → Deploy log
   - 浏览器控制台（F12）

2. **测试工具**
   - 使用 `api_test.html` 测试 API
   - 使用 `test.html` 验证基础部署

3. **参考文档**
   - `NETLIFY_DEPLOY.md`
   - `DEPLOYMENT_GUIDE.md`

---

## ✅ 部署完成检查清单

部署完成后，请确认：

- [ ] 所有文件上传成功
- [ ] `test.html` 显示 "✅ 部署成功！"
- [ ] `portal.html` 正常访问
- [ ] 顾客点餐流程完整测试通过
- [ ] 工作人员端功能正常
- [ ] 订单状态实时更新
- [ ] 二维码打印功能正常
- [ ] API 连接测试通过
- [ ] 后端服务正常运行
- [ ] WebSocket 连接正常

---

## 🎉 部署成功！

恭喜！你的餐饮点餐系统已经成功部署到生产环境！

**下一步：**
1. 配置自定义域名（可选）
2. 设置监控和日志
3. 培训工作人员使用系统
4. 开始正式营业！

**祝生意兴隆！** 🍽️
