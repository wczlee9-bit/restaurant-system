# 重新部署指南

## 📢 为什么需要重新部署？

我已经添加了新的门户页面 `portal.html`，它提供了更好的导航和角色区分功能。你需要重新部署才能使用新功能。

---

## 🚀 重新部署步骤（2分钟）

### 步骤 1: 重新下载 GitHub 仓库

1. **访问 GitHub 仓库**：
   👉 https://github.com/wczlee9-bit/restaurant-system

2. **删除旧的下载**：
   - 删除之前下载的 ZIP 文件和解压后的文件夹

3. **重新下载**：
   - 点击绿色的 "Code" 按钮
   - 点击 "Download ZIP"

4. **解压新文件**

---

### 步骤 2: 在 Netlify 上重新部署

1. **访问你的 Netlify 项目**：
   👉 https://app.netlify.com/sites/benevolent-bonbon-80328f

2. **找到拖拽区域**：
   - 在页面上找到 "Drag and drop your project folder here"
   - 或 "Or, browse to upload"

3. **重新拖拽 `assets` 文件夹**：
   - 从新解压的文件夹中找到 `assets` 文件夹
   - 拖拽到 Netlify 的拖拽区域

4. **等待部署完成**（1-2 分钟）

---

### 步骤 3: 测试新功能

部署成功后，访问：

**新的主门户页面**：
👉 https://benevolent-bonbon-80328f.netlify.app/portal.html

**在新门户页面上，你可以**：
- ✅ 点击"顾客端"选择桌号点餐
- ✅ 点击"工作人员端"登录（不同角色看到不同界面）
- ✅ 点击"店铺设置"管理桌号
- ✅ 点击"测试系统"进入完整测试

**演示账号**（在门户页面底部）：
- 系统管理员：admin / admin123
- 总公司：headquarters / hq123456
- 店长：manager / manager123
- 厨师：chef / chef123
- 传菜员：waiter / waiter123
- 收银员：cashier / cashier123

---

## 🎯 新功能说明

### 1. 主门户页面（portal.html）
- 清晰的四大入口：顾客端、工作人员端、店铺设置、测试系统
- 快速桌号选择
- 演示账号列表（无需记忆）

### 2. 角色区分
- **店长**：查看所有订单、管理桌位、营收数据
- **厨师**：制作订单、完成制作
- **传菜员**：确认上菜、上菜完成
- **收银员**：处理支付、打印小票

### 3. 修复的问题
- ✅ 点击8号桌现在可以正确跳转到点餐页面
- ✅ 不同角色登录后看到对应的界面
- ✅ 提供了统一的门户入口

---

## 📋 完整文件列表

重新部署后，你的站点将包含以下文件：
- ✅ portal.html（新）- 主门户页面
- ✅ customer_order.html - 顾客点餐页面
- ✅ login_standalone.html - 工作人员登录页面
- ✅ staff_workflow.html - 工作人员端（多角色）
- ✅ shop_settings.html - 店铺设置页面
- ✅ index.html - 原始测试页面
- ✅ restaurant_full_test.html - 完整测试系统
- ✅ ... 其他测试和文档文件

---

## 💡 提示

1. **从 portal.html 开始**：
   - 这是新的主入口，所有功能都可以从这里访问

2. **测试不同角色**：
   - 使用不同的演示账号登录
   - 查看每个角色对应的界面和功能

3. **测试点餐流程**：
   - 在门户页面选择8号桌
   - 测试完整的点餐→制作→传菜→结账流程

---

**现在就重新部署吧！大约需要 2 分钟！** 🚀

完成后访问：https://benevolent-bonbon-80328f.netlify.app/portal.html
