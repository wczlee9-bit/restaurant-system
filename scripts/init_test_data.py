"""
初始化测试数据
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy.orm import Session
from storage.database.db import get_session
from storage.database.shared.model import (
    Companies, Users, Stores, MenuCategories, MenuItems,
    Tables, MemberLevelRules, Roles
)
from datetime import datetime

def init_test_data():
    """初始化测试数据"""
    db: Session = get_session()

    try:
        # 1. 创建测试公司
        company = db.query(Companies).filter(Companies.name == "测试餐饮公司").first()
        if not company:
            company = Companies(
                name="测试餐饮公司",
                is_active=True,
                contact_person="张三",
                contact_phone="13800138000",
                address="北京市朝阳区测试大街1号"
            )
            db.add(company)
            db.flush()
            print(f"✓ 创建公司: {company.name} (ID: {company.id})")
        else:
            print(f"✓ 公司已存在: {company.name} (ID: {company.id})")

        # 2. 创建测试用户（店长）
        manager = db.query(Users).filter(Users.username == "manager001").first()
        if not manager:
            manager = Users(
                username="manager001",
                email="manager@test.com",
                password="password123",
                name="李店长",
                is_active=True,
                phone="13900139000"
            )
            db.add(manager)
            db.flush()
            print(f"✓ 创建店长: {manager.name} (ID: {manager.id})")
        else:
            print(f"✓ 店长已存在: {manager.name} (ID: {manager.id})")

        # 3. 创建测试店铺
        store = db.query(Stores).filter(Stores.name == "美味餐厅").first()
        if not store:
            store = Stores(
                company_id=company.id,
                name="美味餐厅",
                is_active=True,
                address="北京市海淀区美味街88号",
                phone="010-12345678",
                manager_id=manager.id,
                opening_hours={
                    "monday": {"open": "09:00", "close": "22:00"},
                    "tuesday": {"open": "09:00", "close": "22:00"},
                    "wednesday": {"open": "09:00", "close": "22:00"},
                    "thursday": {"open": "09:00", "close": "22:00"},
                    "friday": {"open": "09:00", "close": "22:00"},
                    "saturday": {"open": "10:00", "close": "23:00"},
                    "sunday": {"open": "10:00", "close": "23:00"}
                }
            )
            db.add(store)
            db.flush()
            print(f"✓ 创建店铺: {store.name} (ID: {store.id})")
        else:
            print(f"✓ 店铺已存在: {store.name} (ID: {store.id})")

        # 4. 创建菜品分类
        categories = [
            {"name": "热菜", "description": "各种热炒菜肴"},
            {"name": "凉菜", "description": "清爽凉菜"},
            {"name": "主食", "description": "米饭、面条等"},
            {"name": "饮品", "description": "各种饮料"}
        ]

        category_ids = {}
        for i, cat_data in enumerate(categories):
            category = db.query(MenuCategories).filter(
                MenuCategories.store_id == store.id,
                MenuCategories.name == cat_data["name"]
            ).first()
            if not category:
                category = MenuCategories(
                    store_id=store.id,
                    name=cat_data["name"],
                    description=cat_data["description"],
                    is_active=True,
                    sort_order=i + 1
                )
                db.add(category)
                db.flush()
                print(f"✓ 创建分类: {category.name} (ID: {category.id})")
            else:
                print(f"✓ 分类已存在: {category.name} (ID: {category.id})")
            category_ids[category.name] = category.id

        # 5. 创建菜品
        dishes = [
            {
                "category": "热菜",
                "name": "宫保鸡丁",
                "description": "经典川菜，鸡肉鲜嫩，花生脆爽",
                "price": 38.00,
                "image_url": "https://example.com/dish1.jpg"
            },
            {
                "category": "热菜",
                "name": "麻婆豆腐",
                "description": "麻辣鲜香，下饭神器",
                "price": 28.00,
                "image_url": "https://example.com/dish2.jpg"
            },
            {
                "category": "热菜",
                "name": "红烧肉",
                "description": "肥而不腻，入口即化",
                "price": 58.00,
                "image_url": "https://example.com/dish3.jpg"
            },
            {
                "category": "凉菜",
                "name": "凉拌黄瓜",
                "description": "清爽开胃",
                "price": 12.00,
                "image_url": "https://example.com/dish4.jpg"
            },
            {
                "category": "主食",
                "name": "白米饭",
                "description": "东北大米",
                "price": 2.00,
                "image_url": "https://example.com/dish5.jpg"
            },
            {
                "category": "主食",
                "name": "蛋炒饭",
                "description": "扬州风味",
                "price": 18.00,
                "image_url": "https://example.com/dish6.jpg"
            },
            {
                "category": "饮品",
                "name": "可乐",
                "description": "冰爽可乐",
                "price": 6.00,
                "image_url": "https://example.com/drink1.jpg"
            },
            {
                "category": "饮品",
                "name": "柠檬茶",
                "description": "新鲜柠檬制作",
                "price": 15.00,
                "image_url": "https://example.com/drink2.jpg"
            }
        ]

        for i, dish_data in enumerate(dishes):
            dish = db.query(MenuItems).filter(
                MenuItems.store_id == store.id,
                MenuItems.name == dish_data["name"]
            ).first()
            if not dish:
                dish = MenuItems(
                    store_id=store.id,
                    category_id=category_ids[dish_data["category"]],
                    name=dish_data["name"],
                    description=dish_data["description"],
                    price=dish_data["price"],
                    image_url=dish_data["image_url"],
                    is_available=True,
                    is_recommended=False,
                    stock=999,
                    sort_order=i + 1
                )
                db.add(dish)
                db.flush()
                print(f"✓ 创建菜品: {dish.name} (ID: {dish.id}, 价格: ¥{dish.price})")
            else:
                print(f"✓ 菜品已存在: {dish.name} (ID: {dish.id})")

        # 6. 创建桌号
        for i in range(1, 11):
            table = db.query(Tables).filter(
                Tables.store_id == store.id,
                Tables.table_number == str(i)
            ).first()
            if not table:
                table = Tables(
                    store_id=store.id,
                    table_number=str(i),
                    seats=4 if i <= 6 else 8,
                    is_active=True
                )
                db.add(table)
                db.flush()
                print(f"✓ 创建桌号: {table.table_number} (ID: {table.id}, 座位: {table.seats}人)")
            else:
                print(f"✓ 桌号已存在: {table.table_number}")

        # 7. 初始化会员等级规则
        level_rules = [
            {"level": 1, "level_name": "普通会员", "min_points": 0, "discount": 1.0},
            {"level": 2, "level_name": "银卡会员", "min_points": 500, "discount": 0.95},
            {"level": 3, "level_name": "金卡会员", "min_points": 2000, "discount": 0.9},
            {"level": 4, "level_name": "钻石会员", "min_points": 5000, "discount": 0.85},
            {"level": 5, "level_name": "黑金会员", "min_points": 10000, "discount": 0.8}
        ]

        for rule_data in level_rules:
            rule = db.query(MemberLevelRules).filter(
                MemberLevelRules.level == rule_data["level"]
            ).first()
            if not rule:
                rule = MemberLevelRules(
                    level=rule_data["level"],
                    level_name=rule_data["level_name"],
                    min_points=rule_data["min_points"],
                    discount=rule_data["discount"]
                )
                db.add(rule)
                db.flush()
                print(f"✓ 创建会员等级: {rule.level_name} (等级: {rule.level}, 折扣: {rule.discount})")
            else:
                print(f"✓ 会员等级已存在: {rule.level_name}")

        db.commit()
        print("\n✅ 测试数据初始化完成！")
        print(f"\n测试店铺信息:")
        print(f"  店铺ID: {store.id}")
        print(f"  店铺名称: {store.name}")
        print(f"  地址: {store.address}")
        print(f"  电话: {store.phone}")

    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_test_data()
