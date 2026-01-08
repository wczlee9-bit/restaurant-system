# 🚀 餐饮点餐系统 - 立即部署指南

## ✅ 当前状态

### 后端服务
- **数据库**: ✅ 已连接（PostgreSQL 17.5）
- **API服务**: ✅ 全部运行中
  - 顾客端API: 8000
  - 店员端API: 8001
  - 会员API: 8004
  - 总公司API: 8006
- **服务器IP**: 115.191.1.219

### 前端部署
- **配置文件**: ✅ 已更新（netlify.toml）
- **API代理**: ✅ 已配置（指向115.191.1.219）
- **部署文件**: ✅ 已准备（assets/目录）

---

## ⚡ 3步部署到 Netlify

### 第1步：准备部署文件

```bash
cd /workspace/projects
zip -r restaurant-system.zip assets/ netlify.toml
```

### 第2步：上传到 Netlify

1. 访问：https://app.netlify.com/drop
2. 将 `restaurant-system.zip` 拖拽到页面
3. 等待 1-2 分钟，部署完成！

### 第3步：测试访问

获得 Netlify 域名后，访问以下地址测试：

| 功能 | URL示例 |
|------|---------|
| 门户首页 | `https://your-site.netlify.app/` |
| 顾客点餐 | `https://your-site.netlify.app/customer-order` |
| 工作人员端 | `https://your-site.netlify.app/staff-workflow` |
| 会员中心 | `https://your-site.netlify.app/member-center` |
| 总公司后台 | `https://your-site.netlify.app/headquarters` |

---

## ⚠️ 重要：确保端口开放

在部署前，请确认以下端口已对外开放：

```bash
# 检查端口是否开放
netstat -tlnp | grep -E ":(8000|8001|8004|8006)"

# 如果使用云服务商（阿里云、腾讯云、AWS等），请：
# 1. 登录控制台
# 2. 进入安全组/防火墙规则
# 3. 添加入站规则，开放端口 8000, 8001, 8004, 8006
# 4. 协议：TCP
# 5. 来源：0.0.0.0/0
```

---

## 🧪 快速测试

### 测试后端API

```bash
# 测试顾客端API
curl http://115.191.1.219:8000/

# 预期返回：
# {
#   "message": "扫码点餐系统 - 顾客端 API",
#   "version": "1.0.0",
#   ...
# }
```

### 测试前端访问

访问您的 Netlify 站点，检查：
- [ ] 页面正常加载
- [ ] 可以浏览菜单
- [ ] 可以选择桌号
- [ ] API请求成功（检查浏览器控制台）

---

## 🔧 故障排除

### 问题：前端无法连接后端

**检查清单**：
1. 确认后端服务正在运行
2. 确认端口已对外开放（从外部测试：`curl http://115.191.1.219:8000/`）
3. 检查防火墙/安全组规则
4. 查看浏览器控制台错误信息

### 问题：CORS 错误

**解决方案**：后端已配置CORS，如果仍有问题，检查浏览器控制台。

### 问题：404 错误

**解决方案**：确认 `netlify.toml` 文件已上传到 Netlify，检查重定向规则。

---

## 📚 详细文档

如需了解更多信息，请参考：

- 📘 [完整部署指南](NETLIFY_DEPLOYMENT_CURRENT.md)
- 📗 [系统使用手册](USER_MANUAL.md)
- 📖 [商用部署文档](COMMERCIAL_DEPLOYMENT.md)

---

## 💡 提示

1. **首次部署**：建议使用拖拽部署，最快最简单
2. **持续更新**：建议使用Git集成，推送代码自动部署
3. **自定义域名**：部署后可在Netlify配置自定义域名
4. **HTTPS**：Netlify自动提供HTTPS证书

---

## 📞 需要帮助？

如果遇到问题：
- 检查 [完整部署指南](NETLIFY_DEPLOYMENT_CURRENT.md) 的故障排除章节
- 查看Netlify部署日志（Dashboard → Deploys）
- 检查后端服务日志

---

**开始部署吧！** 🎉
