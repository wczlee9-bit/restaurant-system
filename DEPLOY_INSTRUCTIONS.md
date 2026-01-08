# Netlify 拖拽部署指南

## 当前状态

✅ 已准备好部署文件：`restaurant-assets.zip`（包含所有 HTML 文件和资源）

## 需要你操作的步骤

### 步骤 1: 删除当前的 Netlify 项目

在当前的 Netlify 项目页面：
1. 滚动到页面底部的 **"Danger zone"** 部分
2. 找到 **"Delete project"**
3. 点击 **"Delete this project"** 按钮
4. 确认删除

### 步骤 2: 创建新站点（拖拽部署）

1. **访问 Netlify 项目列表**：
   - 删除后会自动跳转，或访问：https://app.netlify.com/sites

2. **点击 "Add new site"** 按钮
   - 在页面顶部或中间位置

3. **选择 "Deploy manually"**（手动部署）
   - 不要选择 "Import an existing project"

4. **准备部署文件**：
   - 你需要下载 `restaurant-assets.zip` 文件
   - 或者在本地准备 `assets` 文件夹

### 步骤 3: 上传文件

**方案 A: 上传 ZIP 文件**
- 将 `restaurant-assets.zip` 文件拖拽到 Netlify 的上传区域
- 等待上传和解压（1-2 分钟）

**方案 B: 上传文件夹**
- 将整个 `assets` 文件夹拖拽到 Netlify 的上传区域
- 等待上传（1-2 分钟）

### 步骤 4: 部署完成

部署成功后：
1. Netlify 会显示绿色的 "Published" 状态
2. 记下站点名称（如：`random-name-12345.netlify.app`）
3. 可以在 "Site settings" 中修改站点名称

### 步骤 5: 测试访问

部署成功后，访问以下 URL（将 `你的站点名` 替换为实际的站点名）：

- **登录页**：`https://你的站点名.netlify.app/login_standalone.html`
- **首页**：`https://你的站点名.netlify.app/index.html`
- **工作人员端**：`https://你的站点名.netlify.app/staff_workflow.html`
- **店铺设置**：`https://你的站点名.netlify.app/shop_settings.html`

## 演示账号

**系统管理员**
- 用户名: `admin`
- 密码: `admin123`

**总公司账号**
- 用户名: `headquarters`
- 密码: `hq123456`

## 关于文件传输

由于服务器环境限制，`restaurant-assets.zip` 文件位于：
`/workspace/projects/restaurant-assets.zip`

你需要通过以下方式之一获取文件：

### 选项 1: 通过 SSH/SFTP 下载
如果你有服务器访问权限，可以使用：
```bash
# 在你的本地电脑上
scp user@server:/workspace/projects/restaurant-assets.zip .
```

### 选项 2: 手动准备文件
在你的本地：
1. 创建一个 `assets` 文件夹
2. 从项目源代码中复制所有 HTML 文件到 `assets` 文件夹
3. 拖拽整个 `assets` 文件夹到 Netlify

### 选项 3: 使用 Netlify CLI（需要安装）
```bash
# 安装 Netlify CLI
npm install -g netlify-cli

# 登录 Netlify
netlify login

# 直接从服务器部署
cd assets
netlify deploy --prod
```

## 如果无法下载文件

请告诉我，我可以帮你：
1. 创建一个更小的压缩包（只包含核心文件）
2. 使用其他部署方式
3. 指导你手动准备文件

## 注意事项

1. 拖拽部署后，Netlify 分配的站点名是随机的
2. 可以在 "Site settings" > "Change site name" 修改站点名
3. 每次更新需要重新上传整个文件夹或 ZIP 文件
4. 部署后记得测试登录功能

---

**下一步**：
1. 删除当前项目
2. 创建新站点
3. 告诉我你是否能够获取 `restaurant-assets.zip` 文件

**如果你无法下载文件，我会提供其他解决方案。**
