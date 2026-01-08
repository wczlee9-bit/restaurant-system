# 🚀 Netlify 快速开始指南

## ⚡ 三分钟快速部署

### 方法一：最快（手动上传）⏱️ 2分钟

1. **准备部署包**
   ```bash
   bash scripts/deploy_netlify.sh
   ```
   这会创建一个 `restaurant-system.zip` 文件

2. **上传到 Netlify**
   - 访问：https://app.netlify.com
   - 登录账号
   - 点击 "Add new site" → "Deploy manually"
   - 拖拽 `restaurant-system.zip` 文件到上传区域
   - 等待 1-2 分钟

3. **开始使用**
   - 访问 Netlify 提供的 URL（例如：`https://xxx.netlify.app`）
   - 开始测试！

---

### 方法二：推荐（Netlify CLI）⏱️ 5分钟

1. **安装 Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **登录 Netlify**
   ```bash
   netlify login
   ```

3. **部署**
   ```bash
   cd /workspace/projects
   bash scripts/deploy_netlify.sh
   ```
   按照提示操作，脚本会自动完成部署

---

### 方法三：Git 部署（适合持续更新）⏱️ 10分钟

1. **推送到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "Ready for Netlify"
   git remote add origin https://github.com/yourusername/restaurant.git
   git push -u origin main
   ```

2. **在 Netlify 中连接**
   - 访问：https://app.netlify.com
   - "Add new site" → "Import an existing project"
   - 选择 GitHub 仓库
   - 配置：
     - **Build command**: (留空)
     - **Publish directory**: `assets`
   - 点击 "Deploy site"

---

## 📋 部署后配置

### 1. 配置 API 地址（重要！）

部署到 Netlify 后，API 地址需要配置为云端地址：

在 `assets/restaurant_full_test.html` 中，确保 API 检测逻辑包含：

```javascript
const detectApiBase = () => {
    // 在 Netlify 环境中，使用云端API
    if (window.location.hostname.includes('netlify.app')) {
        return 'http://9.128.251.82:8000/api';  // 云端API
    }
    return 'http://localhost:8000/api';
};
```

### 2. 跨域问题（CORS）

如果遇到跨域错误，需要在后端 API 中添加 CORS 配置。

当前 API 服务已支持 CORS，应该可以直接使用。

---

## 🎯 快速测试清单

部署完成后，请测试以下功能：

- [ ] 访问主页，页面正常显示
- [ ] 选择桌号（8号桌）
- [ ] 浏览菜单
- [ ] 添加商品到购物车
- [ ] 提交订单
- [ ] 检查 API 请求成功
- [ ] 切换角色（顾客→厨师→传菜员→收银员→店长）
- [ ] 查看订单状态

---

## 🔍 常见问题速查

### Q: 部署后页面空白？
**A**: 检查浏览器控制台（F12），查看是否有 JS 错误或 API 请求失败

### Q: API 请求失败？
**A**: 
1. 确认云端 API 服务运行正常
2. 检查 API 地址配置
3. 查看是否有 CORS 错误

### Q: 图片无法加载？
**A**: 确认 `assets/qrcodes/` 目录已上传，且路径正确

### Q: 如何更新部署？
**A**: 
- 方法一：重新上传 zip 文件
- 方法二：执行 `netlify deploy --prod --dir=assets`
- 方法三：推送到 Git，自动触发部署

---

## 📚 详细文档

完整部署指南请查看：[NETLIFY_DEPLOY.md](NETLIFY_DEPLOY.md)

---

## 🎉 部署成功！

部署成功后，您将获得：

✅ 一个公开可访问的网站 URL  
✅ 自动 HTTPS 加密  
✅ 全球 CDN 加速  
✅ 手机、平板、电脑均可访问  
✅ 可以分享给他人测试  

现在您可以在任何设备上访问和测试系统了！

---

**祝您部署顺利！🚀**
