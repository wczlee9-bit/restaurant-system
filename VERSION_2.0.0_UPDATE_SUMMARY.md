# 餐饮点餐系统 v2.0.0 升级总结

## 版本信息
- **版本号**: v2.0.0
- **发布日期**: 2026-01-09
- **升级内容**: 增加菜品图片上传、会员二维码生成、优惠配置系统

---

## 新增功能

### 1. 菜品图片上传功能
- **功能描述**: 支持为菜品上传图片（JPEG、PNG、GIF格式）
- **存储方式**: 图片存储在S3对象存储中
- **API接口**: `POST /api/menu-items/{item_id}/upload-image`
- **前端页面**: 菜品管理页面（menu_management.html）
- **技术特点**:
  - 自动生成签名URL，有效期1年
  - 支持文件类型验证
  - 图片自动关联到菜品

### 2. 会员二维码生成功能
- **功能描述**: 为会员生成专属二维码，支持扫描识别
- **有效期**: 默认30天，可自定义
- **API接口**:
  - `GET /api/member/{member_id}/qrcode` - 获取会员二维码
  - `POST /api/member/verify` - 验证会员（支持二维码和手机号）
- **前端页面**: 会员中心（member_center.html）
- **技术特点**:
  - 二维码包含会员ID和时间戳
  - 支持下载和打印
  - 记录扫描次数和扫描时间

### 3. 优惠配置系统
- **功能描述**: 灵活配置店铺优惠规则，支持多种优惠类型
- **优惠类型**:
  - 百分比折扣（如打9折）
  - 固定金额减免（如减免10元）
  - 积分抵扣（如100积分抵扣1元）
- **API接口**:
  - `POST /api/discount-config` - 创建优惠配置
  - `GET /api/discount-config` - 获取优惠列表
  - `PATCH /api/discount-config/{id}` - 更新优惠配置
  - `DELETE /api/discount-config/{id}` - 删除优惠配置
  - `POST /api/discount/apply` - 应用优惠（自动计算最优优惠）
- **前端页面**: 优惠管理（discount_management.html）
- **技术特点**:
  - 支持店铺级和公司级优惠
  - 可设置最低消费、最大优惠、适用等级等条件
  - 支持有效期设置
  - 自动应用最优优惠

---

## 数据库变更

### 新增表结构

#### 1. discount_config（优惠配置表）
```sql
CREATE TABLE discount_config (
    id SERIAL PRIMARY KEY,
    store_id INTEGER REFERENCES stores(id) ON DELETE CASCADE,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    discount_type VARCHAR(50) NOT NULL,  -- percentage, fixed, points
    discount_value DOUBLE PRECISION NOT NULL,
    min_amount DOUBLE PRECISION,
    max_discount DOUBLE PRECISION,
    member_level INTEGER,
    points_required INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    valid_from TIMESTAMP,
    valid_until TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    description TEXT,
    updated_at TIMESTAMP
);
```

#### 2. member_qrcodes（会员二维码表）
```sql
CREATE TABLE member_qrcodes (
    id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    qr_code_url VARCHAR(500) NOT NULL,
    qr_code_key VARCHAR(255) NOT NULL,
    valid_from TIMESTAMP NOT NULL DEFAULT NOW(),
    valid_until TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    scan_count INTEGER NOT NULL DEFAULT 0,
    last_scan_time TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    UNIQUE (member_id)
);
```

---

## 代码变更

### 新增文件
1. `scripts/migrate_add_discount_and_qrcode.py` - 数据库迁移脚本
2. `assets/discount_management.html` - 优惠管理界面

### 修改文件
1. `src/api/restaurant_enhanced_api.py` - 增强API服务（已存在，无需修改）
2. `assets/member_center.html` - 会员中心（已包含二维码功能，无需修改）
3. `assets/portal.html` - 门户页面（已包含优惠管理入口，无需修改）
4. `netlify.toml` - Netlify配置（已包含增强API代理，无需修改）
5. `scripts/start_api_services.py` - 启动脚本（已包含增强API启动，无需修改）

### 修复文件
1. `src/tools/order_management_tool.py` - 修复导入错误（Order -> Orders）
2. `src/tools/revenue_analysis_tool.py` - 修复导入错误（Order -> Orders）

---

## 部署步骤

### 1. 数据库迁移
```bash
cd /workspace/projects
PYTHONPATH=/workspace/projects/src python scripts/migrate_add_discount_and_qrcode.py
```

### 2. 启动增强API服务
```bash
python scripts/start_api_services.py
```

或单独启动增强API：
```bash
cd /workspace/projects/src
PYTHONPATH=/workspace/projects/src python -m uvicorn api.restaurant_enhanced_api:app --host 0.0.0.0 --port 8007
```

### 3. 部署前端到Netlify
使用拖拽部署方式：
1. 登录Netlify（https://app.netlify.com）
2. 创建新站点或选择现有站点
3. 将 `assets` 目录拖拽到Netlify部署区域
4. 等待部署完成

### 4. 验证部署
- 访问门户页面
- 测试优惠管理功能
- 测试会员二维码生成
- 测试菜品图片上传

---

## API服务端口分配

| 服务名称 | 端口 | 说明 |
|---------|------|------|
| 餐饮系统完整API | 8000 | 核心API服务 |
| 会员API | 8004 | 会员管理API |
| 总公司管理API | 8006 | 总公司后台API |
| **餐饮系统增强API** | **8007** | 菜品图片、会员二维码、优惠系统（新增） |

---

## Netlify配置更新

netlify.toml 已包含以下配置：
- 增强API代理：`/api/enhanced*` -> `http://115.191.1.219:8007/api/:splat`
- 优惠管理路由：`/discount-management` -> `/discount_management.html`
- 缓存策略和安全头部

---

## 测试结果

### 1. 健康检查
```bash
curl http://localhost:8007/health
# 返回: {"status":"ok","message":"餐饮系统增强API服务运行正常"}
```

### 2. 获取优惠配置列表
```bash
curl http://localhost:8007/api/discount-config
# 返回: [] (空列表，表示API正常工作)
```

### 3. 数据库迁移
```bash
python scripts/migrate_add_discount_and_qrcode.py
# 返回: ✅ 数据库迁移成功完成！
```

---

## 使用指南

### 1. 上传菜品图片
1. 进入菜品管理页面
2. 选择要上传图片的菜品
3. 点击"上传图片"按钮
4. 选择图片文件（JPEG、PNG、GIF）
5. 点击确定，图片将自动上传并显示

### 2. 生成会员二维码
1. 进入会员中心
2. 登录会员账号
3. 点击"查看我的会员二维码"
4. 二维码将自动生成
5. 可以下载保存或直接展示

### 3. 配置优惠规则
1. 进入优惠管理页面
2. 点击"创建优惠"
3. 填写优惠信息：
   - 优惠类型（百分比、固定金额、积分抵扣）
   - 优惠值
   - 最低消费（可选）
   - 最大优惠（可选）
   - 适用会员等级（可选）
   - 所需积分（可选）
   - 生效/到期日期（可选）
   - 优惠描述
4. 点击确定创建优惠

### 4. 应用优惠
系统会自动计算最优优惠：
- 会员等级折扣
- 积分抵扣（1积分=0.01元）
- 自定义优惠配置

---

## 注意事项

1. **S3对象存储**: 确保环境变量 `COZE_BUCKET_ENDPOINT_URL` 和 `COZE_BUCKET_NAME` 已正确配置
2. **端口占用**: 确保8007端口未被占用
3. **数据库连接**: 确保PostgreSQL数据库可访问
4. **Netlify代理**: 更新netlify.toml中的后端IP地址为实际部署地址
5. **图片格式**: 只支持JPEG、PNG、GIF格式
6. **二维码有效期**: 默认30天，到期后需重新生成
7. **优惠叠加**: 会员等级折扣、积分抵扣、自定义优惠会叠加应用

---

## 版本兼容性

- **后端API**: Python 3.9+
- **数据库**: PostgreSQL 13+
- **前端**: 现代浏览器（Chrome、Firefox、Safari、Edge）
- **Netlify**: 无需特殊配置

---

## 更新日志

### v2.0.0 (2026-01-09)
- 新增菜品图片上传功能
- 新增会员二维码生成和验证功能
- 新增优惠配置系统
- 创建优惠管理界面
- 数据库新增2张表（discount_config、member_qrcodes）
- 增强API服务运行在8007端口

---

## 技术支持

如有问题，请联系技术支持或查看以下文档：
- 部署文档：DEPLOYMENT_GUIDE.md
- Netlify部署：NETLIFY_DEPLOYMENT.md
- 用户手册：USER_MANUAL.md
