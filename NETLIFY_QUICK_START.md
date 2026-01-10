# ⚡ Netlify 快速部署（3步完成）

## 🚀 步骤1：登录并连接GitHub

1. 访问 **https://app.netlify.com**
2. 点击 **"Sign in with GitHub"** 登录
3. 点击 **"Add new site"** → **"Import an existing project"**
4. 点击 **"GitHub"** 图标
5. 选择仓库：**`wczlee9-bit/restaurant-system`**
6. 点击 **"Import site"**

---

## ⚙️ 步骤2：配置构建设置 ⚠️ 重要！

| 配置项 | 填写值 |
|-------|--------|
| **Build command** | 留空（不填） |
| **Publish directory** | `assets` ← **必须是这个！** |
| **Branch to deploy** | `main` |

---

## ✅ 步骤3：部署并访问

1. 点击 **"Deploy site"** 按钮
2. 等待1-3分钟
3. 看到绿色 ✅ 表示部署成功
4. 访问你的网站！

**你的网站地址：**
```
https://your-site-name.netlify.app/portal.html
```

---

## 🌐 所有功能页面

| 功能 | URL |
|-----|-----|
| 🏠 门户首页 | `/portal.html` |
| 👤 顾客点餐 | `/customer_order_v3.html` |
| 🏪 工作人员登录 | `/login_standalone.html` |
| 👥 会员中心 | `/member_center.html` |
| 🏢 总公司后台 | `/headquarters_dashboard.html` |
| 🎁 优惠管理 | `/discount_management.html` |

---

## ⚠️ 重要提醒

**确保后端API服务运行在 115.191.1.219 服务器上**

测试API连接：
```bash
curl http://115.191.1.219:8000/api/health
curl http://115.191.1.219:8001/api/health
curl http://115.191.1.219:8004/api/health
curl http://115.191.1.219:8006/api/health
curl http://115.191.1.219:8007/api/health
```

如果API失败，需要在后端配置CORS：
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ✅ 部署后验证

- [ ] 访问主页成功
- [ ] 页面样式正常
- [ ] 可以点餐下单
- [ ] API请求成功
- [ ] 工作人员可以登录
- [ ] 会员中心正常
- [ ] 总公司后台正常

---

**详细教程**：查看 `NETLIFY_FINAL_DEPLOYMENT.md`

**开始部署吧！** 🚀
