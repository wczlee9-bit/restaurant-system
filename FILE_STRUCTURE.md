# 📁 餐饮点餐系统 - 文件结构指南

## 🎯 核心文件（测试必看）

### 测试入口文件

```
assets/
├── index.html                          ⭐ 主入口（从这里开始）
│   └── 桌号选择 + 一键测试
│
├── restaurant_full_test.html            ⭐ 全流程测试页面
│   └── 5角色无缝切换 + 完整业务流程
│
└── qrcodes/
    ├── table_1.png ~ table_10.png      桌号二维码
    └── 模拟扫码场景
```

### 指南文档

```
项目根目录/
├── TESTING_GUIDE.md                    ⭐ 完整测试方案
│   └── 三种测试方式 + 详细流程
│
assets/
├── QUICK_TEST_GUIDE.md                 ⭐ 快速测试指南
│   └── 30秒开始测试
│
└── ACCESS_GUIDE.md                     访问指南（外部访问用）
```

---

## 📂 完整文件树

```
/workspace/projects/
│
├── 📄 TESTING_GUIDE.md                 ⭐ 从这里看测试方案
├── 📄 README_TEST.md                   测试系统说明
├── 📄 TEST_REPORT.md                   测试报告
│
├── 📁 assets/                          资源目录
│   ├── 📄 index.html                   ⭐ 【从这里开始】
│   ├── 📄 restaurant_full_test.html    ⭐ 全流程测试页面
│   │
│   ├── 📄 QUICK_TEST_GUIDE.md          快速测试指南
│   ├── 📄 ACCESS_GUIDE.md              访问指南
│   ├── 📄 TEST_SYSTEM_GUIDE.md         系统指南
│   │
│   └── 📁 qrcodes/                     二维码目录
│       ├── table_1.png
│       ├── table_2.png
│       ├── ...
│       └── table_10.png
│
├── 📁 scripts/                         脚本目录
│   ├── init_test_data_full.py          初始化测试数据
│   ├── generate_qrcodes.py             生成二维码
│   ├── quick_test.py                   快速功能测试
│   └── check_services.sh               服务诊断工具
│
├── 📁 src/                             源代码目录
│   ├── 📁 api/                         API接口
│   │   └── restaurant_api.py           餐厅API
│   ├── 📁 models/                      数据模型
│   └── 📁 utils/                       工具类
│
└── 📁 config/                          配置目录
    └── agent_llm_config.json          LLM配置
```

---

## 🚀 快速开始（3步）

### 第1步：查看测试方案

**文件**：`TESTING_GUIDE.md`

**内容**：
- ✅ 三种测试方式
- ✅ 完整测试流程（8号桌）
- ✅ 技术细节说明

---

### 第2步：进入测试页面

**文件**：`assets/index.html`

**操作**：
1. 点击打开 `assets/index.html`
2. 点击大按钮：**⚡ 立即测试8号桌完整流程**
3. 开始测试！

---

### 第3步：使用全流程测试

**文件**：`assets/restaurant_full_test.html`

**角色切换**：
- 👤 顾客：点餐
- 👨‍🍳 厨师：制作
- 🤵 传菜员：上菜
- 💰 收银员：结账
- 👔 店长：管理

---

## 📋 文件分类

### 🎮 测试相关

| 文件 | 路径 | 说明 |
|------|------|------|
| **主入口** | `assets/index.html` | 桌号选择 + 一键测试 |
| **测试页面** | `assets/restaurant_full_test.html` | 全流程测试页面 |
| **二维码** | `assets/qrcodes/table_*.png` | 1-10号桌二维码 |

### 📖 指南文档

| 文件 | 路径 | 说明 |
|------|------|------|
| **测试方案** | `TESTING_GUIDE.md` | 完整测试方案 |
| **快速指南** | `assets/QUICK_TEST_GUIDE.md` | 30秒开始测试 |
| **访问指南** | `assets/ACCESS_GUIDE.md` | 外部访问指南 |

### 🔧 工具脚本

| 文件 | 路径 | 说明 |
|------|------|------|
| **初始化数据** | `scripts/init_test_data_full.py` | 初始化测试数据 |
| **生成二维码** | `scripts/generate_qrcodes.py` | 生成桌号二维码 |
| **快速测试** | `scripts/quick_test.py` | API功能测试 |
| **服务诊断** | `scripts/check_services.sh` | 检查服务状态 |

---

## 💡 如何找到文件

### 方式1：使用文件树（IDE左侧）

1. 展开项目根目录
2. 展开 `assets/` 文件夹
3. 找到 `index.html` 或 `restaurant_full_test.html`

### 方式2：使用搜索功能

1. 按 `Ctrl + P`（VSCode风格）
2. 输入文件名：
   - `index.html`
   - `restaurant_full_test.html`
   - `TESTING_GUIDE.md`

### 方式3：使用命令行

```bash
# 列出所有HTML文件
find /workspace/projects/assets -name "*.html"

# 查看测试指南
cat /workspace/projects/TESTING_GUIDE.md
```

---

## ⚠️ 重要提示

### 核心测试文件（仅需关注3个）

```
1. TESTING_GUIDE.md           → 看文档
2. assets/index.html          → 点这里开始
3. assets/restaurant_full_test.html  → 完整测试
```

### 可以忽略的文件

- 其他HTML测试页面（已整合到restaurant_full_test.html）
- 详细的技术文档（测试时不需要）
- 旧版测试文件

---

## 🎯 推荐测试流程

```
1. 阅读：TESTING_GUIDE.md（了解测试方案）
2. 打开：assets/index.html（进入测试页面）
3. 点击：⚡ 立即测试8号桌完整流程
4. 按照5个角色顺序测试：
   👤 顾客 → 👨‍🍳 厨师 → 🤵 传菜员 → 💰 收银员 → 👔 店长
```

---

## 📞 需要帮助？

### 如果找不到文件

1. 确认在 `/workspace/projects/` 目录
2. 使用搜索功能（Ctrl+P）
3. 查看上面的文件树

### 如果不知道从哪里开始

1. 打开 `TESTING_GUIDE.md`
2. 按照文档指引操作

---

**🎮 现在开始测试吧！从 `assets/index.html` 开始！**
