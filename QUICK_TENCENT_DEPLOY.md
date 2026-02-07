# 🚀 腾讯云部署 - 快速开始

## 一键部署（5分钟完成）

### 步骤1：准备文件

在**本地电脑**（不是服务器）执行：

```bash
# 1. 进入项目目录
cd /workspace/projects

# 2. 确认文件已打包
ls -lh restaurant-frontend.tar.gz
```

应该看到类似输出：
```
-rw-r--r-- 1 root root 23K Feb  7 23:18 restaurant-frontend.tar.gz
```

### 步骤2：上传到服务器

使用以下任一方法上传文件：

#### 方法A：使用scp（推荐）
```bash
scp restaurant-frontend.tar.gz root@115.191.1.219:/tmp/
scp deploy_to_tencent_cloud.sh root@115.191.1.219:/tmp/
```

#### 方法B：使用其他工具
- 使用WinSCP、FileZilla等工具上传
- 上传到服务器的 `/tmp/` 目录

### 步骤3：SSH登录服务器

```bash
ssh root@115.191.1.219
```

### 步骤4：运行部署脚本

在服务器上执行：

```bash
# 添加执行权限
chmod +x /tmp/deploy_to_tencent_cloud.sh

# 运行部署脚本
bash /tmp/deploy_to_tencent_cloud.sh
```

### 步骤5：验证部署

在浏览器中打开：

- **顾客端**: http://115.191.1.219/
- **管理端**: http://115.191.1.219/admin/dashboard/index.html
- **API文档**: http://115.191.1.219/api/docs

看到页面即表示部署成功！🎉

---

## 如果无法使用SCP

### 手动部署步骤

1. **SSH登录服务器**
```bash
ssh root@115.191.1.219
```

2. **下载代码**
```bash
cd /tmp
# 从GitHub克隆代码
git clone https://github.com/wczlee9-bit/restaurant-system.git

# 复制前端文件
cp -r restaurant-system/frontend /var/www/restaurant-system/
```

3. **运行部署脚本**
```bash
cd /tmp
chmod +x restaurant-system/deploy_to_tencent_cloud.sh
bash restaurant-system/deploy_to_tencent_cloud.sh
```

---

## 测试点餐流程

### 1. 顾客端测试

访问：http://115.191.1.219/

测试流程：
- 扫码进入（或直接访问）
- 浏览菜单
- 添加菜品到购物车
- 提交订单

### 2. 管理端测试

访问：http://115.191.1.219/admin/dashboard/index.html

测试流程：
- 查看统计数据
- 管理菜品
- 处理订单
- 管理会员

### 3. API测试

访问：http://115.191.1.219/api/docs

测试接口：
- GET /api/tables/
- GET /api/menu-items/
- POST /api/orders/
- PATCH /api/orders/{id}/status

---

## 常见问题

### Q1: 404 Not Found
**解决**:
```bash
# 检查文件
ls -la /var/www/restaurant-system/frontend/customer/

# 检查Nginx配置
nginx -t

# 查看错误日志
tail -f /var/log/nginx/error.log
```

### Q2: API 500错误
**解决**:
```bash
# 检查后端服务
systemctl status restaurant-backend

# 检查API地址配置
cat /var/www/restaurant-system/frontend/common/js/api.js
```

### Q3: 无法上传文件
**解决**:
- 使用FileZilla等工具上传
- 或使用GitHub克隆方式

---

## 技术支持

如果遇到问题：
1. 查看Nginx日志：`tail -f /var/log/nginx/error.log`
2. 查看部署文档：`TENCENT_CLOUD_DEPLOYMENT.md`
3. 检查后端服务状态：`systemctl status restaurant-backend`

---

**部署成功后，请访问 http://115.191.1.219 测试所有功能！** 🚀
