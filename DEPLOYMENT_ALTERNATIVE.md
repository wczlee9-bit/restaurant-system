# Netlify 部署备选方案

## 当前问题

Netlify 持续在 "Install dependencies" 阶段失败，即使已尝试：
- 删除 package.json
- 简化 netlify.toml
- 删除 netlify.toml
- 添加 _redirects 文件

## 备选方案 1：调整目录结构

**原理**：将静态文件直接放在根目录，避免 Netlify 的自动检测问题。

**步骤**：

1. 在本地创建一个干净的部署目录：

```bash
mkdir deploy-clean
cd deploy-clean
```

2. 复制关键文件到新目录：

```bash
# 复制所有 HTML 文件
cp ../assets/*.html ./

# 复制重定向规则
cp ../assets/_redirects ./

# 复制其他静态资源
cp -r ../assets/* ./
```

3. 提交到 GitHub：

```bash
git init
git add .
git commit -m "Initial deployment"
git remote add origin https://github.com/wczlee9-bit/restaurant-system.git
git push -u origin main --force  # ⚠️ 强制推送，覆盖现有分支
```

---

## 备选方案 2：使用 Netlify CLI 本地部署

**步骤**：

1. 安装 Netlify CLI：

```bash
npm install -g netlify-cli
```

2. 登录 Netlify：

```bash
netlify login
```

3. 部署 assets 目录：

```bash
cd assets
netlify deploy --prod --dir=.
```

---

## 备选方案 3：使用 GitHub Pages（最简单的备选方案）

如果 Netlify 继续有问题，可以考虑切换到 GitHub Pages：

### 步骤：

1. 在 GitHub 仓库页面，进入 Settings
2. 左侧找到 Pages
3. 在 Source 部分，选择 `Deploy from a branch`
4. Branch 选择 `main`，目录选择 `/(root)`
5. 点击 Save

6. 等待部署，访问 `https://wczlee9-bit.github.io/restaurant-system/`

### 注意事项：

- GitHub Pages 默认使用 Jekyll，可能需要创建 `.nojekyll` 文件
- API 代理可能需要在应用层处理（GitHub Pages 不支持重定向规则）

---

## 备选方案 4：使用 Vercel

Vercel 是另一个静态托管服务，可能对纯静态站点更友好：

1. 访问 [vercel.com](https://vercel.com)
2. 点击 "New Project"
3. 导入 GitHub 仓库：`wczlee9-bit/restaurant-system`
4. 配置：
   - Framework Preset: Other
   - Root Directory: `assets`
5. 点击 Deploy

---

## 推荐行动顺序

1. **当前尝试**：等待删除 netlify.toml 后的自动部署结果
2. **如果失败**：按照手动配置指南在 Netlify 控制台配置
3. **如果仍然失败**：使用备选方案 1（调整目录结构）
4. **最后选择**：切换到 GitHub Pages 或 Vercel

---

## 当前部署状态

- Git 提交：758706d (删除 netlify.toml)
- 配置文件：
  - `assets/_redirects` ✅
  - `assets/.nojekyll` ✅
  - `netlify.toml` ❌ (已删除)
  - `netlify.toml.backup` (备份)

---

## 快速验证命令

部署成功后，在浏览器控制台执行：

```javascript
// 检查文件大小
fetch('/customer_order_v3.html')
  .then(r => r.arrayBuffer())
  .then(b => console.log('文件大小:', b.byteLength, '字节'))
  .then(() => console.log('预期: 42KB'))
```

---

最后更新：2026-01-12
