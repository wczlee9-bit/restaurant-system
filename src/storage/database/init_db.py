"""
初始化数据库
在 API 启动时自动创建表结构和初始化基础数据
"""
import sys
import os
import logging

logger = logging.getLogger(__name__)

def init_database():
    """初始化数据库表结构"""
    try:
        from storage.database.db import get_engine
        from storage.database.shared.model import Base

        engine = get_engine()
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        return False

def ensure_test_data():
    """确保基础测试数据存在"""
    try:
        from storage.database.db import get_session
        from storage.database.shared.model import (
            Companies, Users, Stores, MenuCategories, MenuItems, Tables
        )

        db = get_session()

        # 检查是否已有店铺数据
        store_count = db.query(Stores).count()
        if store_count == 0:
            # 如果没有店铺数据，创建所有基础数据
            logger.info("Initializing test data...")

            # 创建公司
            company = Companies(
                name="测试餐饮公司",
                is_active=True,
                contact_person="管理员",
                contact_phone="13800138000",
                address="测试地址"
            )
            db.add(company)
            db.flush()

            # 创建店铺
            store = Stores(
                company_id=company.id,
                name="美味餐厅",
                is_active=True,
                address="北京市海淀区测试街88号",
                phone="010-12345678",
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
        else:
            # 使用现有店铺
            store = db.query(Stores).first()
            logger.info(f"Using existing store: {store.name} (id={store.id})")

        # 检查是否已有分类，没有则创建
        category_count = db.query(MenuCategories).filter(MenuCategories.store_id == store.id).count()
        if category_count == 0:
            logger.info("Creating categories...")

            categories_data = [
                {"name": "热菜", "description": "各种热炒菜肴"},
                {"name": "凉菜", "description": "清爽凉菜"},
                {"name": "主食", "description": "米饭、面条等"},
                {"name": "饮品", "description": "各种饮料"}
            ]

            for i, cat_data in enumerate(categories_data):
                category = MenuCategories(
                    store_id=store.id,
                    name=cat_data["name"],
                    description=cat_data["description"],
                    is_active=True,
                    sort_order=i + 1
                )
                db.add(category)
                db.flush()
                logger.info(f"Created category: {cat_data['name']}")
        else:
            logger.info(f"Categories already exist ({category_count} categories), skipping creation")

        # 保存分类以便后续使用
        category_map = {cat.name: cat for cat in db.query(MenuCategories).filter(MenuCategories.store_id == store.id).all()}

        # 检查是否已有菜品
        menu_item_count = db.query(MenuItems).filter(MenuItems.store_id == store.id).count()
        if menu_item_count == 0:
            logger.info("Creating menu items...")

            menu_items_data = [
                # 热菜
                {"name": "宫保鸡丁", "category": "热菜", "price": 38.00, "stock": 50, "desc": "经典川菜，麻辣鲜香", "recommended": True},
                {"name": "鱼香肉丝", "category": "热菜", "price": 32.00, "stock": 45, "desc": "酸甜可口的经典菜", "recommended": False},
                {"name": "红烧肉", "category": "热菜", "price": 48.00, "stock": 30, "desc": "肥而不腻，入口即化", "recommended": True},
                {"name": "可乐鸡翅", "category": "热菜", "price": 35.00, "stock": 40, "desc": "老少皆宜", "recommended": False},
                {"name": "水煮鱼", "category": "热菜", "price": 68.00, "stock": 20, "desc": "麻辣鲜香，鱼肉鲜嫩", "recommended": True},
                {"name": "麻婆豆腐", "category": "热菜", "price": 28.00, "stock": 60, "desc": "经典川菜，麻辣下饭", "recommended": False},
                # 凉菜
                {"name": "凉拌黄瓜", "category": "凉菜", "price": 12.00, "stock": 100, "desc": "清爽开胃", "recommended": False},
                {"name": "皮蛋豆腐", "category": "凉菜", "price": 15.00, "stock": 80, "desc": "清香爽口", "recommended": False},
                {"name": "夫妻肺片", "category": "凉菜", "price": 38.00, "stock": 40, "desc": "麻辣鲜香，回味无穷", "recommended": True},
                {"name": "拍黄瓜", "category": "凉菜", "price": 10.00, "stock": 120, "desc": "简单清爽", "recommended": False},
                # 主食
                {"name": "米饭", "category": "主食", "price": 2.00, "stock": 200, "desc": "香甜可口", "recommended": False},
                {"name": "蛋炒饭", "category": "主食", "price": 18.00, "stock": 80, "desc": "蛋香浓郁", "recommended": False},
                {"name": "牛肉面", "category": "主食", "price": 22.00, "stock": 50, "desc": "汤浓面劲", "recommended": True},
                {"name": "扬州炒饭", "category": "主食", "price": 20.00, "stock": 60, "desc": "配料丰富", "recommended": False},
                # 饮品
                {"name": "可乐", "category": "饮品", "price": 5.00, "stock": 80, "desc": "冰镇可乐", "recommended": False},
                {"name": "雪碧", "category": "饮品", "price": 5.00, "stock": 80, "desc": "冰镇雪碧", "recommended": False},
                {"name": "橙汁", "category": "饮品", "price": 12.00, "stock": 50, "desc": "鲜榨橙汁", "recommended": False},
                {"name": "西瓜汁", "category": "饮品", "price": 15.00, "stock": 60, "desc": "新鲜榨汁", "recommended": True},
            ]

            for i, item_data in enumerate(menu_items_data):
                category = category_map.get(item_data["category"])
                if not category:
                    logger.warning(f"Category not found: {item_data['category']}, skipping item: {item_data['name']}")
                    continue

                menu_item = MenuItems(
                    store_id=store.id,
                    name=item_data["name"],
                    category_id=category.id,
                    price=item_data["price"],
                    stock=item_data["stock"],
                    description=item_data["desc"],
                    is_available=True,
                    is_recommended=item_data["recommended"],
                    image_url="",
                    sort_order=i + 1
                )
                db.add(menu_item)
                logger.info(f"Created menu item: {item_data['name']}")
        else:
            logger.info(f"Menu items already exist ({menu_item_count} items), skipping creation")

        # 检查是否已有桌号
        table_count = db.query(Tables).filter(Tables.store_id == store.id).count()
        if table_count == 0:
            logger.info("Creating tables...")

            seats_map = [4, 4, 6, 4, 2, 6, 4, 4, 8, 10]
            for i in range(1, 11):
                table = Tables(
                    store_id=store.id,
                    table_number=str(i),  # 使用简单数字格式，与 portal.html 一致
                    seats=seats_map[i-1],
                    is_active=True,
                    status="available"
                )
                db.add(table)
                logger.info(f"Created table: {i}号桌")
        else:
            logger.info(f"Tables already exist ({table_count} tables), skipping creation")

            # 检查桌号格式，如果不是数字格式，进行转换
            non_standard_tables = db.query(Tables).filter(
                Tables.store_id == store.id,
                Tables.table_number.like('A%')
            ).all()

            if non_standard_tables:
                logger.info(f"Found {len(non_standard_tables)} tables with A-prefix format, converting...")
                for table in non_standard_tables:
                    old_number = table.table_number
                    new_number = old_number.replace('A', '').lstrip('0')
                    if new_number == '':
                        new_number = '0'
                    table.table_number = new_number
                    logger.info(f"Updated table number: {old_number} -> {new_number}")
                db.commit()

        db.commit()
        logger.info("✓ Test data initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize test data: {e}")
        import traceback
        traceback.print_exc()
        return False
