"""
测试数据初始化脚本
"""
from sqlalchemy.orm import Session
from storage.database.db import get_session
from storage.database.shared.model import (
    User, Role, UserRole, Company, Store, Table, Staff,
    MenuCategory, MenuItem, Order, OrderItem, Payment, Member, Inventory,
    Supplier, PurchaseOrder, PurchaseItem
)
from datetime import datetime, timedelta
import random

def create_test_data():
    """创建测试数据"""
    db = get_session()
    try:
        # 1. 创建角色
        roles = []
        role_data = [
            ("developer", "系统开发者"),
            ("company", "总公司管理员"),
            ("store_manager", "店长"),
            ("staff", "店员")
        ]
        for name, desc in role_data:
            role = db.query(Role).filter(Role.name == name).first()
            if not role:
                role = Role(name=name, description=desc, permissions=[])
                db.add(role)
                db.flush()
            roles.append(role)
        
        # 2. 创建用户
        users = []
        for i in range(1, 11):
            username = f"user{i}"
            existing_user = db.query(User).filter(User.username == username).first()
            if not existing_user:
                user = User(
                    username=username,
                    password="hashed_password",  # 实际应用中应该加密
                    email=f"user{i}@example.com",
                    phone=f"138000{i:04d}",
                    name=f"用户{i}",
                    is_active=True
                )
                db.add(user)
                db.flush()
            else:
                user = existing_user
            users.append(user)
        
        # 分配角色
        user_roles = [
            (0, 0),  # user1 -> developer
            (1, 1),  # user2 -> company
            (2, 2),  # user3 -> store_manager
            (3, 3),  # user4 -> staff
            (4, 3),  # user5 -> staff
        ]
        for user_idx, role_idx in user_roles:
            ur = db.query(UserRole).filter(
                UserRole.user_id == users[user_idx].id,
                UserRole.role_id == roles[role_idx].id
            ).first()
            if not ur:
                ur = UserRole(
                    user_id=users[user_idx].id,
                    role_id=roles[role_idx].id
                )
                db.add(ur)
        
        # 3. 创建总公司
        company = db.query(Company).filter(Company.name == "示例餐饮集团").first()
        if not company:
            company = Company(
                name="示例餐饮集团",
                contact_person="张总",
                contact_phone="13900000000",
                address="北京市朝阳区",
                is_active=True
            )
            db.add(company)
            db.flush()
        
        # 4. 创建店铺
        store = db.query(Store).filter(Store.name == "示范餐厅").first()
        if not store:
            store = Store(
                company_id=company.id,
                name="示范餐厅",
                address="北京市朝阳区示范路1号",
                phone="010-12345678",
                manager_id=users[2].id,
                is_active=True,
                opening_hours={"open": "09:00", "close": "22:00"}
            )
            db.add(store)
            db.flush()
        
        # 5. 创建桌号
        tables = []
        for i in range(1, 11):
            table_num = f"T{i:02d}"
            table = db.query(Table).filter(
                Table.store_id == store.id,
                Table.table_number == table_num
            ).first()
            if not table:
                table = Table(
                    store_id=store.id,
                    table_number=table_num,
                    table_name=f"桌号{i}",
                    qrcode_content=f"table_{table_num}",
                    seats=random.choice([2, 4, 6]),
                    is_active=True
                )
                db.add(table)
                db.flush()
            tables.append(table)
        
        # 6. 创建店员
        staff_records = []
        for i in range(3, 6):
            staff = db.query(Staff).filter(
                Staff.user_id == users[i].id,
                Staff.store_id == store.id
            ).first()
            if not staff:
                position = "厨师" if i == 3 else ("服务员" if i == 4 else "传菜员")
                staff = Staff(
                    user_id=users[i].id,
                    store_id=store.id,
                    position=position,
                    is_active=True
                )
                db.add(staff)
                db.flush()
            staff_records.append(staff)
        
        # 7. 创建菜品分类
        categories = []
        category_names = ["热菜", "凉菜", "主食", "饮品", "汤品"]
        for idx, cat_name in enumerate(category_names):
            cat = db.query(MenuCategory).filter(
                MenuCategory.store_id == store.id,
                MenuCategory.name == cat_name
            ).first()
            if not cat:
                cat = MenuCategory(
                    store_id=store.id,
                    name=cat_name,
                    description=f"{cat_name}系列",
                    sort_order=idx + 1,
                    is_active=True
                )
                db.add(cat)
                db.flush()
            categories.append(cat)
        
        # 8. 创建菜品
        menu_items_data = [
            ("宫保鸡丁", "经典川菜，香辣可口", 38.0, categories[0].id),
            ("鱼香肉丝", "酸甜适中，老少皆宜", 32.0, categories[0].id),
            ("麻婆豆腐", "麻辣鲜香，下饭神器", 28.0, categories[0].id),
            ("凉拌黄瓜", "清爽解腻", 18.0, categories[1].id),
            ("拍黄瓜", "简单美味", 15.0, categories[1].id),
            ("蛋炒饭", "经典主食", 16.0, categories[2].id),
            ("牛肉炒饭", "营养丰富", 22.0, categories[2].id),
            ("可乐", "冰镇可乐", 6.0, categories[3].id),
            ("橙汁", "鲜榨橙汁", 12.0, categories[3].id),
            ("紫菜蛋花汤", "鲜美清淡", 12.0, categories[4].id),
            ("西红柿鸡蛋汤", "家常美味", 15.0, categories[4].id),
        ]
        
        for name, desc, price, cat_id in menu_items_data:
            item = db.query(MenuItem).filter(
                MenuItem.store_id == store.id,
                MenuItem.name == name
            ).first()
            if not item:
                item = MenuItem(
                    store_id=store.id,
                    category_id=cat_id,
                    name=name,
                    description=desc,
                    price=price,
                    original_price=price * 1.2,
                    stock=100,
                    unit="份",
                    cooking_time=random.randint(10, 30),
                    is_available=True,
                    is_recommended=random.choice([True, False]),
                    sort_order=1
                )
                db.add(item)
        
        # 9. 创建供应商
        suppliers = []
        supplier_data = [
            ("蔬菜供应商", "李经理", "13911112222", "北京市大兴区"),
            ("肉类供应商", "王经理", "13922223333", "北京市通州区"),
            ("饮料供应商", "赵经理", "13933334444", "北京市海淀区"),
        ]
        for name, contact, phone, address in supplier_data:
            supplier = db.query(Supplier).filter(Supplier.name == name).first()
            if not supplier:
                supplier = Supplier(
                    name=name,
                    contact_person=contact,
                    contact_phone=phone,
                    address=address
                )
                db.add(supplier)
                db.flush()
            suppliers.append(supplier)
        
        # 10. 创建库存
        inventory_data = [
            ("鸡肉", "肉类", "斤", 50.0, 10.0, 100.0, 25.0, suppliers[1].id),
            ("猪肉", "肉类", "斤", 40.0, 10.0, 100.0, 28.0, suppliers[1].id),
            ("鸡蛋", "蛋类", "斤", 30.0, 10.0, 80.0, 8.0, suppliers[0].id),
            ("大米", "主食", "袋", 20.0, 5.0, 50.0, 120.0, suppliers[0].id),
            ("蔬菜", "蔬菜", "斤", 100.0, 20.0, 200.0, 5.0, suppliers[0].id),
        ]
        for item_name, category, unit, qty, min_qty, max_qty, cost, supplier_id in inventory_data:
            inv = db.query(Inventory).filter(
                Inventory.store_id == store.id,
                Inventory.item_name == item_name
            ).first()
            if not inv:
                inv = Inventory(
                    store_id=store.id,
                    item_name=item_name,
                    category=category,
                    unit=unit,
                    quantity=qty,
                    min_stock=min_qty,
                    max_stock=max_qty,
                    cost_price=cost,
                    supplier_id=supplier_id
                )
                db.add(inv)
        
        # 11. 创建测试订单
        # 模拟过去5天的订单
        for day_offset in range(5):
            current_date = datetime.now() - timedelta(days=day_offset)
            
            # 每天创建 5-10 个订单
            num_orders = random.randint(5, 10)
            for i in range(num_orders):
                order_number = f"ORD{current_date.strftime('%Y%m%d')}{i+1:04d}"
                table = random.choice(tables)
                
                # 随机选择 2-5 个菜品
                menu_items = db.query(MenuItem).filter(MenuItem.store_id == store.id).all()
                selected_items = random.sample(menu_items, random.randint(2, 5))
                
                # 计算订单金额
                total_amount = sum(item.price * random.randint(1, 3) for item in selected_items)
                discount_amount = random.uniform(0, 10) if random.random() > 0.7 else 0
                final_amount = total_amount - discount_amount
                
                # 随机订单状态
                status_weights = ["completed"] * 7 + ["cancelled"] * 1 + ["serving"] * 1
                order_status = random.choice(status_weights)
                
                # 创建订单
                order = Order(
                    store_id=store.id,
                    table_id=table.id,
                    order_number=order_number,
                    total_amount=total_amount,
                    discount_amount=discount_amount,
                    final_amount=final_amount,
                    payment_status="paid" if order_status != "cancelled" else "unpaid",
                    payment_method=random.choice(["wechat", "alipay", "cash"]),
                    payment_time=current_date if order_status != "cancelled" else None,
                    order_status=order_status,
                    created_at=current_date
                )
                db.add(order)
                db.flush()
                
                # 创建订单项
                for item in selected_items:
                    quantity = random.randint(1, 3)
                    order_item = OrderItem(
                        order_id=order.id,
                        menu_item_id=item.id,
                        menu_item_name=item.name,
                        menu_item_price=item.price,
                        quantity=quantity,
                        subtotal=item.price * quantity,
                        status="served" if order_status == "completed" else "pending"
                    )
                    db.add(order_item)
                
                # 创建支付记录
                if order.payment_status == "paid":
                    payment = Payment(
                        order_id=order.id,
                        payment_method=order.payment_method,
                        amount=final_amount,
                        transaction_id=f"TXN{order_number}",
                        payment_time=current_date,
                        status="success"
                    )
                    db.add(payment)
        
        db.commit()
        print("✅ 测试数据创建成功！")
        print(f"- 创建了 {len(roles)} 个角色")
        print(f"- 创建了 {len(users)} 个用户")
        print(f"- 创建了 1 个总公司")
        print(f"- 创建了 1 个店铺")
        print(f"- 创建了 {len(tables)} 个桌号")
        print(f"- 创建了 {len(categories)} 个菜品分类")
        print(f"- 创建了 {len(menu_items_data)} 个菜品")
        print(f"- 创建了 {len(suppliers)} 个供应商")
        print(f"- 创建了 5 个库存项目")
        print(f"- 创建了大量测试订单")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 测试数据创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
