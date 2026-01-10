# 🔧 Netlify API 代理配置快速切换指南

## 📊 当前状态

- ✅ 后端服务已启动（沙盒环境）
- ✅ API 测试通过（桌号、菜品分类、菜品列表）
- ❌ Netlify 当前代理指向生产服务器（115.191.1.219:8000）- 未运行

## 🎯 快速测试方案（推荐用于开发测试）

### 方式 1：使用 Netlify 控制台修改（最快）

1. 登录 [Netlify](https://app.netlify.com)
2. 进入你的站点：`mellow-rabanadas-877f3e`
3. 点击 **Site settings** → **Build & deploy** → **Environment variables**
4. 找到 **Netlify configuration** 部分
5. 点击 **Edit netlify.toml**
6. 将所有 `115.191.1.219` 替换为 `9.129.157.122`
7. 保存后等待重新部署（约 1-2 分钟）

**示例修改：**
```toml
# 修改前
from = "/api/*"
to = "http://115.191.1.219:8000/api/:splat"

# 修改后
from = "/api/*"
to = "http://9.129.157.122:8000/api/:splat"
```

### 方式 2：使用测试配置文件

我已经创建了 `netlify-sandbox.toml` 文件，通过以下方式使用：

**方法 A：通过 Netlify 控制台上传**
1. 登录 Netlify 控制台
2. 进入 **Site settings** → **Build & deploy** → **Continuous Deployment**
3. 找到 **Netlify configuration** → **Edit netlify.toml**
4. 复制 `netlify-sandbox.toml` 的内容粘贴进去
5. 保存并等待部署

**方法 B：通过 Git 提交（不推荐测试环境）**
```bash
# 重命名配置文件
mv netlify-sandbox.toml netlify.toml

# 提交并推送（会触发 Netlify 自动部署）
git add netlify.toml
git commit -m "chore: switch to sandbox API for testing"
git push origin main
```

## 🚀 生产环境部署（推荐用于正式上线）

### 配置 GitHub Secrets 实现自动部署到服务器

需要配置以下 GitHub Secrets：

1. 访问：https://github.com/wczlee9-bit/restaurant-system/settings/secrets/actions
2. 点击 **New repository secret**

**必需的 Secrets：**

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `SSH_PRIVATE_KEY` | 服务器的 SSH 私钥 | `-----BEGIN RSA PRIVATE KEY-----...` |
| `SERVER_HOST` | 服务器 IP 地址 | `115.191.1.219` |
| `SERVER_USER` | 服务器用户名 | `root` 或 `ubuntu` |
| `SERVER_PORT` | SSH 端口（可选） | `22` |
| `SERVER_DEPLOY_PATH` | 部署路径 | `/opt/restaurant-system` |

**获取 SSH 私钥：**
```bash
# 在服务器上执行（如果还没生成密钥）
ssh-keygen -t rsa -b 4096 -C "github-actions"

# 将公钥添加到服务器
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

# 复制私钥内容（包括 BEGIN 和 END 行）
cat ~/.ssh/id_rsa
```

**配置完成后的效果：**
- 当你推送代码到 GitHub 时，GitHub Actions 会自动：
  1. SSH 连接到服务器
  2. 拉取最新代码
  3. 安装/更新依赖
  4. 重启所有 API 服务

## ✅ 验证部署

部署完成后，访问前端并测试：

```
https://mellow-rabanadas-877f3e.netlify.app/
```

**测试 API 连接：**

1. 打开浏览器开发者工具（F12）
2. 切换到 **Network** 标签
3. 刷新页面或点击功能
4. 查看是否有 API 请求成功（状态码 200）

**预期结果：**
- ✅ 页面能正常加载
- ✅ 菜品数据正常显示
- ✅ 桌号列表正常显示
- ✅ 不会出现灰色/空白页面

## 🔄 配置切换

**沙盒测试环境 → 生产环境：**
```bash
# 恢复生产配置
mv netlify.toml netlify-sandbox.toml.backup
git checkout netlify-production.toml
mv netlify-production.toml netlify.toml

# 或者直接修改 netlify.toml
# 将 9.129.157.122 改回 115.191.1.219
```

## 📝 快速命令

```bash
# 检查当前后端服务状态
curl http://9.129.157.122:8000/api/tables/

# 测试 Netlify 代理（在浏览器执行）
fetch('/api/tables/').then(r=>r.json()).then(console.log)

# 查看后端服务日志
tail -f logs/restaurant_api_8000.log

# 重启后端服务
pkill -f "uvicorn.*restaurant_api"
nohup uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000 > logs/restaurant_api_8000.log 2>&1 &
```

## 🐛 常见问题

**Q: 修改配置后还是无法连接 API？**
- 检查 Netlify 部署状态：确保部署成功（无红色错误）
- 清除浏览器缓存：Ctrl + Shift + R（Windows）或 Cmd + Shift + R（Mac）
- 检查后端服务：`curl http://9.129.157.122:8000/api/tables/`

**Q: 如何确认 Netlify 使用的是哪个配置？**
- 访问 Netlify 控制台 → **Deploys** 页面
- 点击最新的部署记录
- 查看 **Deploy summary** 中的配置信息

**Q: GitHub Actions 部署失败怎么办？**
- 检查 GitHub Actions 日志：仓库 → **Actions** 标签
- 验证 Secrets 是否正确配置
- 确认服务器 SSH 连接正常：`ssh -p 22 root@115.191.1.219`

## 📞 下一步

1. **快速测试**：使用方式 1 修改 Netlify 配置，指向沙盒环境
2. **验证功能**：测试扫码点餐、订单提交等功能
3. **生产部署**：配置 GitHub Secrets，实现自动部署到生产服务器

---

**文档更新时间**：2025-01-10
**当前环境**：沙盒测试环境（9.129.157.122:8000）
