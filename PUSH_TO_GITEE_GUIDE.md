# 🚀 推送代码到 Gitee 指南

## 📋 概述

本文档指导如何将合并后的模块化架构代码推送到 Gitee 仓库。

## 🎯 目标仓库

- **平台**: Gitee (码云)
- **仓库**: `lijun75/restaurant`
- **URL**: https://gitee.com/lijun75/restaurant.git

## 📂 当前状态

### 已完成的工作

✅ **基础框架集成**：
- `core/module_base.py` - 模块基类和注册器
- `core/service_interfaces.py` - 服务接口定义
- `modular_app.py` - 模块化应用入口

✅ **模块配置系统**：
- `config/modules.json` - 模块配置文件
- `src/module_loader.py` - 模块加载器

✅ **遗留模块封装**：
- `modules/legacy/base_module.py` - 遗留模块适配器
- `modules/legacy/order_module.py` - 订单模块
- `modules/legacy/menu_module.py` - 菜单模块
- `modules/legacy/user_module.py` - 用户模块
- `modules/legacy/stock_module.py` - 库存模块
- `modules/legacy/member_module.py` - 会员模块
- `modules/legacy/payment_module.py` - 支付模块
- `modules/legacy/stats_module.py` - 统计模块
- `modules/legacy/receipt_module.py` - 小票模块
- `modules/legacy/websocket_module.py` - WebSocket 模块
- `modules/legacy/workflow_module.py` - 工作流模块
- `modules/legacy/permission_module.py` - 权限模块

✅ **测试验证**：
- `test_module_loader.py` - 模块加载器测试脚本

## 🔧 推送步骤

### 步骤 1：检查当前 Git 状态

```bash
# 查看当前 remote
git remote -v

# 查看当前分支
git branch
```

### 步骤 2：添加 Gitee remote

```bash
# 添加 Gitee remote
git remote add gitee https://gitee.com/lijun75/restaurant.git

# 验证 remote
git remote -v
```

### 步骤 3：提交当前更改

```bash
# 查看更改
git status

# 添加所有新文件
git add .

# 提交更改
git commit -m "feat: 集成模块化架构

- 添加模块化框架 (core/)
- 添加模块加载器 (src/module_loader.py)
- 封装现有系统为遗留模块 (modules/legacy/)
- 添加模块配置文件 (config/modules.json)
- 添加测试脚本 (test_module_loader.py)
"
```

### 步骤 4：推送到 Gitee

```bash
# 推送到 Gitee main 分支
git push gitee main

# 如果 main 分支不存在，先创建
git push -u gitee main
```

### 步骤 5：验证推送

1. 访问 Gitee 仓库：https://gitee.com/lijun75/restaurant
2. 检查以下文件是否存在：
   - `core/module_base.py`
   - `core/service_interfaces.py`
   - `src/module_loader.py`
   - `config/modules.json`
   - `modules/legacy/`

## 🔄 替代方案：使用 HTTPS 和 Token

如果遇到认证问题，可以使用 Gitee Personal Access Token：

### 获取 Personal Access Token

1. 访问：https://gitee.com/profile/personal_access_tokens
2. 创建新 Token
3. 选择权限：`projects`（读写权限）
4. 复制 Token（只显示一次）

### 使用 Token 推送

```bash
# 使用 URL + Token 方式
git remote set-url gitee https://<your-token>@gitee.com/lijun75/restaurant.git

# 推送
git push gitee main
```

## 📝 推送后的验证

### 1. 检查文件结构

在 Gitee 仓库中，检查以下结构：

```
restaurant/
├── core/
│   ├── module_base.py
│   └── service_interfaces.py
├── modules/
│   └── legacy/
│       ├── base_module.py
│       ├── order_module.py
│       ├── menu_module.py
│       └── ...
├── config/
│   └── modules.json
├── src/
│   ├── module_loader.py
│   └── ...
└── test_module_loader.py
```

### 2. 克隆并测试

在新的环境中克隆并测试：

```bash
# 克隆仓库
git clone https://gitee.com/lijun75/restaurant.git
cd restaurant

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行测试
python test_module_loader.py
```

## 🚨 常见问题

### 问题 1：认证失败

**错误信息**：
```
fatal: Authentication failed for 'https://gitee.com/lijun75/restaurant.git'
```

**解决方案**：
1. 使用 Personal Access Token（参考上面的步骤）
2. 或者配置 SSH 密钥

### 问题 2：远程仓库已存在

**错误信息**：
```
fatal: remote gitee already exists
```

**解决方案**：
```bash
# 删除现有的 remote
git remote remove gitee

# 重新添加
git remote add gitee https://gitee.com/lijun75/restaurant.git
```

### 问题 3：推送被拒绝

**错误信息**：
```
! [rejected] main -> main (fetch first)
error: failed to push some refs
```

**解决方案**：
```bash
# 先拉取远程代码
git pull gitee main --rebase

# 再推送
git push gitee main
```

## 📊 推送清单

完成以下任务后，推送才算完成：

- [ ] 当前代码已提交到本地 Git
- [ ] Gitee remote 已配置
- [ ] 代码已成功推送到 Gitee
- [ ] Gitee 仓库中文件结构正确
- [ ] 在新环境中克隆并测试成功

## 🎉 推送成功后

推送成功后，可以开始以下工作：

1. **部署到腾讯云**
   - 参考 `deploy_from_gitee.sh` 脚本
   - 或手动部署到腾讯云服务器

2. **渐进式重构**
   - 参考 `GITEE_MERGE_PLAN.md`
   - 逐个模块重构，提升代码质量

3. **文档更新**
   - 更新 README.md
   - 更新 API 文档
   - 更新部署文档

## 📞 支持

如有问题，请：
1. 查看 Gitee 仓库 Issues
2. 查看项目文档
3. 联系项目维护者

---

**最后更新**: 2024-02-06
