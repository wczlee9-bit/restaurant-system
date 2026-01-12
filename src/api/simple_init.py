"""
简化的数据初始化端点
直接在 API 路由中初始化数据，避免复杂的依赖
"""
from fastapi import APIRouter, HTTPException
from storage.database.db import get_session
from storage.database.shared.model import (
    Stores, MenuCategories, MenuItems, Tables
)

router = APIRouter(tags=["simple-init"])

@router.post("/api/simple-init")
def simple_init():
    """简化版数据初始化"""
    db = get_session()

    try:
        # 检查是否已有店铺
        store = db.query(Stores).first()
        if not store:
            # 创建店铺
            store = Stores(
                company_id=1,  # 使用固定ID
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
            print(f"Created store: {store.name} (id={store.id})")
        else:
            print(f"Using existing store: {store.name} (id={store.id})")

        # 创建分类
        categories_data = [
            {"name": "热菜", "description": "各种热炒菜肴"},
            {"name": "凉菜", "description": "清爽凉菜"},
            {"name": "主食", "description": "米饭、面条等"},
            {"name": "饮品", "description": "各种饮料"}
        ]

        category_map = {}
        for cat_data in categories_data:
            existing_cat = db.query(MenuCategories).filter(
                MenuCategories.store_id == store.id,
                MenuCategories.name == cat_data["name"]
            ).first()

            if not existing_cat:
                cat = MenuCategories(
                    store_id=store.id,
                    name=cat_data["name"],
                    description=cat_data["description"],
                    is_active=True,
                    sort_order=len(category_map) + 1
                )
                db.add(cat)
                db.flush()
                category_map[cat.name] = cat
                print(f"Created category: {cat.name}")
            else:
                category_map[existing_cat.name] = existing_cat
                print(f"Using existing category: {existing_cat.name}")

        # 创建菜品
        menu_items_data = [
            {"name": "宫保鸡丁", "category": "热菜", "price": 38.00, "stock": 50, "desc": "经典川菜，麻辣鲜香", "recommended": True},
            {"name": "鱼香肉丝", "category": "热菜", "price": 32.00, "stock": 45, "desc": "酸甜可口的经典菜", "recommended": False},
            {"name": "红烧肉", "category": "热菜", "price": 48.00, "stock": 30, "desc": "肥而不腻，入口即化", "recommended": True},
            {"name": "可乐鸡翅", "category": "热菜", "price": 35.00, "stock": 40, "desc": "老少皆宜", "recommended": False},
            {"name": "水煮鱼", "category": "热菜", "price": 68.00, "stock": 20, "desc": "麻辣鲜香，鱼肉鲜嫩", "recommended": True},
            {"name": "麻婆豆腐", "category": "热菜", "price": 28.00, "stock": 60, "desc": "经典川菜，麻辣下饭", "recommended": False},
            {"name": "凉拌黄瓜", "category": "凉菜", "price": 12.00, "stock": 100, "desc": "清爽开胃", "recommended": False},
            {"name": "皮蛋豆腐", "category": "凉菜", "price": 15.00, "stock": 80, "desc": "清香爽口", "recommended": False},
            {"name": "夫妻肺片", "category": "凉菜", "price": 38.00, "stock": 40, "desc": "麻辣鲜香，回味无穷", "recommended": True},
            {"name": "拍黄瓜", "category": "凉菜", "price": 10.00, "stock": 120, "desc": "简单清爽", "recommended": False},
            {"name": "米饭", "category": "主食", "price": 2.00, "stock": 200, "desc": "香甜可口", "recommended": False},
            {"name": "蛋炒饭", "category": "主食", "price": 18.00, "stock": 80, "desc": "蛋香浓郁", "recommended": False},
            {"name": "牛肉面", "category": "主食", "price": 22.00, "stock": 50, "desc": "汤浓面劲", "recommended": True},
            {"name": "扬州炒饭", "category": "主食", "price": 20.00, "stock": 60, "desc": "配料丰富", "recommended": False},
            {"name": "可乐", "category": "饮品", "price": 5.00, "stock": 80, "desc": "冰镇可乐", "recommended": False},
            {"name": "雪碧", "category": "饮品", "price": 5.00, "stock": 80, "desc": "冰镇雪碧", "recommended": False},
            {"name": "橙汁", "category": "饮品", "price": 12.00, "stock": 50, "desc": "鲜榨橙汁", "recommended": False},
            {"name": "西瓜汁", "category": "饮品", "price": 15.00, "stock": 60, "desc": "新鲜榨汁", "recommended": True},
        ]

        for item_data in menu_items_data:
            category = category_map.get(item_data["category"])
            if not category:
                print(f"Warning: Category not found: {item_data['category']}")
                continue

            # 检查是否已存在
            existing_item = db.query(MenuItems).filter(
                MenuItems.store_id == store.id,
                MenuItems.name == item_data["name"]
            ).first()

            if not existing_item:
                item = MenuItems(
                    store_id=store.id,
                    name=item_data["name"],
                    category_id=category.id,
                    price=item_data["price"],
                    stock=item_data["stock"],
                    description=item_data["desc"],
                    is_available=True,
                    is_recommended=item_data["recommended"],
                    image_url="",
                    sort_order=0
                )
                db.add(item)
                print(f"Created menu item: {item.name}")

        # 创建桌号
        seats_map = [4, 4, 6, 4, 2, 6, 4, 4, 8, 10]
        for i in range(1, 11):
            existing_table = db.query(Tables).filter(
                Tables.store_id == store.id,
                Tables.table_number == str(i)
            ).first()

            if not existing_table:
                table = Tables(
                    store_id=store.id,
                    table_number=str(i),
                    seats=seats_map[i-1],
                    is_active=True,
                    status="available"
                )
                db.add(table)
                print(f"Created table: {i}号桌")

        db.commit()

        # 统计创建的数据
        category_count = db.query(MenuCategories).filter(MenuCategories.store_id == store.id).count()
        menu_item_count = db.query(MenuItems).filter(MenuItems.store_id == store.id).count()
        table_count = db.query(Tables).filter(Tables.store_id == store.id).count()

        return {
            "status": "success",
            "message": "Data initialized successfully",
            "data": {
                "store": store.name,
                "categories": category_count,
                "menu_items": menu_item_count,
                "tables": table_count
            }
        }

    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
