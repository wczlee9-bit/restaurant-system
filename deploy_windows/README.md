# Windows 云服务器部署工具包

本工具包包含在 Windows 云服务器（宝塔面板）上部署餐饮系统的自动化脚本和配置文件。

---

## 📋 包含文件

| 文件 | 说明 |
|------|------|
| `quick_deploy.bat` | 一键部署主脚本 |
| `install_requirements.bat` | 安装 Python 依赖 |
| `init_database.bat` | 初始化数据库 |
| `start_backend.bat` | 启动后端服务 |
| `README.md` | 本文件 |

---

## 🚀 快速开始

### 方法 1: 使用快速部署脚本（推荐）

1. **下载项目代码**到 Windows 服务器
   ```powershell
   cd C:\
   mkdir restaurant-system
   cd C:\restaurant-system
   git clone https://github.com/wczlee9-bit/restaurant-system.git
   ```

2. **运行快速部署脚本**
   ```powershell
   cd restaurant-system\deploy_windows
   quick_deploy.bat
   ```

3. **按提示选择操作**：
   - 选项 1：安装 Python 依赖
   - 选项 2：初始化数据库
   - 选项 3：启动后端服务
   - 选项 4：复制前端文件
   - 选项 5：生成配置文件
   - 选项 6：检查部署状态

### 方法 2: 手动执行每个步骤

#### Step 1: 安装 Python 依赖

```powershell
cd C:\restaurant-system\deploy_windows
install_requirements.bat
```

#### Step 2: 设置数据库连接

```powershell
# 设置环境变量
set PGDATABASE_URL=postgresql://username:password@localhost:5432/restaurant_system
```

#### Step 3: 初始化数据库

```powershell
cd C:\restaurant-system\deploy_windows
init_database.bat
```

#### Step 4: 启动后端服务

```powershell
cd C:\restaurant-system\deploy_windows
start_backend.bat
```

#### Step 5: 复制前端文件

在宝塔面板手动操作，或使用脚本：

```powershell
cd C:\restaurant-system\deploy_windows
quick_deploy.bat
# 选择选项 4
```

---

## 📋 部署前准备

### 1. 在宝塔面板安装软件

- Python 3.10+
- PostgreSQL 14+
- Nginx 1.20+

### 2. 创建数据库

在宝塔面板：
1. 点击 **数据库** → **PostgreSQL**
2. 创建数据库：
   - 数据库名：`restaurant_system`
   - 用户名：`restaurant_user`
   - 密码：设置强密码

### 3. 获取数据库连接字符串

格式：
```
postgresql://用户名:密码@localhost:5432/数据库名
```

例如：
```
postgresql://restaurant_user:YourPassword123@localhost:5432/restaurant_system
```

---

## 🔧 配置说明

### 环境变量

脚本使用以下环境变量：

| 环境变量 | 说明 | 必填 |
|---------|------|------|
| `PGDATABASE_URL` | 数据库连接字符串 | 是 |
| `SECRET_KEY` | JWT 密钥 | 否（有默认值） |

### 数据库连接字符串格式

```
postgresql://username:password@host:port/database
```

---

## 📊 部署流程

```
1. 远程连接 Windows 服务器
2. 在宝塔面板安装必要软件（Python, PostgreSQL, Nginx）
3. 创建数据库
4. 下载项目代码到服务器
5. 运行 quick_deploy.bat
6. 按顺序执行：
   - 安装 Python 依赖
   - 初始化数据库
   - 启动后端服务
   - 复制前端文件
7. 在宝塔面板配置 Nginx 反向代理
8. 测试访问
```

---

## 🧪 测试部署

### 测试后端

访问：
```
http://localhost:8000/health
```

应该返回：
```json
{
  "status": "ok",
  "message": "餐饮系统API服务运行正常",
  ...
}
```

### 测试前端

访问：
```
http://服务器IP/
http://服务器IP/portal.html
http://服务器IP/customer_order_v3.html
```

---

## 🔍 常见问题

### Q1: 提示 "未找到 Python"

**解决**：
1. 在宝塔面板安装 Python 3.10+
2. 或手动安装 Python：https://www.python.org/downloads/
3. 重启服务器

### Q2: 数据库连接失败

**解决**：
1. 检查 PostgreSQL 服务是否运行
2. 检查数据库连接字符串是否正确
3. 检查数据库用户名和密码

### Q3: 依赖安装失败

**解决**：
1. 检查网络连接
2. 尝试使用国内镜像：
   ```powershell
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
   ```

### Q4: 后端服务无法启动

**解决**：
1. 检查端口 8000 是否被占用
2. 检查数据库连接
3. 查看错误日志

---

## 📚 详细文档

完整的部署指南请查看：

**[WINDOWS_CLOUD_DEPLOYMENT_GUIDE.md](../WINDOWS_CLOUD_DEPLOYMENT_GUIDE.md)**

包含：
- 详细的部署步骤
- 宝塔面板配置方法
- Nginx 配置示例
- SSL 证书配置
- 性能优化建议
- 安全建议

---

## 💡 下一步

部署完成后：

1. **配置 Nginx 反向代理**
   - 在宝塔面板配置 Nginx
   - 设置反向代理规则

2. **测试所有功能**
   - 点餐功能
   - 订单管理
   - 会员系统
   - 库存管理

3. **配置 SSL 证书（可选）**
   - 使用 Let's Encrypt 免费证书
   - 在宝塔面板一键申请

4. **定期备份数据**
   - 在宝塔面板设置自动备份
   - 备份数据库和前端文件

---

## 🆘 需要帮助？

- 查看日志文件：`C:\restaurant-system\logs\api.log`
- 查看宝塔面板日志
- 联系技术支持

---

**版本**: v2.0.0
**更新时间**: 2025-01-12
