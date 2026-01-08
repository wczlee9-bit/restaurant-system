# Netlify 部署说明

## 更新内容

本次更新包含了订单流程配置系统的重构，新增了以下文件：

### 新增文件
- `assets/order_flow_config.html` - 灵活的订单流程配置页面
- `scripts/migrate_to_flexible_workflow.py` - 数据库迁移脚本
- `scripts/test_order_flow_api.py` - API 测试脚本
- `src/api/order_flow_api.py` - 订单流程配置 API

### 修改文件
- `src/storage/database/shared/model.py` - 数据库模型更新
- `src/api/restaurant_api.py` - 注册新的 API 路由
- `assets/shop_settings.html` - 添加灵活配置入口

## 部署步骤

### 1. Netlify 自动部署

由于已经将代码推送到 GitHub，Netlify 会自动检测到更改并触发重新部署。

- Netlify 网站：https://tiny-sprite-65833c.netlify.app
- 预计部署时间：1-3 分钟

### 2. 手动拖拽部署（如果自动部署失败）

如果自动部署失败或需要立即部署，可以手动拖拽部署：

1. 在本地项目根目录执行：
   ```bash
   # 打包需要部署的文件
   zip -r restaurant-deploy.zip assets/*.html netlify.toml
   ```

2. 访问 Netlify 控制台：https://app.netlify.com/

3. 进入你的站点设置

4. 拖拽 `restaurant-deploy.zip` 文件到部署区域

## 验证部署

部署完成后，访问以下链接验证：

1. **主页面**：https://tiny-sprite-65833c.netlify.app/portal.html
2. **店铺设置**：https://tiny-sprite-65833c.netlify.app/shop_settings.html
3. **订单流程配置**：https://tiny-sprite-65833c.netlify.app/order_flow_config.html

## 数据库迁移

部署前端页面后，还需要执行数据库迁移：

```bash
# 在服务器上执行数据库迁移
python scripts/migrate_to_flexible_workflow.py
```

## 新功能说明

### 灵活角色管理

- **自定义角色**：支持创建、编辑、删除角色
- **角色描述**：每个角色可以添加描述信息
- **启用/禁用**：可以禁用角色而不删除

### 灵活功能分配

- **订单状态分配**：将订单状态（待确认、制作中、待传菜、上菜中、已完成）分配给任意角色
- **操作方式配置**：每个角色对每个状态的操作方式可独立配置
  - 逐项确认：每道菜单独确认
  - 订单确认：整个订单一起确认
  - 自动跳过：该角色不需要处理此状态
  - 忽略不显示：可以看到但不需要操作

### 使用场景示例

1. **不使用传菜员**：
   - 删除或禁用"传菜员"角色
   - 将"待传菜"和"上菜中"状态分配给收银员

2. **一个角色多个功能**：
   - 收银员可以同时负责"待传菜"、"上菜中"、"已完成"等状态

3. **不同店铺不同配置**：
   - 每个店铺可以有独立的角色配置和流程配置

## 测试 API

测试新 API：

```bash
python scripts/test_order_flow_api.py
```

## 注意事项

1. 执行数据库迁移前请备份数据库
2. 迁移会删除旧的 `workflow_config` 表，如有自定义配置请先导出
3. 新功能需要后端 API 服务支持，确保后端服务正在运行

## 后续步骤

1. ✅ 代码已推送到 GitHub
2. ⏳ 等待 Netlify 自动部署完成（1-3分钟）
3. ⏳ 执行数据库迁移脚本
4. ✅ 测试新功能是否正常工作
