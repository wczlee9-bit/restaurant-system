# 🎉 多店铺扫码点餐系统 - 完整部署指南

## ✅ 开发完成总结

### 已开发功能清单

| 阶段 | 功能 | 状态 |
|------|------|------|
| **第一阶段** | Nginx 反向代理配置 | ✅ 完成 |
| **第二阶段** | 扫码点餐前端（Vue.js 3） | ✅ 完成 |
| **第三阶段** | 管理后台（Vue.js 3 + Element Plus） | ✅ 完成 |
| **第四阶段** | 后端功能扩展（库存/会员/统计） | ✅ 完成 |
| **第五阶段** | WebSocket 实时通信 | ✅ 完成 |
| **第五阶段** | 小票打印功能 | ✅ 完成 |

---

## 📦 沙盒项目结构

```
/workspace/projects/
├── frontend/                    # 扫码点餐前端
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   ├── api/                # API 封装
│   │   └── App.vue             # 根组件
│   ├── package.json            # 依赖配置
│   └── vite.config.js          # Vite 配置
│
├── admin/                       # 管理后台
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   ├── components/         # 布局组件
│   │   ├── api/                # API 封装
│   │   └── App.vue             # 根组件
│   ├── package.json
│   └── vite.config.js
│
└── backend_extensions/         # 后端扩展
    ├── src/
    │   ├── routes/             # API 路由
    │   │   ├── stats_routes.py      # 统计 API
    │   │   ├── stock_routes.py      # 库存 API
    │   │   ├── member_routes.py     # 会员 API
    │   │   ├── websocket_routes.py  # WebSocket
    │   │   └── receipt_routes.py    # 小票打印
    │   ├── storage/database/   # 数据库模型
    │   ├── websocket_manager.py     # WebSocket 管理
    │   └── main.py             # 应用入口
```

---

## 🚀 部署步骤（一次性完成）

### 第一步：上传所有文件到服务器

```bash
# 服务器上执行
cd /opt/restaurant-system

# 1. 上传前端文件（从沙盒 /workspace/projects/frontend/）
#    复制所有文件到 /opt/restaurant-system/frontend/

# 2. 上传管理后台文件（从沙盒 /workspace/projects/admin/）
#    复制所有文件到 /opt/restaurant-system/admin/

# 3. 上传后端扩展文件（从沙盒 /workspace/projects/backend_extensions/）
#    复制 src/ 目录到 /opt/restaurant-system/src/
```

### 第二步：更新后端代码

```bash
# 1. 备份原有路由
cd /opt/restaurant-system/src/routes
cp order_routes.py order_routes.py.bak

# 2. 替换为更新后的路由（从 backend_extensions/src/routes/）
#    将 stats_routes.py, stock_routes.py, member_routes.py
#    websocket_routes.py, receipt_routes.py 复制到 routes/ 目录
#    将 order_routes_updated.py 覆盖为 order_routes.py

# 3. 复制 WebSocket 管理器
#    websocket_manager.py 复制到 src/ 目录

# 4. 更新 main.py 注册新路由
```

### 第三步：更新数据库模型

```bash
cd /opt/restaurant-system/src/storage/database

# 备份原模型
cp models.py models.py.bak

# 替换为新模型（包含 points 和 low_stock_threshold 字段）
#    从 backend_extensions/src/storage/database/models.py 覆盖
```

### 第四步：数据库迁移

```bash
cd /opt/restaurant-system

# 执行数据库迁移脚本
PGPASSWORD='restaurant_pass_2024' psql -h localhost -U restaurant_user -d restaurant_db << 'EOSQL'
-- 添加积分字段
ALTER TABLE users ADD COLUMN IF NOT EXISTS points INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 添加低库存阈值字段
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS low_stock_threshold INTEGER DEFAULT 10;
ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 验证字段
\d users
\d menu_items
EOSQL
```

### 第五步：构建前端项目

```bash
# 1. 构建扫码点餐前端
cd /opt/restaurant-system/frontend
npm install
npm run build

# 2. 构建管理后台
cd /opt/restaurant-system/admin
npm install
npm run build
```

### 第六步：更新 Nginx 配置

```bash
# 备份原配置
cp /etc/nginx/sites-available/restaurant /etc/nginx/sites-available/restaurant.bak

# 创建新配置（支持 WebSocket）
cat > /etc/nginx/sites-available/restaurant << 'EOF'
server {
    listen 80;
    server_name _;

    # 前端 - 扫码点餐
    location / {
        root /opt/restaurant-system/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 管理后台
    location /admin {
        alias /opt/restaurant-system/admin/dist;
        try_files $uri $uri/ /admin/index.html;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
    }

    # WebSocket 支持
    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    # API 文档
    location /docs {
        proxy_pass http://127.0.0.1:8001;
    }
}
EOF

# 测试配置
nginx -t

# 重启 Nginx
systemctl restart nginx
```

### 第七步：重启后端服务

```bash
cd /opt/restaurant-system

# 停止现有服务
pkill -f "uvicorn"

# 重新启动服务
export PYTHONPATH=/opt/restaurant-system/src:$PYTHONPATH
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 > /tmp/app.log 2>&1 &

# 等待服务启动
sleep 3

# 检查服务状态
ps aux | grep uvicorn
tail -20 /tmp/app.log
```

### 第八步：验证部署

```bash
# 1. 检查前端
curl -I http://129.226.196.76/

# 2. 检查管理后台
curl -I http://129.226.196.76/admin/

# 3. 检查 API
curl http://129.226.196.76/api/menu/?store_id=1

# 4. 检查新 API
curl http://129.226.196.76/api/stats/overview
```

---

## 📱 访问地址

| 页面 | 地址 | 说明 |
|------|------|------|
| 扫码点餐 | http://129.226.196.76/?table=1&store=1 | 1 号桌点餐 |
| 管理后台 | http://129.226.196.76/admin | 管理员登录 |
| API 文档 | http://129.226.196.76/docs | Swagger 文档 |

---

## 🔑 测试账号

```
用户名：admin
密码：admin123
角色：系统管理员
```

---

## 🆕 新增功能说明

### 1. 数据统计 API

```
GET /api/stats/overview        # 概览统计
GET /api/stats/top-items       # 热门菜品
GET /api/stats/revenue-trend   # 营收趋势
```

### 2. 库存管理 API

```
GET  /api/menu/{id}/stock              # 获取库存
PUT  /api/menu/{id}/stock              # 更新库存
GET  /api/menu/low-stock               # 低库存列表
POST /api/menu/{id}/restock            # 补货
GET  /api/menu/stock-summary           # 库存汇总
```

### 3. 会员管理 API

```
GET    /api/members/me                  # 我的会员信息
GET    /api/members/{user_id}           # 获取会员信息
POST   /api/members/{id}/points/add    # 添加积分
POST   /api/members/{id}/points/deduct # 扣除积分
GET    /api/members/list                # 会员列表
GET    /api/members/rankings            # 会员排行榜
```

### 4. WebSocket 实时通信

```
WS /ws/orders?store_id=1           # 订单实时推送
WS /ws/table/{table_id}?store_id=1  # 桌台订单推送
```

### 5. 小票打印 API

```
POST   /api/receipt/print           # 打印小票
GET    /api/receipt/{id}/preview    # 预览小票
POST   /api/receipt/batch-print     # 批量打印
```

---

## 🎨 管理后台功能

### 数据统计
- 今日订单数、今日营收
- 待处理订单数量
- 订单状态分布
- 营收趋势图表
- 热门菜品排行

### 订单管理
- 查看所有订单
- 更新订单状态
- 查看订单详情
- 实时刷新（30秒）

### 菜单管理
- 添加菜品
- 编辑菜品
- 删除菜品
- 更新库存
- 上架/下架

---

## ⚠️ 常见问题

### Q1: npm install 失败

```bash
# 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs
```

### Q2: 构建后页面空白

```bash
# 检查 Nginx 配置
nginx -t

# 查看错误日志
tail -f /var/log/nginx/error.log
```

### Q3: WebSocket 连接失败

```bash
# 检查 Nginx 配置是否包含 WebSocket 支持
# 确保配置中有以下内容：
# proxy_http_version 1.1;
# proxy_set_header Upgrade $http_upgrade;
# proxy_set_header Connection "upgrade";
```

### Q4: 后端服务启动失败

```bash
# 查看日志
tail -50 /tmp/app.log

# 检查端口占用
netstat -tlnp | grep 8001
```

---

## 📊 部署检查清单

- [ ] 所有前端文件已上传
- [ ] 所有后端扩展文件已上传
- [ ] 数据库模型已更新
- [ ] 数据库迁移已执行
- [ ] 前端依赖已安装
- [ ] 管理后台依赖已安装
- [ ] 前端已构建
- *管理后台已构建
- [ ] Nginx 配置已更新
- [ ] 后端服务已重启
- [ ] 可以访问扫码点餐页面
- [ ] 可以访问管理后台
- [ ] API 接口正常
- [ ] WebSocket 连接正常

---

## 🎉 部署完成！

完成上述步骤后，您的多店铺扫码点餐系统就全部部署完成了！

**系统包含：**
- ✅ 扫码点餐前端（Vue.js 3）
- ✅ 管理后台（Vue.js 3 + Element Plus）
- ✅ 完整后端 API（FastAPI）
- ✅ 数据统计功能
- ✅ 库存管理功能
- ✅ 会员积分功能
- ✅ WebSocket 实时通信
- ✅ 小票打印功能

**访问地址：**
- 点餐：http://129.226.196.76/?table=1&store=1
- 后台：http://129.226.196.76/admin
- 文档：http://129.226.196.76/docs

**测试账号：admin / admin123**

---

🚀 **祝使用愉快！**
