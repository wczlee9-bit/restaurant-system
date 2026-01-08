# 🔧 登录问题故障排查指南

## 问题现象
登录功能无法使用，需要排查原因。

---

## 🚀 快速测试方案

### 方案 1: 使用简化测试页面（推荐）

访问简化的测试页面，无需依赖 Vue 和 ElementPlus：

```
http://localhost:8080/test_login.html
```

**测试步骤：**
1. 打开上述链接
2. 点击任意测试账号卡片（如 👑 系统管理员）
3. 用户名和密码会自动填充
4. 点击"🔑 测试登录"按钮
5. 查看下方的测试日志和结果

**如果测试页面可以登录，说明：**
- ✅ 配置文件正常
- ✅ 服务器正常
- ❌ 原始登录页面的 Vue 或 ElementPlus 加载有问题

---

### 方案 2: 检查浏览器控制台

1. 打开登录页面：`http://localhost:8080/login.html`
2. 按 `F12` 打开浏览器开发者工具
3. 切换到 `Console`（控制台）标签
4. 查看是否有红色错误信息

**常见错误及解决方法：**

#### 错误 1: Vue is not defined
```
Uncaught ReferenceError: Vue is not defined
```
**原因：** Vue 库未正确加载

**解决方法：**
1. 检查网络连接，确保能访问 CDN
2. 查看是否被防火墙或代理拦截
3. 尝试刷新页面（Ctrl + Shift + R）

#### 错误 2: ElementPlus is not defined
```
Uncaught ReferenceError: ElementPlus is not defined
```
**原因：** ElementPlus 库未正确加载

**解决方法：**
1. 检查网络连接
2. 查看浏览器控制台的 Network 标签，检查资源是否加载成功
3. 尝试更换浏览器（推荐 Chrome 或 Edge）

#### 错误 3: Failed to fetch config/users.json
```
Failed to fetch config/users.json
```
**原因：** 配置文件加载失败

**解决方法：**
1. 检查 HTTP 服务器是否运行：`ps aux | grep http.server`
2. 检查文件是否存在：`ls -la assets/config/users.json`
3. 直接访问文件确认：`http://localhost:8080/config/users.json`

#### 错误 4: CORS 错误
```
Access to fetch at '...' has been blocked by CORS policy
```
**原因：** 跨域请求被阻止

**解决方法：**
1. 确保使用 `localhost` 或 `127.0.0.1` 访问
2. 不要使用 `file://` 协议打开 HTML 文件
3. 通过 HTTP 服务器访问页面

---

### 方案 3: 检查服务器状态

**1. 检查 HTTP 服务器是否运行：**
```bash
ps aux | grep "python.*http.server" | grep -v grep
```

如果没有输出，启动服务器：
```bash
cd /workspace/projects
python3 -m http.server 8080 --directory assets
```

**2. 检查端口是否被占用：**
```bash
lsof -i :8080
```

如果端口被占用，可以使用其他端口：
```bash
python3 -m http.server 8081 --directory assets
```

**3. 测试配置文件是否可访问：**
```bash
curl http://localhost:8080/config/users.json
```

应该返回 JSON 格式的用户列表。

---

### 方案 4: 验证账号信息

**测试账号列表：**

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 系统管理员 | system_admin | admin123 |
| 总公司 | company | company123 |
| 店长 | admin | admin123 |
| 厨师 | chef | chef123 |
| 传菜员 | waiter | waiter123 |
| 收银员 | cashier | cashier123 |

**验证步骤：**
1. 确保输入的用户名和密码完全正确（区分大小写）
2. 注意前后不要有空格
3. 尝试复制粘贴用户名和密码

---

## 🔍 详细诊断步骤

### 步骤 1: 检查文件结构

```bash
ls -la assets/
ls -la assets/config/
```

应该看到：
```
assets/
├── login.html
├── config/
│   └── users.json
├── test_login.html          # 新增的测试页面
└── ...
```

### 步骤 2: 检查 CDN 资源

访问这些链接，确认资源可以加载：
- Vue: https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js
- ElementPlus CSS: https://cdn.jsdelivr.net/npm/element-plus/dist/index.css
- ElementPlus JS: https://cdn.jsdelivr.net/npm/element-plus/dist/index.full.min.js

如果无法访问，尝试：
- 使用 VPN
- 更换 DNS 服务器为 8.8.8.8
- 使用国内 CDN 镜像

### 步骤 3: 测试简化登录

打开测试页面：`http://localhost:8080/test_login.html`

1. 查看日志是否显示"✅ 成功加载 6 个用户账号"
2. 点击系统管理员卡片
3. 点击"测试登录"
4. 查看日志是否显示"✅ 本地验证成功!"

### 步骤 4: 测试原始登录页面

打开原始页面：`http://localhost:8080/login.html`

1. 按 F12 打开控制台
2. 点击系统管理员卡片
3. 点击"登录"按钮
4. 查看控制台是否有错误
5. 查看是否弹出成功提示

---

## 💡 常见问题和解决方案

### 问题 1: 页面空白或卡住
**可能原因：**
- Vue 或 ElementPlus 加载失败
- JavaScript 执行错误

**解决方案：**
- 使用简化测试页面测试
- 检查浏览器控制台错误
- 尝试更换浏览器

### 问题 2: 点击演示账号没有反应
**可能原因：**
- JavaScript 未执行
- Vue 没有正确挂载

**解决方案：**
- 检查浏览器控制台
- 确认 Vue 加载成功
- 尝试刷新页面

### 问题 3: 点击登录后没有反应
**可能原因：**
- 登录逻辑有错误
- 用户数据加载失败

**解决方案：**
- 检查控制台是否有错误
- 确认 config/users.json 文件存在
- 查看网络请求是否成功

### 问题 4: 提示"用户名或密码错误"
**可能原因：**
- 输入的用户名或密码不正确
- 用户数据加载失败，使用了默认账号

**解决方案：**
- 确认账号信息正确（区分大小写）
- 检查是否有多余空格
- 使用简化测试页面验证

### 问题 5: 登录成功但没有跳转
**可能原因：**
- staff_workflow.html 文件不存在
- 跳转逻辑被拦截

**解决方案：**
- 检查文件是否存在：`ls assets/staff_workflow.html`
- 确认浏览器没有阻止弹窗
- 手动访问 staff_workflow.html 测试

---

## 🎯 推荐的测试顺序

### 优先级 1: 使用测试页面（最简单）
```
访问: http://localhost:8080/test_login.html
```

### 优先级 2: 检查浏览器控制台
```
1. 打开 http://localhost:8080/login.html
2. 按 F12
3. 查看 Console 标签的错误
```

### 优先级 3: 验证配置文件
```
访问: http://localhost:8080/config/users.json
```

### 优先级 4: 手动测试登录
```
1. 输入用户名: system_admin
2. 输入密码: admin123
3. 点击登录
4. 观察反应
```

---

## 📝 需要的信息

如果问题仍未解决，请提供以下信息：

1. **浏览器控制台错误截图**
   - 按 F12
   - Console 标签
   - 截图红色错误信息

2. **网络请求状态**
   - 按 F12
   - Network 标签
   - 查看 config/users.json 请求是否成功

3. **使用的浏览器和版本**
   - Chrome / Edge / Firefox / Safari
   - 版本号

4. **访问的完整 URL**
   - http://localhost:8080/login.html
   - 或其他 URL

5. **具体操作步骤**
   - 你做了什么
   - 预期发生什么
   - 实际发生了什么

---

## 🆘 联系支持

如果以上方法都无法解决问题，请：
1. 记录详细的错误信息
2. 提供浏览器控制台截图
3. 说明你的测试环境（浏览器、操作系统等）

---

**祝测试顺利！** 🚀
