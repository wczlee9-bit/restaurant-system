# 演示账号已更新

## ✅ 账号已统一

我已经统一了所有页面的演示账号配置，确保 `portal.html` 和 `login_standalone.html` 使用相同的账号。

---

## 🔐 正确的演示账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 👑 系统管理员 | system_admin | admin123 |
| 🏢 总公司 | company | company123 |
| 👔 店长 | admin | admin123 |
| 👨‍🍳 厨师 | chef | chef123 |
| 🤵 传菜员 | waiter | waiter123 |
| 💰 收银员 | cashier | cashier123 |

---

## 📋 重要说明

### 账号角色说明

**system_admin（系统管理员）**
- 最高权限
- 可以管理系统所有功能
- 查看所有店铺和订单数据

**company（总公司）**
- 可以查看多个店铺的运营数据
- 跨店铺管理功能

**admin（店长）**
- 管理单个店铺
- 查看本店订单和营收
- 管理工作人员

**chef（厨师）**
- 查看待制作订单
- 开始制作和完成制作

**waiter（传菜员）**
- 查看待传菜品
- 确认上菜

**cashier（收银员）**
- 查看待支付订单
- 处理支付

---

## 🚀 测试账号功能

### 测试 1：系统管理员登录
1. 访问：https://benevolent-bonbon-80328f.netlify.app/login_standalone.html
2. 使用账号：system_admin / admin123
3. 应该能成功登录

### 测试 2：总公司登录
1. 访问：https://benevolent-bonbon-80328f.netlify.app/login_standalone.html
2. 使用账号：company / company123
3. 应该能成功登录

### 测试 3：店长登录
1. 访问：https://benevolent-bonbon-80328f.netlify.app/login_standalone.html
2. 使用账号：admin / admin123
3. 应该能成功登录并查看店长界面

### 测试 4：其他角色
1. 访问登录页面
2. 分别使用 chef、waiter、cashier 账号登录
3. 查看不同角色对应的界面

---

## ⚠️ 需要重新部署吗？

**如果你还没有重新部署**：
- 是的，需要重新部署才能看到更新的账号配置

**如果你已经重新部署过**：
- 可能需要清除浏览器缓存
- 或使用 Ctrl+F5 强制刷新页面

---

## 🔄 如何重新部署

1. 访问 GitHub：https://github.com/wczlee9-bit/restaurant-system
2. 重新下载 ZIP 文件（删除旧的）
3. 解压文件
4. 在 Netlify 上拖拽 `assets` 文件夹
5. 等待 1-2 分钟部署完成

---

## 📞 账号登录问题排查

### 问题：提示"用户名或密码错误"

**解决方法**：
1. 检查用户名和密码是否拼写正确
2. 确认使用的是新的账号（不是旧账号）
3. 清除浏览器缓存后重试

### 问题：登录后界面不对

**解决方法**：
1. 退出登录
2. 重新登录，确认账号正确
3. 检查角色是否正确

### 问题：页面加载慢或无法加载

**解决方法**：
1. 检查网络连接
2. 清除浏览器缓存
3. 使用无痕模式访问

---

## 🎯 快速访问

**主门户页面**：
https://benevolent-bonbon-80328f.netlify.app/portal.html

**登录页面**：
https://benevolent-bonbon-80328f.netlify.app/login_standalone.html

**工作人员端**：
https://benevolent-bonbon-80328f.netlify.app/staff_workflow.html

---

**更新时间**：2025-01-08
