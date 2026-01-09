# 餐饮点餐系统 - 生产环境部署指南

## 📋 系统概览

多店铺扫码点餐系统，支持：
- ✅ 顾客扫码点餐（支持菜品图片、优惠应用）
- ✅ 会员系统（积分、等级、会员二维码）
- ✅ 工作人员管理（店长、厨师、传菜员、收银员）
- ✅ 优惠配置系统（百分比、固定金额、积分抵扣）
- ✅ 跨店铺结算与第三方积分互通
- ✅ 总公司管理后台

## 🔧 系统架构

### 前端（Netlify）
- 静态HTML + Vue 3 + Element Plus
- 所有页面在 `assets/` 目录
- 通过 Netlify CDN 全球加速

### 后端API服务
| 服务 | 端口 | 功能 |
|------|------|------|
| restaurant_api | 8000 | 餐饮系统完整API（订单、菜单、桌号、WebSocket） |
| member_api | 8004 | 会员API（积分、订单查询） |
| headquarters_api | 8006 | 总公司管理API |
| restaurant_enhanced_api | 8007 | 增强API（菜品图片、会员二维码、优惠系统） |

### 数据库
- PostgreSQL
- S3 对象存储（图片、二维码）

## 📦 部署步骤

### 1. 数据库初始化

```bash
# 运行所有数据库迁移
cd /workspace/projects
python scripts/migrate_add_discount_and_qrcode.py
```

### 2. 启动后端API服务

```bash
# 启动所有API服务
cd /workspace/projects
python scripts/start_api_services.py
```

服务将在以下端口启动：
- http://115.191.1.219:8000 - 餐饮系统API
- http://115.191.1.219:8004 - 会员API
- http://115.191.1.219:8006 - 总公司管理API
- http://115.191.1.219:8007 - 增强API

### 3. 部署到Netlify

#### 方法一：拖拽部署（推荐）

1. 打开 [Netlify Dashboard](https://app.netlify.com/)
2. 登录你的账户
3. 点击 "Add new site" → "Deploy manually"
4. 将 `assets/` 目录中的所有文件拖拽到上传区域
5. 上传完成后，将 `netlify.toml` 文件也拖拽到相同位置
6. 等待部署完成（通常 1-2 分钟）

#### 方法二：Git集成部署

1. 将代码推送到GitHub
2. 在Netlify中连接GitHub仓库
3. 配置构建设置：
   - Build command: `# No build command`
   - Publish directory: `assets`
4. 点击 "Deploy site"

### 4. 配置API代理

Netlify会自动使用 `netlify.toml` 中的配置，将前端请求代理到后端服务器。

如果需要修改后端服务器地址，编辑 `netlify.toml` 中的 `to` 字段：
```toml
[[redirects]]
  from = "/api/*"
  to = "http://YOUR_SERVER_IP:8000/api/:splat"  # 修改为你的服务器IP
  status = 200
  force = true
```

### 5. 配置自定义域名（可选）

1. 在Netlify Site Settings中，点击 "Domain management"
2. 点击 "Add custom domain"
3. 输入你的域名
4. 按照Netlify的指引配置DNS记录

### 6. 启用HTTPS（自动）

Netlify会自动为所有站点提供HTTPS证书，无需额外配置。

## 🔐 安全配置

### 1. 环境变量

确保以下环境变量已设置：
- `COZE_BUCKET_ENDPOINT_URL` - S3对象存储端点
- `COZE_BUCKET_NAME` - S3存储桶名称
- `DATABASE_URL` - PostgreSQL数据库连接字符串

### 2. 防火墙规则

确保服务器防火墙允许以下端口：
- 8000, 8004, 8006, 8007 - API服务端口
- 5432 - PostgreSQL数据库（仅限本地访问）

## ✅ 部署验证

部署完成后，访问以下URL验证系统：

1. **门户页面**：`https://your-site.netlify.app/`
2. **顾客点餐**：`https://your-site.netlify.app/customer_order_v3.html?table=1`
3. **工作人员登录**：`https://your-site.netlify.app/login_standalone.html`
4. **会员中心**：`https://your-site.netlify.app/member_center.html`
5. **优惠管理**：`https://your-site.netlify.app/discount_management.html`

## 🎯 功能测试

### 1. 顾客点餐流程
1. 扫描桌号二维码（或手动输入桌号）
2. 选择菜品（支持图片预览）
3. 查看应用优惠后的价格
4. 确认下单
5. 选择支付方式（马上支付/柜台支付）
6. 查看订单状态实时更新

### 2. 会员功能
1. 登录会员中心
2. 查看会员二维码
3. 扫描二维码验证会员身份
4. 查看积分和订单记录

### 3. 优惠系统
1. 店长登录优惠管理页面
2. 创建优惠配置（百分比/固定金额/积分抵扣）
3. 在点餐时应用优惠
4. 验证优惠计算正确

### 4. 菜品图片上传
1. 进入菜品管理页面
2. 选择菜品并上传图片
3. 在顾客端查看菜品图片

## 📊 性能优化

1. **CDN加速**：Netlify自动提供全球CDN加速
2. **图片压缩**：上传前压缩图片，建议：
   - 宽度：800px - 1200px
   - 格式：JPEG (质量 85%) 或 WebP
   - 大小：< 300KB
3. **API响应时间**：优化数据库查询，添加索引

## 🔄 更新部署

当需要更新系统时：

1. 更新代码
2. 拖拽新的 `assets/` 文件到Netlify
3. 拖拽新的 `netlify.toml` 文件
4. 等待部署完成

## 📞 技术支持

如有问题，请检查：
1. 后端API服务是否正常运行
2. 数据库连接是否正常
3. Netlify部署日志
4. 浏览器控制台错误信息

## 📝 更新日志

### v2.0.0 (2024-01-15)
- ✨ 新增菜品图片上传功能
- ✨ 新增会员二维码生成
- ✨ 新增优惠配置系统
- ✨ 优化会员中心界面
- ✨ 支持多种优惠类型（百分比、固定金额、积分抵扣）
- 🐛 修复订单流程问题
- 📚 更新部署文档
