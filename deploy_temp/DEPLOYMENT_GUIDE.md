# 🚀 更新部署指南

## 📋 更新内容

### 本次修复
- ✅ **修复顾客端订单提交失败问题**
  - 启用后端 API 调用（`http://localhost:8000/api/orders/`）
  - 移除仅使用 localStorage 的模拟逻辑
  - 支持两种支付方式：马上支付（immediate）、柜台支付（counter）
  - 订单号由后端自动生成（格式：ORD + 时间戳 + 随机数）

### 已部署功能
- 📱 顾客端：扫码点餐、购物车、订单提交、实时状态更新
- 👨‍🍳 工作人员端：厨师单打印、传菜员单打印、订单状态管理
- 🏪 店铺管理：桌号管理、二维码生成、菜品管理
- 🔐 登录系统：中英文双语、多种角色支持

---

## 🌐 部署到 Netlify

### 方法一：拖拽部署（推荐，最简单）

1. **准备文件**
   ```bash
   # 进入项目目录
   cd /workspace/projects

   # 确认 assets 目录包含所有前端文件
   ls assets/*.html
   ```

2. **创建部署包**
   ```bash
   # 创建临时部署目录
   mkdir -p deploy_temp

   # 复制必要文件
   cp -r assets deploy_temp/

   # 复制 Netlify 配置
   cp netlify.toml deploy_temp/
   ```

3. **手动部署到 Netlify**
   - 访问 [Netlify App](https://app.netlify.com/)
   - 登录你的账号
   - 点击 "Add new site" → "Deploy manually"
   - 将 `deploy_temp` 文件夹**拖拽**到上传区域
   - 等待部署完成（约 1-2 分钟）

4. **访问部署后的网站**
   - Netlify 会提供一个随机域名，例如：`https://tiny-sprite-65833c.netlify.app`
   - 你可以在 "Site settings" → "Change site name" 中修改为自定义域名

---

### 方法二：Git 集成部署

1. **推送到 GitHub**
   ```bash
   # 初始化 Git（如果还没有）
   git init

   # 添加所有文件
   git add .

   # 提交更改
   git commit -m "fix: 修复订单提交失败并更新部署"

   # 推送到 GitHub
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **在 Netlify 中连接 GitHub**
   - 访问 [Netlify App](https://app.netlify.com/)
   - 点击 "Add new site" → "Import an existing project"
   - 选择你的 GitHub 仓库
   - 配置部署设置：
     - Build command: `echo 'No build needed'`
     - Publish directory: `assets`
   - 点击 "Deploy site"

---

## 🔧 本地后端服务启动

部署后，前端会尝试连接 `http://localhost:8000` 的 API 服务。你需要：

### 启动后端 API 服务
```bash
# 进入项目目录
cd /workspace/projects

# 启动餐饮系统 API 服务
python scripts/start_restaurant_api.py
```

服务信息：
- 🌐 API 地址: http://localhost:8000
- 📚 API 文档: http://localhost:8000/docs
- 💚 健康检查: http://localhost:8000/health

### 启动 WebSocket 服务（用于实时通知）
```bash
# 在另一个终端窗口启动 WebSocket 服务
python scripts/start_api_services.py
```

---

## 📱 使用说明

### 顾客端
1. **访问网站**
   - 打开部署后的 Netlify 域名
   - 例如：https://tiny-sprite-65833c.netlify.app

2. **扫码点餐流程**
   - 访问 `customer_order.html?table=8` （8号桌，可修改为其他桌号）
   - 或通过门户页面 `portal.html` 进入
   - 选择菜品，添加到购物车
   - 选择支付方式（马上支付/柜台支付）
   - 提交订单

3. **订单状态跟踪**
   - 页面会实时显示订单状态（制作中 → 待传菜 → 上菜中 → 已完成）
   - 通过 WebSocket 接收实时更新

### 工作人员端
1. **登录**
   - 访问 `staff_workflow.html`
   - 使用登录页面账号登录（已隐藏，可在代码中查看）

2. **角色切换**
   - 登录后可选择角色：店长、厨师、传菜员、收银员

3. **订单打印**
   - 厨师：打印厨师单（包含桌号、订单号、菜品清单、备注）
   - 传菜员：打印传菜员单（包含桌号、订单号、菜品清单、金额、支付状态、备注）

---

## 🔍 故障排查

### 订单提交失败
- ✅ 已修复：API 调用已启用
- 确保后端服务运行在 `http://localhost:8000`
- 检查浏览器控制台是否有网络错误

### WebSocket 连接失败
- 确保WebSocket服务运行在 `http://localhost:8001`
- 检查防火墙设置

### 订单状态不更新
- 刷新页面重新连接WebSocket
- 检查后端WebSocket服务是否正常运行

---

## 📊 功能清单

### ✅ 已实现
- [x] 顾客端扫码点餐
- [x] 购物车管理
- [x] 订单提交（支持两种支付方式）
- [x] 订单号自动生成
- [x] 实时订单状态更新（WebSocket）
- [x] 厨师单打印
- [x] 传菜员单打印
- [x] 中英文双语登录
- [x] 多角色权限管理
- [x] 桌号管理
- [x] 菜品管理
- [x] 二维码生成

### 🔄 待优化
- [ ] 支付接口集成（微信/支付宝）
- [ ] 会员积分系统
- [ ] 营收数据统计
- [ ] 移动端响应式优化

---

## 📞 技术支持

如遇到问题，请检查：
1. 后端服务是否正常运行
2. 浏览器控制台是否有错误信息
3. API 地址是否正确（默认：http://localhost:8000）

---

## 📅 更新日志

### 2024-01-08
- ✅ 修复顾客端订单提交失败问题
- ✅ 启用后端 API 调用
- ✅ 支持马上支付和柜台支付
- ✅ 实现双订单打印功能
- ✅ 订单号自动生成（日期+时间+随机数）

---

**部署完成后，记得启动后端服务才能正常使用所有功能！** 🚀
