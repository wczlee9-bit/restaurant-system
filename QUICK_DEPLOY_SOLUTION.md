# 快速部署解决方案

## 问题
`restaurant-assets.zip` 文件在服务器上，无法直接下载到本地。

## 解决方案：从 GitHub 下载文件

由于你的代码已经推送到 GitHub，可以直接从 GitHub 下载文件进行部署。

### 步骤 1: 删除当前的 Netlify 项目

在当前 Netlify 项目页面：
1. 滚动到 **"Danger zone"** 部分
2. 点击 **"Delete this project"**
3. 确认删除

### 步骤 2: 从 GitHub 下载 assets 文件夹

1. **访问 GitHub 仓库**：
   https://github.com/wczlee9-bit/restaurant-system

2. **点击 "Code" 按钮**

3. **点击 "Download ZIP"**
   - 下载整个仓库的压缩包

4. **解压下载的 ZIP 文件**

5. **找到 `assets` 文件夹**
   - 在解压后的文件夹中找到 `assets` 文件夹

### 步骤 3: 拖拽部署到 Netlify

1. **访问 Netlify**：
   https://app.netlify.com/sites

2. **点击 "Add new site"**

3. **选择 "Deploy manually"**

4. **将 `assets` 文件夹拖拽到 Netlify 上传区域**

5. **等待 1-2 分钟部署完成**

### 步骤 4: 访问部署后的站点

部署成功后，Netlify 会显示站点 URL（类似：`random-name-12345.netlify.app`）

访问：
- **登录页**：`https://你的站点名.netlify.app/login_standalone.html`
- **首页**：`https://你的站点名.netlify.app/index.html`

### 步骤 5: 测试登录

使用以下账号测试：
- **系统管理员**：用户名 `admin`，密码 `admin123`
- **总公司账号**：用户名 `headquarters`，密码 `hq123456`

## 备用方案：只上传核心文件

如果下载整个仓库太慢，可以只上传核心文件：

在本地创建一个 `assets` 文件夹，然后从 GitHub 下载以下文件：

### 必需文件（拖拽部署必须）：
1. `login_standalone.html`（登录页面）
2. `index.html`（首页）
3. `staff_workflow.html`（工作人员端）
4. `shop_settings.html`（店铺设置）
5. `customer_order.html`（顾客点餐）

### 如何从 GitHub 下载单个文件：

1. **访问 GitHub 仓库**
   https://github.com/wczlee9-bit/restaurant-system/tree/main/assets

2. **点击想要下载的文件**

3. **点击右上角的 "Raw" 按钮**

4. **右键"另存为"或使用 Ctrl+S 保存**

5. **保存到 `assets` 文件夹中**

6. **重复以上步骤下载所有必需文件**

7. **将 `assets` 文件夹拖拽到 Netlify**

---

## 推荐流程（最快）：

1. ✅ 删除当前的 Netlify 项目
2. ✅ 访问 https://github.com/wczlee9-bit/restaurant-system
3. ✅ 点击 "Download ZIP" 下载整个仓库
4. ✅ 解压并找到 `assets` 文件夹
5. ✅ 在 Netlify 创建新站点
6. ✅ 拖拽 `assets` 文件夹到 Netlify
7. ✅ 等待部署完成并测试登录

---

**现在开始吧！第一步：删除当前的 Netlify 项目**

完成后告诉我，我会指导你下一步！
