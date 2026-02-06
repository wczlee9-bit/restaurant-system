# 🚀 从 Git 重新部署通讯服务指南

## 📋 概述

本文档说明如何从 Git 仓库拉取最新代码并重新部署通讯服务。

---

## 🎯 部署目标

- **源码仓库**：https://github.com/wczlee9-bit/restaurant-system.git
- **部署服务器**：129.226.196.76
- **部署目录**：/opt/restaurant-system

---

## 📝 部署步骤

### 第一步：服务器准备

```bash
# SSH 连接到服务器
ssh root@129.226.196.76

# 进入项目目录
cd /opt/restaurant-system

# 查看当前状态
git status
```

### 第二步：拉取最新代码

```bash
# 拉取最新代码
git pull origin main

# 查看更新内容
git log --oneline -5
```

### 第三步：安装依赖

```bash
# 如果有新的 Python 依赖
pip install -r requirements.txt

# 如果前端有新的依赖
cd frontend && npm install && npm run build && cd ..
cd admin && npm install && npm run build && cd ..
```

### 第四步：数据库迁移（如需要）

```bash
# 如果有数据库变更，执行迁移
cd backend_extensions

# 初始化测试数据库（如果需要）
export PYTHONPATH=/opt/restaurant-system/backend_extensions/src:$PYTHONPATH
python3 init_test_db.py

# 或者执行生产数据库迁移
# python3 -m migrations.migrate
```

### 第五步：重启服务

```bash
# 停止当前服务
pkill -f "uvicorn"

# 等待进程完全停止
sleep 3

# 启动新版本
cd /opt/restaurant-system
export PYTHONPATH=/opt/restaurant-system/src:$PYTHONPATH
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 > /tmp/app.log 2>&1 &

# 或者使用 systemd（推荐）
# systemctl restart restaurant-system
```

### 第六步：验证部署

```bash
# 检查服务状态
ps aux | grep uvicorn

# 查看日志
tail -20 /tmp/app.log

# 检查 API
curl http://localhost:8001/health

# 检查前端
curl -I http://localhost/

# 检查管理后台
curl -I http://localhost/admin/
```

---

## 🔄 完整部署脚本

创建 `deploy.sh` 脚本：

```bash
#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}   从 Git 重新部署通讯服务${NC}"
echo -e "${YELLOW}========================================${NC}"

# 1. 进入项目目录
cd /opt/restaurant-system || exit 1
echo -e "${GREEN}✅ 进入项目目录${NC}"

# 2. 拉取最新代码
echo -e "${YELLOW}正在拉取最新代码...${NC}"
git pull origin main
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 拉取代码失败${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 代码拉取成功${NC}"

# 3. 安装 Python 依赖
echo -e "${YELLOW}正在安装 Python 依赖...${NC}"
pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 安装依赖失败${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 依赖安装成功${NC}"

# 4. 构建前端
echo -e "${YELLOW}正在构建前端...${NC}"
cd frontend
npm install -q
npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 前端构建失败${NC}"
    exit 1
fi
cd ..
echo -e "${GREEN}✅ 前端构建成功${NC}"

# 5. 构建管理后台
echo -e "${YELLOW}正在构建管理后台...${NC}"
cd admin
npm install -q
npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 管理后台构建失败${NC}"
    exit 1
fi
cd ..
echo -e "${GREEN}✅ 管理后台构建成功${NC}"

# 6. 停止服务
echo -e "${YELLOW}正在停止服务...${NC}"
pkill -f "uvicorn"
sleep 3
echo -e "${GREEN}✅ 服务已停止${NC}"

# 7. 启动服务
echo -e "${YELLOW}正在启动服务...${NC}"
export PYTHONPATH=/opt/restaurant-system/src:$PYTHONPATH
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 > /tmp/app.log 2>&1 &
sleep 3

# 8. 验证服务
if ps aux | grep -v grep | grep uvicorn > /dev/null; then
    echo -e "${GREEN}✅ 服务启动成功${NC}"
else
    echo -e "${RED}❌ 服务启动失败${NC}"
    tail -20 /tmp/app.log
    exit 1
fi

# 9. 健康检查
echo -e "${YELLOW}正在进行健康检查...${NC}"
sleep 2
response=$(curl -s http://localhost:8001/health)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 健康检查通过${NC}"
    echo -e "${GREEN}响应: ${response}${NC}"
else
    echo -e "${RED}❌ 健康检查失败${NC}"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}访问地址：${NC}"
echo -e "  - 点餐页面: http://129.226.196.76/?table=1&store=1"
echo -e "  - 管理后台: http://129.226.196.76/admin"
echo -e "  - API 文档: http://129.226.196.76/docs"
```

使用方法：

```bash
# 添加执行权限
chmod +x deploy.sh

# 执行部署
./deploy.sh
```

---

## 🔍 部署验证清单

- [ ] 代码拉取成功
- [ ] 依赖安装成功
- [ ] 前端构建成功
- [ ] 管理后台构建成功
- [ ] 服务启动成功
- [ ] 健康检查通过
- [ ] 前端页面可访问
- [ ] 管理后台可访问
- [ ] API 接口正常

---

## 🚨 回滚方案

如果部署失败，需要回滚到之前的版本：

```bash
# 方法1: 回滚到上一个提交
git reset --hard HEAD~1

# 方法2: 回滚到指定提交
git reset --hard <commit-hash>

# 重新部署
./deploy.sh
```

---

## 📊 部署记录

| 部署时间 | Git Commit | 版本 | 部署人 | 状态 |
|---------|-----------|------|--------|------|
| 2025-02-06 22:56 | 375f5b8 | v1.0.0 | Coze Coding | ✅ 成功 |

---

## 📞 联系方式

如有问题，请联系：
- 开发团队：Coze Coding
- 文档：查看项目 README.md

---

**文档版本**：1.0.0  
**最后更新**：2025-02-06  
**维护者**：Coze Coding
