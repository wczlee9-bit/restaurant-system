#!/usr/bin/env python3
"""
初始化测试数据
"""

from storage.database.db_config import engine, SessionLocal
from storage.database.models import Base, User, Store, Table, MenuItem, Order, OrderItem
import hashlib

# 创建所有表
Base.metadata.create_all(bind=engine)
print("数据库表创建完成")

# 创建会话
db = SessionLocal()

try:
    # 检查是否已有数据
    existing_store = db.query(Store).first()
    if existing_store:
        print("数据库已有数据，跳过初始化")
        db.close()
        exit(0)

    # 创建简单的密码哈希
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    # 创建管理员用户
    admin_user = User(
        username="admin",
        hashed_password=hash_password("admin123"),
        role="admin",
        real_name="系统管理员"
    )
    db.add(admin_user)

    # 创建店铺
    store = Store(
        name="测试餐厅",
        address="测试地址123号",
        phone="13800138000"
    )
    db.add(store)
    db.flush()  # 获取 store.id

    # 创建桌台
    tables = []
    for i in range(1, 6):
        table = Table(
            store_id=store.id,
            table_number=str(i),
            capacity=4
        )
        tables.append(table)
        db.add(table)

    # 创建菜单项
    menu_items = [
        MenuItem(
            store_id=store.id,
            name="宫保鸡丁",
            description="经典川菜，香辣可口",
            price=38.0,
            category="热菜",
            stock=100,
            low_stock_threshold=10
        ),
        MenuItem(
            store_id=store.id,
            name="鱼香肉丝",
            description="酸甜口味，下饭神器",
            price=35.0,
            category="热菜",
            stock=100,
            low_stock_threshold=10
        ),
        MenuItem(
            store_id=store.id,
            name="麻婆豆腐",
            description="麻辣鲜香，经典名菜",
            price=28.0,
            category="热菜",
            stock=100,
            low_stock_threshold=10
        ),
        MenuItem(
            store_id=store.id,
            name="清蒸鲈鱼",
            description="新鲜鲈鱼，清蒸烹饪",
            price=88.0,
            category="海鲜",
            stock=50,
            low_stock_threshold=5
        ),
        MenuItem(
            store_id=store.id,
            name="西红柿炒鸡蛋",
            description="家常菜，简单美味",
            price=22.0,
            category="热菜",
            stock=100,
            low_stock_threshold=10
        ),
        MenuItem(
            store_id=store.id,
            name="蛋炒饭",
            description="经典炒饭，简单美味",
            price=18.0,
            category="主食",
            stock=100,
            low_stock_threshold=10
        ),
        MenuItem(
            store_id=store.id,
            name="可乐鸡翅",
            description="香甜可口，老少皆宜",
            price=42.0,
            category="热菜",
            stock=100,
            low_stock_threshold=10
        ),
        MenuItem(
            store_id=store.id,
            name="酸辣土豆丝",
            description="酸辣开胃，爽脆可口",
            price=18.0,
            category="素菜",
            stock=100,
            low_stock_threshold=10
        )
    ]

    for item in menu_items:
        db.add(item)

    # 提交所有数据
    db.commit()

    print("✅ 测试数据初始化完成")
    print(f"   创建店铺: {store.name}")
    print(f"   创建桌台: {len(tables)} 个")
    print(f"   创建菜品: {len(menu_items)} 道")
    print(f"   管理员账号: admin / admin123")

except Exception as e:
    db.rollback()
    print(f"❌ 初始化失败: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
