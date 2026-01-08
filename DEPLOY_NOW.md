# 🚀 快速部署到 Netlify

## 📦 部署文件已准备好！

部署文件位于：`deploy_temp/` 文件夹

---

## 🎯 方法一：拖拽部署（推荐，最简单）

### 步骤：
1. **访问 Netlify**
   - 打开浏览器访问：https://app.netlify.com/
   - 登录你的 Netlify 账号

2. **开始部署**
   - 点击 "Add new site" → "Deploy manually"
   - 找到项目中的 `deploy_temp` 文件夹
   - 将整个文件夹**拖拽**到页面上的虚线框中
   - 等待 1-2 分钟，部署完成！

3. **访问网站**
   - Netlify 会提供一个随机域名，例如：`https://tiny-sprite-65833c.netlify.app`
   - 点击网站名称查看部署状态

---

## 🔗 方法二：Git 集成部署（推荐用于持续更新）

### 步骤：
1. **推送到 GitHub**
   ```bash
   # 提交所有更改
   git add .
   git commit -m "fix: 修复订单提交失败并更新部署"
   git push origin main
   ```

2. **在 Netlify 连接 GitHub**
   - 访问 https://app.netlify.com/
   - 点击 "Add new site" → "Import an existing project"
   - 选择 "GitHub"，授权访问你的仓库
   - 选择你的仓库并点击 "Import"

3. **配置构建设置**
   - Build command: `echo 'No build needed'`
   - Publish directory: `assets`
   - 点击 "Deploy site"

---

## 📱 部署后的重要提示

### ⚠️ 前端已部署，但后端需要本地运行！

Netlify 只托管静态文件（HTML/CSS/JS），后端 API 服务需要在本地运行。

### 启动后端服务
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

### 🔌 启动 WebSocket 服务（实时通知）
```bash
# 在另一个终端窗口
python scripts/start_api_services.py
```

---

## 🧪 测试部署

### 1. 顾客端测试
访问：`https://YOUR-SITE.netlify.app/customer_order.html?table=8`

- 选择桌号
- 添加菜品到购物车
- 选择支付方式（马上支付/柜台支付）
- 提交订单

### 2. 工作人员端测试
访问：`https://YOUR-SITE.netlify.app/staff_workflow.html`

- 使用演示账号登录
- 切换角色（厨师/传菜员）
- 查看订单并打印

### 3. 门户入口
访问：`https://YOUR-SITE.netlify.app/portal.html`

---

## 🔧 常见问题

### Q: 订单提交失败？
A: 确保本地后端服务正在运行（端口 8000）

### Q: WebSocket 连接失败？
A: 确保 WebSocket 服务正在运行（端口 8001）

### Q: 如何更新网站？
A:
- 方法一（拖拽）：修改文件后，重新将 `deploy_temp` 文件夹拖拽到 Netlify
- 方法二（Git）：提交代码推送到 GitHub，Netlify 会自动部署

---

## 📚 文档链接

- 📘 详细部署指南：[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- 🎮 功能测试指南：[QUICK_TEST_GUIDE.md](assets/QUICK_TEST_GUIDE.md)
- 📖 系统说明：[README.md](README.md)

---

## ✅ 部署检查清单

- [ ] `deploy_temp` 文件夹已准备
- [ ] Netlify 账号已登录
- [ ] 拖拽部署完成
- [ ] 后端服务已启动（端口 8000）
- [ ] WebSocket 服务已启动（端口 8001）
- [ ] 顾客端测试通过
- [ ] 工作人员端测试通过

---

**🎉 恭喜！你已成功部署餐饮系统！**

**📞 遇到问题？** 查看详细文档或检查浏览器控制台错误信息
