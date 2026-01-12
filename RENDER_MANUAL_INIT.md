# Render 手动数据初始化方案

如果自动初始化失败，请在 Render 控制台手动执行以下命令：

## 步骤 1：进入 Render Shell

1. 登录 Render 控制台
2. 进入你的 Web Service：`restaurant-system-vzj0`
3. 点击 "Shell" 按钮
4. 进入命令行界面

## 步骤 2：进入项目目录并初始化数据

```bash
# 进入项目目录
cd /opt/render/project/src

# 初始化数据库（创建表结构）
python -c "from storage.database.init_db import init_database; init_database()"

# 初始化测试数据
python -c "from storage.database.init_db import ensure_test_data; ensure_test_data()"
```

## 步骤 3：验证数据

```bash
# 检查数据库连接
python -c "from storage.database.db import get_session; from storage.database.shared.model import Stores, MenuItems, Tables; db = get_session(); print(f'Stores: {db.query(Stores).count()}, MenuItems: {db.query(MenuItems).count()}, Tables: {db.query(Tables).count()}')"
```

## 步骤 4：测试 API

```bash
# 测试健康检查
curl http://localhost:10000/api/diagnostic/health

# 测试菜品接口
curl http://localhost:10000/api/menu-items/
```

## 预期输出

- Stores: 1
- MenuItems: 18
- Tables: 10

## 故障排查

如果初始化失败，请检查：
1. 数据库连接是否正常：`print(os.getenv('PGDATABASE_URL'))`
2. 表结构是否创建成功
3. 是否有外键约束错误

## 重新初始化（如需要）

```bash
# 删除所有表并重新初始化
python -c "
from storage.database.db import get_engine
from storage.database.shared.model import Base
engine = get_engine()
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
from storage.database.init_db import ensure_test_data
ensure_test_data()
"
```

## 完成后

1. 退出 Shell：`exit`
2. 刷新前端页面测试
3. 检查是否正常显示菜品
