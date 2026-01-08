# 🍽️ 餐饮点餐系统 - 测试入口

## ⚡ 快速开始（30秒测试）

### 🎯 测试入口

**文件位置**：`assets/index.html`

**打开方式**：
1. 在左侧文件树中找到 `assets/` 文件夹
2. 双击打开 `index.html`
3. 点击页面中的 **"⚡ 立即测试8号桌完整流程"** 按钮
4. 开始测试！

---

## 📋 核心文件

| 文件 | 位置 | 说明 |
|------|------|------|
| **📄 OPEN_FILE_GUIDE.txt** | 项目根目录 | 如何打开文件的详细指南 |
| **📄 HOW_TO_OPEN_FILES.md** | 项目根目录 | 打开文件的操作说明 |
| **📄 START_HERE.md** | 项目根目录 | 快速入门指南 |
| **📄 TESTING_GUIDE.md** | 项目根目录 | 完整测试方案 |
| **📱 index.html** | assets/ | 测试入口页面 |

---

## ⚠️ 重要提示

**不要**在搜索引擎中搜索 "assets/index.html"！

- 搜索引擎无法访问沙盒环境
- 搜索结果与您的测试系统无关
- 请直接在左侧文件树中打开文件

---

## 📂 项目结构

```
/workspace/projects/
│
├── 📄 README.md                  ← 你现在看的文件
├── 📄 OPEN_FILE_GUIDE.txt        ← 如何打开文件（必看）
├── 📄 HOW_TO_OPEN_FILES.md       ← 详细操作说明
├── 📄 START_HERE.md              ← 快速入门
├── 📄 TESTING_GUIDE.md          ← 完整测试方案
│
├── 📁 assets/
│   ├── 📄 index.html  ← 【双击打开这个文件开始测试】
│   ├── 📄 restaurant_full_test.html
│   ├── 📄 QUICK_TEST_GUIDE.md
│   └── 📁 qrcodes/
│       └── table_1.png ~ table_10.png
│
├── 📁 scripts/
│   ├── generate_qrcodes.py       # 生成二维码
│   └── quick_test.py             # 快速测试
│
└── 📁 src/                       ← 源代码（测试时不需要）
```

---

## 🎮 测试流程

```
1. 打开 assets/index.html
2. 点击 "⚡ 立即测试8号桌完整流程"
3. 按照5个角色顺序测试：
   👤 顾客 → 👨‍🍳 厨师 → 🤵 传菜员 → 💰 收银员 → 👔 店长
```

---

## 📖 详细文档

- **OPEN_FILE_GUIDE.txt**：如何在沙盒中打开文件（必看）
- **HOW_TO_OPEN_FILES.md**：打开文件的详细操作说明
- **START_HERE.md**：快速入门指南
- **TESTING_GUIDE.md**：完整测试方案和流程

---

# 项目结构说明（开发者参考）

# 本地运行
## 运行流程
bash scripts/local_run.sh -m flow

## 运行节点
bash scripts/local_run.sh -m node -n node_name

# 启动HTTP服务
bash scripts/http_run.sh -m http -p 5000

