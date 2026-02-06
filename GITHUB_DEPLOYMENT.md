# 🚀 腾讯云部署指南（从 GitHub）

## 📦 最简单的部署方式

现在我们不需要 Gitee 了！直接从 GitHub 部署到腾讯云。

---

## 🎯 两种部署方式

### 方式 1：使用部署包（推荐，最简单）

```bash
# 1. 上传部署包到腾讯云
scp restaurant-github-deploy-20260206-233518.tar.gz root@129.226.196.76:/tmp/

# 2. 连接到腾讯云
ssh root@129.226.196.76

# 3. 解压并部署
cd /tmp
tar -xzf restaurant-github-deploy-20260206-233518.tar.gz
cd github_deployment_package_temp
bash deploy_from_github.sh
```

### 方式 2：直接从 GitHub（无需上传文件）

```bash
# 1. 连接到腾讯云
ssh root@129.226.196.76

# 2. 下载部署脚本
cd /tmp
wget https://raw.githubusercontent.com/wczlee9-bit/restaurant-system/main/deploy_from_github.sh

# 3. 运行部署
chmod +x deploy_from_github.sh
bash deploy_from_github.sh
```

---

## 📋 部署包信息

- 文件名: `restaurant-github-deploy-20260206-233518.tar.gz`
- 大小: 65M
- 包含: 源代码 + 部署脚本 + 文档

---

## ✅ 部署脚本会自动完成

1. ✅ 环境检查
2. ✅ 备份现有系统
3. ✅ 从 GitHub 克隆代码
4. ✅ 安装依赖
5. ✅ 初始化数据库
6. ✅ 测试模块加载器
7. ✅ 配置服务
8. ✅ 启动服务
9. ✅ 配置 Nginx
10. ✅ 验证部署

---

## 🎯 部署后验证

```bash
# 检查服务状态
systemctl status restaurant

# 测试 API
curl http://localhost:8000/health

# 访问系统
# http://129.226.196.76
```

---

## 🔄 更新系统

```bash
# 连接到腾讯云
ssh root@129.226.196.76

# 重新运行部署脚本（自动拉取最新代码）
cd /opt/restaurant-system
bash deploy_from_github.sh
```

---

## 📊 项目地址

- GitHub: https://github.com/wczlee9-bit/restaurant-system
- 腾讯云: http://129.226.196.76

---

## 🎉 开始部署

选择一种方式开始部署吧！

**推荐方式 1**（最简单，使用部署包）

```bash
scp restaurant-github-deploy-20260206-233518.tar.gz root@129.226.196.76:/tmp/
```

然后连接到腾讯云运行 `bash deploy_from_github.sh`

---

**预计时间**: 10-15分钟

**祝您部署成功！** 🚀
