# 📚 餐饮点餐系统 - 部署文档索引

本文档帮助你快速找到所需的部署和使用文档。

---

## 🚀 快速开始

### 第一次部署？
👉 从这里开始: **[QUICK_START.md](./QUICK_START.md)**

30分钟快速完成系统部署，包含：
- 5分钟准备工作
- 20分钟后端部署
- 5分钟前端部署
- 3分钟验证测试

---

## 📖 完整文档

### 1. 快速开始指南
**文件**: `QUICK_START.md`

适合人群：初次部署的用户

内容概要：
- 5分钟快速部署流程
- 常用命令速查
- 系统访问地址
- 常见问题快速解决

---

### 2. 完整商用部署指南
**文件**: `COMMERCIAL_DEPLOYMENT.md`

适合人群：需要详细了解部署过程的技术人员

内容概要：
- 系统架构详解
- 服务器环境准备
- 数据库配置
- Systemd服务配置
- Nginx反向代理
- 备份策略
- 扩容方案
- 运维与维护
- 故障排除

---

### 3. Netlify部署指南
**文件**: `NETLIFY_DEPLOYMENT.md`

适合人群：前端部署人员

内容概要：
- Netlify平台介绍
- 三种部署方法（GitHub集成、拖拽、CLI）
- 自定义域名配置
- API代理配置
- HTTPS证书配置
- 性能优化
- 常见问题

---

### 4. 用户使用手册
**文件**: `USER_MANUAL.md`

适合人群：系统使用人员（顾客、工作人员、管理员）

内容概要：
- 顾客端使用指南
- 工作人员端使用指南
- 会员中心使用指南
- 总公司后台使用指南
- 常见问题解答

---

## 🔧 脚本工具

### 1. 服务器部署脚本
**文件**: `scripts/deploy_to_server.sh`

一键部署工具，支持自动化安装和配置。

**使用方法**:
```bash
# 安装系统
sudo ./scripts/deploy_to_server.sh install

# 更新系统
sudo ./scripts/deploy_to_server.sh update

# 服务管理
sudo ./scripts/deploy_to_server.sh start
sudo ./scripts/deploy_to_server.sh stop
sudo ./scripts/deploy_to_server.sh restart
sudo ./scripts/deploy_to_server.sh status

# 数据库备份
sudo ./scripts/deploy_to_server.sh backup
sudo ./scripts/deploy_to_server.sh restore /path/to/backup.sql.gz
```

---

### 2. 系统验证脚本
**文件**: `scripts/verify_system.sh`

系统健康检查工具，全面验证系统运行状态。

**使用方法**:
```bash
# 运行验证
sudo ./scripts/verify_system.sh
```

**验证内容**:
- ✅ 系统服务状态
- ✅ 端口监听情况
- ✅ 数据库连接
- ✅ API端点可用性
- ✅ 文件完整性
- ✅ 日志检查
- ✅ 性能检查
- ✅ 安全检查
- ✅ 备份检查

---

### 3. API服务启动脚本
**文件**: `scripts/start_api_services.py`

手动启动所有API服务的Python脚本。

**使用方法**:
```bash
# 启动所有服务
python scripts/start_api_services.py
```

---

## 📁 配置文件

### 1. Netlify生产配置
**文件**: `netlify.toml`

Netlify生产环境配置文件，包含：
- 构建设置
- 路由重定向
- API代理配置
- 缓存策略
- 安全头部

**重要**: 部署前需要将 `YOUR_BACKEND_IP` 替换为实际的服务器IP地址。

---

### 2. 数据库初始化脚本
**文件**: `scripts/init_database.py`

数据库表结构初始化脚本，用于：
- 创建数据库表
- 初始化默认数据
- 配置角色和权限

---

## 🎯 根据角色选择文档

### 我是系统管理员
推荐阅读顺序：
1. [QUICK_START.md](./QUICK_START.md) - 快速部署
2. [COMMERCIAL_DEPLOYMENT.md](./COMMERCIAL_DEPLOYMENT.md) - 详细配置
3. [scripts/deploy_to_server.sh](./scripts/deploy_to_server.sh) - 自动化工具
4. [scripts/verify_system.sh](./scripts/verify_system.sh) - 系统验证

### 我是开发人员
推荐阅读顺序：
1. [COMMERCIAL_DEPLOYMENT.md](./COMMERCIAL_DEPLOYMENT.md) - 系统架构
2. [NETLIFY_DEPLOYMENT.md](./NETLIFY_DEPLOYMENT.md) - 前端部署
3. 源代码中的注释和文档

### 我是运维人员
推荐阅读顺序：
1. [COMMERCIAL_DEPLOYMENT.md](./COMMERCIAL_DEPLOYMENT.md) - 完整部署
2. 运维与维护章节
3. 故障排除章节
4. [scripts/verify_system.sh](./scripts/verify_system.sh) - 系统监控

### 我是店铺管理者
推荐阅读顺序：
1. [USER_MANUAL.md](./USER_MANUAL.md) - 工作人员端使用
2. [USER_MANUAL.md](./USER_MANUAL.md) - 总公司后台使用
3. [USER_MANUAL.md](./USER_MANUAL.md) - 常见问题

### 我是餐厅员工
推荐阅读：
- [USER_MANUAL.md](./USER_MANUAL.md) - 工作人员端使用指南

### 我是顾客
推荐阅读：
- [USER_MANUAL.md](./USER_MANUAL.md) - 顾客端使用指南

---

## 📞 技术支持

### 联系方式
- 技术支持邮箱: support@example.com
- 技术支持电话: 400-xxx-xxxx
- 在线客服: 9:00-18:00

### 在线资源
- 官网: https://www.example.com
- 帮助中心: https://help.example.com
- 开发者文档: https://docs.example.com
- 社区论坛: https://community.example.com

---

## 🔄 版本更新

### 当前版本: v1.0.0

**文档更新日期**: 2024-01-01

**更新内容**:
- ✅ 创建完整的部署文档体系
- ✅ 添加自动化部署脚本
- ✅ 添加系统验证脚本
- ✅ 完善用户使用手册

---

## 📝 文档贡献

如果你发现文档中的错误或有改进建议，欢迎：

1. 提交Issue反馈问题
2. 提交Pull Request改进文档
3. 联系技术支持团队

---

## 🎉 开始使用

选择适合你的文档，开始部署和使用餐饮点餐系统吧！

**快速开始**: [QUICK_START.md](./QUICK_START.md)

**完整部署**: [COMMERCIAL_DEPLOYMENT.md](./COMMERCIAL_DEPLOYMENT.md)

**用户手册**: [USER_MANUAL.md](./USER_MANUAL.md)

---

祝你部署顺利，使用愉快！🍽️
