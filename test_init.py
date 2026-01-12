#!/usr/bin/env python
"""
测试数据库初始化
"""
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from storage.database.db import get_session
from storage.database.shared.model import (
    Companies, Users, Stores, MenuCategories, MenuItems, Tables
)

db = get_session()

# 检查现有数据
print("=" * 60)
print("检查现有数据")
print("=" * 60)

store_count = db.query(Stores).count()
print(f"店铺数量: {store_count}")

category_count = db.query(MenuCategories).count()
print(f"分类数量: {category_count}")

menu_item_count = db.query(MenuItems).count()
print(f"菜品数量: {menu_item_count}")

table_count = db.query(Tables).count()
print(f"桌号数量: {table_count}")

# 显示桌号
print("\n桌号列表:")
tables = db.query(Tables).all()
for table in tables:
    print(f"  - {table.table_number}号桌 (座位: {table.seats}, 状态: {table.status})")

# 显示分类
print("\n分类列表:")
categories = db.query(MenuCategories).all()
for cat in categories:
    print(f"  - {cat.name}: {cat.description}")

# 显示菜品
print("\n菜品列表:")
items = db.query(MenuItems).limit(10).all()
for item in items:
    print(f"  - {item.name}: ¥{item.price} (库存: {item.stock})")

db.close()

print("\n" + "=" * 60)
print("数据检查完成")
print("=" * 60)
