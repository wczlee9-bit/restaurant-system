#!/usr/bin/env python3
"""
初始化测试数据
为测试平台创建必要的初始数据
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from src.storage.database.db import get_session
from src.storage.database.shared.model import (
    Companies, Stores, MenuCategories, MenuItems, Tables, Users, Roles, UserRoles
)

def init_test_data():
    """初始化测试数据"""
    print("🔄 开始初始化测试数据...")
    
    db = get_session()
    
    try:
        # 1. 创建公司
        company = db.query(Companies).filter(Companies.name == "测试餐厅总公司").first()
        if not company:
            company = Companies(
                name="测试餐厅总公司",
                is_active=True,
                contact_person="测试经理",
                contact_phone="13800138000",
                address="测试街道123号"
            )
            db.add(company)
            db.flush()
            print("✅ 创建公司")
        else:
            print("ℹ️  公司已存在，跳过")
        
        # 2. 创建店铺
        store = db.query(Stores).filter(Stores.name == "美味餐厅测试店").first()
        if not store:
            store = Stores(
                company_id=company.id,
                name="美味餐厅测试店",
                is_active=True,
                address="测试路456号",
                phone="010-88888888",
                opening_hours={
                    "monday": "09:00-22:00",
                    "tuesday": "09:00-22:00",
                    "wednesday": "09:00-22:00",
                    "thursday": "09:00-22:00",
                    "friday": "09:00-22:00",
                    "saturday": "10:00-23:00",
                    "sunday": "10:00-23:00"
                }
            )
            db.add(store)
            db.flush()
            print("✅ 创建店铺")
        else:
            print("ℹ️  店铺已存在，跳过")
        
        # 3. 创建菜品分类
        categories_data = [
            {"name": "热菜", "description": "各种热销热菜", "sort_order": 1, "is_active": True},
            {"name": "凉菜", "description": "清爽凉菜", "sort_order": 2, "is_active": True},
            {"name": "主食", "description": "米饭面条等", "sort_order": 3, "is_active": True},
            {"name": "饮品", "description": "各类饮品", "sort_order": 4, "is_active": True},
            {"name": "汤类", "description": "各种汤品", "sort_order": 5, "is_active": True}
        ]
        
        categories = {}
        for cat_data in categories_data:
            category = db.query(MenuCategories).filter(
                MenuCategories.store_id == store.id,
                MenuCategories.name == cat_data["name"]
            ).first()
            if not category:
                category = MenuCategories(
                    store_id=store.id,
                    **cat_data
                )
                db.add(category)
                db.flush()
                categories[cat_data["name"]] = category
                print(f"✅ 创建分类: {cat_data['name']}")
            else:
                categories[cat_data["name"]] = category
                print(f"ℹ️  分类已存在: {cat_data['name']}")
        
        # 4. 创建菜品
        menu_items_data = [
            # 热菜
            {"name": "宫保鸡丁", "category": "热菜", "price": 38, "description": "经典川菜，香辣可口", "stock": 100},
            {"name": "鱼香肉丝", "category": "热菜", "price": 35, "description": "酸甜口味的经典菜品", "stock": 100},
            {"name": "糖醋排骨", "category": "热菜", "price": 48, "description": "酸甜软糯，老少皆宜", "stock": 80},
            {"name": "麻婆豆腐", "category": "热菜", "price": 28, "description": "麻辣鲜香，下饭神器", "stock": 120},
            {"name": "回锅肉", "category": "热菜", "price": 42, "description": "四川特色，香辣过瘾", "stock": 90},
            {"name": "水煮鱼", "category": "热菜", "price": 68, "description": "麻辣鲜嫩，香气四溢", "stock": 60},
            
            # 凉菜
            {"name": "凉拌黄瓜", "category": "凉菜", "price": 18, "description": "清爽解腻，开胃小菜", "stock": 150},
            {"name": "拍黄瓜", "category": "凉菜", "price": 16, "description": "简单快手，清脆爽口", "stock": 150},
            {"name": "皮蛋豆腐", "category": "凉菜", "price": 22, "description": "口感丰富，营养丰富", "stock": 100},
            
            # 主食
            {"name": "米饭", "category": "主食", "price": 2, "description": "东北大米", "stock": 500},
            {"name": "蛋炒饭", "category": "主食", "price": 15, "description": "粒粒分明，香气扑鼻", "stock": 200},
            {"name": "牛肉面", "category": "主食", "price": 25, "description": "汤浓面劲，牛肉鲜嫩", "stock": 150},
            
            # 饮品
            {"name": "可乐", "category": "饮品", "price": 6, "description": "冰镇可乐", "stock": 200},
            {"name": "雪碧", "category": "饮品", "price": 6, "description": "冰镇雪碧", "stock": 200},
            {"name": "橙汁", "category": "饮品", "price": 12, "description": "鲜榨橙汁", "stock": 100},
            {"name": "酸梅汤", "category": "饮品", "price": 8, "description": "自制酸梅汤", "stock": 150},
            
            # 汤类
            {"name": "番茄鸡蛋汤", "category": "汤类", "price": 15, "description": "酸甜开胃，营养健康", "stock": 100},
            {"name": "紫菜蛋花汤", "category": "汤类", "price": 12, "description": "清淡鲜香", "stock": 120},
            {"name": "冬瓜排骨汤", "category": "汤类", "price": 35, "description": "清热去火，滋补养身", "stock": 80}
        ]
        
        for item_data in menu_items_data:
            category_name = item_data.pop("category")
            menu_item = db.query(MenuItems).filter(
                MenuItems.store_id == store.id,
                MenuItems.name == item_data["name"]
            ).first()
            if not menu_item:
                menu_item = MenuItems(
                    store_id=store.id,
                    category_id=categories[category_name].id,
                    sort_order=len(db.query(MenuItems).filter(
                        MenuItems.category_id == categories[category_name].id
                    ).all()) + 1,
                    is_available=True,
                    is_recommended=item_data["price"] > 30,
                    **item_data
                )
                db.add(menu_item)
                db.flush()
                print(f"✅ 创建菜品: {item_data['name']}")
            else:
                print(f"ℹ️  菜品已存在: {item_data['name']}")
        
        # 5. 创建桌号
        tables_data = [
            {"table_number": "1", "seats": 4, "is_active": True},
            {"table_number": "2", "seats": 4, "is_active": True},
            {"table_number": "3", "seats": 6, "is_active": True},
            {"table_number": "4", "seats": 6, "is_active": True},
            {"table_number": "5", "seats": 2, "is_active": True},
            {"table_number": "6", "seats": 2, "is_active": True},
            {"table_number": "7", "seats": 4, "is_active": True},
            {"table_number": "8", "seats": 4, "is_active": True},
            {"table_number": "9", "seats": 8, "is_active": True},
            {"table_number": "10", "seats": 8, "is_active": True},
            {"table_number": "11", "seats": 10, "is_active": True},
            {"table_number": "12", "seats": 10, "is_active": True}
        ]
        
        for table_data in tables_data:
            table = db.query(Tables).filter(
                Tables.store_id == store.id,
                Tables.table_number == table_data["table_number"]
            ).first()
            if not table:
                table = Tables(
                    store_id=store.id,
                    **table_data
                )
                db.add(table)
                db.flush()
                print(f"✅ 创建桌号: {table_data['table_number']}号")
            else:
                print(f"ℹ️  桌号已存在: {table_data['table_number']}号")
        
        # 6. 创建角色
        roles_data = [
            {"name": "管理员", "description": "系统管理员"},
            {"name": "总公司", "description": "总公司管理人员"},
            {"name": "店长", "description": "店铺店长"},
            {"name": "厨师", "description": "厨房厨师"},
            {"name": "店员", "description": "店铺服务人员"},
            {"name": "收银员", "description": "收银人员"},
            {"name": "传菜员", "description": "传菜人员"}
        ]
        
        for role_data in roles_data:
            role = db.query(Roles).filter(Roles.name == role_data["name"]).first()
            if not role:
                role = Roles(**role_data)
                db.add(role)
                db.flush()
                print(f"✅ 创建角色: {role_data['name']}")
            else:
                print(f"ℹ️  角色已存在: {role_data['name']}")
        
        # 7. 创建测试用户
        users_data = [
            {"username": "admin", "password": "admin123", "name": "系统管理员", "role": "管理员"},
            {"username": "manager", "password": "manager123", "name": "店长张三", "role": "店长"},
            {"username": "chef1", "password": "chef123", "name": "厨师李四", "role": "厨师"},
            {"username": "waiter1", "password": "waiter123", "name": "传菜员王五", "role": "传菜员"},
            {"username": "cashier1", "password": "cashier123", "name": "收银员赵六", "role": "收银员"}
        ]
        
        for user_data in users_data:
            user = db.query(Users).filter(Users.username == user_data["username"]).first()
            if not user:
                user = Users(
                    username=user_data["username"],
                    password=user_data["password"],  # 实际应用中应该加密
                    name=user_data["name"],
                    is_active=True
                )
                db.add(user)
                db.flush()
                
                # 分配角色
                role = db.query(Roles).filter(Roles.name == user_data["role"]).first()
                if role:
                    user_role = UserRoles(user_id=user.id, role_id=role.id)
                    db.add(user_role)
                
                print(f"✅ 创建用户: {user_data['name']} ({user_data['role']})")
            else:
                print(f"ℹ️  用户已存在: {user_data['name']}")
        
        db.commit()
        
        print("\n" + "="*50)
        print("✅ 测试数据初始化完成！")
        print("="*50)
        print("\n📊 数据统计:")
        print(f"   公司: {db.query(Companies).count()}")
        print(f"   店铺: {db.query(Stores).count()}")
        print(f"   分类: {db.query(MenuCategories).count()}")
        print(f"   菜品: {db.query(MenuItems).count()}")
        print(f"   桌号: {db.query(Tables).count()}")
        print(f"   用户: {db.query(Users).count()}")
        print("\n🎮 现在可以开始测试了！")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = init_test_data()
    sys.exit(0 if success else 1)
