# 📦 Netlify 部署文件清单

## 🚀 核心必传文件（必须上传）

### 🎯 主要入口页面（4个）
| 文件名 | 大小 | 用途 | 优先级 |
|--------|------|------|--------|
| **portal.html** | 8.5K | 主门户页面（推荐入口） | ⭐⭐⭐⭐⭐ |
| **index.html** | 12K | 原始测试入口 | ⭐⭐⭐⭐ |
| **login_standalone.html** | 16K | 工作人员登录页面 | ⭐⭐⭐⭐⭐ |
| **test.html** | 469B | 部署测试页面（新增） | ⭐⭐⭐ |

### 👤 顾客端页面（2个）
| 文件名 | 大小 | 用途 | 优先级 |
|--------|------|------|--------|
| **customer_order_v2.html** | 31K | 顾客点餐页面（最新版） | ⭐⭐⭐⭐⭐ |
| **customer_order.html** | 31K | 顾客点餐页面（旧版） | ⭐⭐⭐ |

### 👥 工作人员端页面（1个）
| 文件名 | 大小 | 用途 | 优先级 |
|--------|------|------|--------|
| **staff_workflow.html** | 51K | 工作人员管理界面（多角色） | ⭐⭐⭐⭐⭐ |

### ⚙️ 管理页面（2个）
| 文件名 | 大小 | 用途 | 优先级 |
|--------|------|------|--------|
| **shop_settings.html** | 53K | 店铺设置（桌号、二维码、支付配置） | ⭐⭐⭐⭐⭐ |
| **menu_management.html** | 28K | 菜品管理界面 | ⭐⭐⭐⭐ |

### 🧪 API测试页面（1个）
| 文件名 | 大小 | 用途 | 优先级 |
|--------|------|------|--------|
| **api_test.html** | 14K | API连接测试工具 | ⭐⭐⭐⭐ |

### 📁 config 目录
| 文件名 | 大小 | 用途 | 优先级 |
|--------|------|------|--------|
| **config/users.json** | - | 用户配置（可选） | ⭐⭐ |

---

## 📚 可选文件（可根据需要选择）

### 🧪 完整测试页面（2个）
| 文件名 | 大小 | 用途 |
|--------|------|------|
| restaurant_full_test.html | 63K | 完整测试系统（旧版） |
| restaurant_test_system.html | 72K | 完整测试系统（新版） |

### 📋 其他管理页面（3个）
| 文件名 | 大小 | 用途 |
|--------|------|------|
| inventory_management.html | 40K | 物料库存管理 |
| order_flow_config.html | 23K | 订单流程配置 |
| menu_management.html | 28K | 菜品管理 |

### 📚 文档页面（多个）
| 文件名 | 大小 | 用途 |
|--------|------|------|
| ACCESS_GUIDE.html | 17K | 访问指南 |
| LOCALHOST_ACCESS.html | 9.8K | 本地访问指南 |
| deploy_to_netlify.html | 19K | 部署指南 |
| netlify_deployment_quickref.html | 13K | 快速部署参考 |

### 🧪 测试工具页面（多个）
| 文件名 | 大小 | 用途 |
|--------|------|------|
| test_dashboard.html | 64K | 测试仪表板 |
| test_customer_flow.html | 7.7K | 顾客流程测试 |
| test_login.html | 11K | 登录测试 |

### 📁 qrcodes 目录（二维码图片）
- 包含生成的桌号二维码图片
- 可选上传

---

## ❌ 不建议上传的文件

### 备份文件（.bak 扩展名）
```
customer_order.html.bak
index.html.bak
login.html.bak
shop_settings.html.bak
staff_workflow.html.bak
restaurant_full_test.html.bak
restaurant_test_system.html.bak
deploy_to_netlify.html.bak
netlify_deployment_quickref.html.bak
```

### Markdown 文档文件（.md 扩展名）
```
ACCESS_GUIDE.md
FEATURE_UPDATE_20240108.md
QUICK_START.md
QUICK_TEST_GUIDE.md
README_TEST_SYSTEM.md
TEST_SYSTEM_GUIDE.md
```

### 测试和开发页面
```
coze_test_dashboard.html
kitchen_display.html
order.html
```

---

## ✅ 推荐的最小部署包

### 方案A：核心功能包（约 180KB）
```
必传文件：
- portal.html (8.5K)
- index.html (12K)
- login_standalone.html (16K)
- test.html (469B)
- customer_order_v2.html (31K)
- staff_workflow.html (51K)
- shop_settings.html (53K)
- api_test.html (14K)

总计：约 180KB
```

### 方案B：完整功能包（约 320KB）
```
核心功能包 +
- menu_management.html (28K)
- inventory_management.html (40K)
- order_flow_config.html (23K)
- restaurant_test_system.html (72K)

总计：约 320KB
```

---

## 🚀 部署步骤

### 1️⃣ 准备上传文件

**最小部署（推荐测试用）：**
```
选中这些文件：
✓ portal.html
✓ index.html
✓ login_standalone.html
✓ test.html
✓ customer_order_v2.html
✓ staff_workflow.html
✓ shop_settings.html
✓ api_test.html
```

**完整部署（推荐生产用）：**
```
最小部署文件 +
✓ menu_management.html
✓ inventory_management.html
✓ order_flow_config.html
✓ restaurant_test_system.html
```

### 2️⃣ 上传到 Netlify

1. 打开 https://app.netlify.com
2. 点击 "Add new site" → "Deploy manually"
3. **同时拖拽**：
   - 选中的所有 HTML 文件
   - `netlify-simple.toml` 配置文件
4. 等待 1-2 分钟完成部署

### 3️⃣ 验证部署

**测试顺序：**
1. `https://你的域名.netlify.app/test.html` - 基础测试
2. `https://你的域名.netlify.app/portal.html` - 门户页面
3. `https://你的域名.netlify.app/api_test.html` - API 连接测试

---

## 📊 文件优先级说明

| 优先级 | 说明 | 文件类型 |
|--------|------|----------|
| ⭐⭐⭐⭐⭐ | 必须上传 | portal.html, customer_order_v2.html, staff_workflow.html, shop_settings.html, login_standalone.html |
| ⭐⭐⭐⭐ | 强烈推荐 | index.html, api_test.html |
| ⭐⭐⭐ | 可选 | menu_management.html, inventory_management.html, restaurant_test_system.html |
| ⭐⭐ | 可选 | 文档页面、测试页面 |
| ⭐ | 不建议 | .bak 备份文件, .md 文档 |

---

## 💡 最佳实践

### 初次部署
1. 使用**最小部署包**测试
2. 验证基础功能正常
3. 再添加其他管理页面

### 生产部署
1. 使用**完整功能包**
2. 包含所有管理页面
3. 确保配置文件正确

### 更新部署
1. 只上传修改过的文件
2. Netlify 会自动增量更新
3. 无需重新上传全部文件

---

## 🎯 快速开始

**现在就动手：**

1. 下载这份文件清单
2. 在文件管理器中打开 `/workspace/projects/assets/`
3. 对照清单，选择要上传的文件
4. 拖拽到 Netlify 上传区域
5. 等待部署完成

**就这么简单！** 🎉
