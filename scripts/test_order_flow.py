"""
测试脚本 - 验证完整的扫码点餐流程
"""
import sys
import os

# 添加项目路径到 sys.path
sys.path.insert(0, '/workspace/projects/src')

from sqlalchemy.orm import Session
from storage.database.db import get_session
from storage.database.shared.model import (
    Stores, Tables, MenuCategories, MenuItems,
    Companies, Users, Roles, UserRoles
)
from tools.qrcode_tool import QRCodeGenerator
import requests
import json


def setup_test_data():
    """
    创建测试数据：公司、店铺、用户、菜品分类、菜品、桌号
    """
    db = get_session()
    try:
        print("=" * 60)
        print("步骤 1: 创建测试数据")
        print("=" * 60)
        
        # 创建公司
        company = Companies(
            name="测试餐饮公司",
            is_active=True,
            contact_person="张三",
            contact_phone="13800138000",
            address="北京市朝阳区"
        )
        db.add(company)
        db.flush()
        print(f"✓ 创建公司: {company.name} (ID: {company.id})")
        
        # 创建角色（如果不存在）
        role = db.query(Roles).filter(Roles.name == "店长").first()
        if not role:
            role = Roles(
                name="店长",
                description="店铺负责人",
                permissions={"all": True}
            )
            db.add(role)
            db.flush()
            print(f"✓ 创建角色: {role.name} (ID: {role.id})")
        else:
            print(f"✓ 使用现有角色: {role.name} (ID: {role.id})")
        
        # 创建用户（使用随机用户名避免重复）
        import random
        import time
        random_suffix = random.randint(1000, 9999)
        user = Users(
            username=f"manager{random_suffix}",
            password="hashed_password",
            name="李店长",
            email=f"manager{random_suffix}@example.com",
            phone=f"138{random_suffix:08d}",
            is_active=True
        )
        db.add(user)
        db.flush()
        print(f"✓ 创建用户: {user.name} (ID: {user.id})")
        
        # 创建用户角色关联
        user_role = UserRoles(
            user_id=user.id,
            role_id=role.id
        )
        db.add(user_role)
        db.flush()
        
        # 创建店铺
        store = Stores(
            company_id=company.id,
            name="测试餐厅",
            is_active=True,
            address="北京市朝阳区建国路88号",
            phone="010-12345678",
            manager_id=user.id,
            opening_hours={"start": "09:00", "end": "22:00"}
        )
        db.add(store)
        db.flush()
        print(f"✓ 创建店铺: {store.name} (ID: {store.id})")
        
        # 创建菜品分类
        categories = []
        category_names = ["热菜", "凉菜", "主食", "饮品", "小吃"]
        for idx, name in enumerate(category_names, 1):
            category = MenuCategories(
                store_id=store.id,
                name=name,
                sort_order=idx,
                is_active=True,
                description=f"美味的{name}"
            )
            db.add(category)
            categories.append(category)
        db.flush()
        print(f"✓ 创建 {len(categories)} 个菜品分类")
        
        # 创建菜品
        items = []
        menu_data = [
            {"category": 0, "name": "宫保鸡丁", "price": 38.00, "stock": 50},
            {"category": 0, "name": "麻婆豆腐", "price": 28.00, "stock": 50},
            {"category": 0, "name": "红烧肉", "price": 48.00, "stock": 30},
            {"category": 1, "name": "凉拌黄瓜", "price": 18.00, "stock": 100},
            {"category": 1, "name": "拍黄瓜", "price": 16.00, "stock": 100},
            {"category": 2, "name": "米饭", "price": 2.00, "stock": 200},
            {"category": 2, "name": "炒饭", "price": 15.00, "stock": 50},
            {"category": 3, "name": "可乐", "price": 8.00, "stock": 100},
            {"category": 3, "name": "橙汁", "price": 10.00, "stock": 100},
            {"category": 4, "name": "炸鸡翅", "price": 22.00, "stock": 50},
            {"category": 4, "name": "薯条", "price": 12.00, "stock": 100}
        ]
        
        for idx, data in enumerate(menu_data, 1):
            category_idx = data["category"]
            item = MenuItems(
                store_id=store.id,
                category_id=categories[category_idx].id,
                name=data["name"],
                price=data["price"],
                stock=data["stock"],
                is_available=True,
                is_recommended=idx <= 3,
                sort_order=idx,
                description=f"美味的{data['name']}",
                unit="份",
                cooking_time=15
            )
            db.add(item)
            items.append(item)
        db.flush()
        print(f"✓ 创建 {len(items)} 个菜品")
        
        # 创建桌号
        tables = []
        for i in range(1, 6):
            table = Tables(
                store_id=store.id,
                table_number=str(i),
                table_name=f"{i}号桌",
                seats=4,
                is_active=True
            )
            db.add(table)
            tables.append(table)
        db.flush()
        print(f"✓ 创建 {len(tables)} 个桌号")
        
        # 提交所有测试数据
        db.commit()
        print("\n✓ 测试数据创建完成！")
        
        return {
            "store_id": store.id,
            "table_ids": [t.id for t in tables],
            "table_numbers": [t.table_number for t in tables],
            "menu_item_ids": [item.id for item in items],
            "user_id": user.id
        }
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ 创建测试数据失败: {str(e)}")
        raise
    finally:
        db.close()


def test_qrcode_generation(store_id, table_ids):
    """
    测试二维码生成
    """
    print("\n" + "=" * 60)
    print("步骤 2: 测试二维码生成")
    print("=" * 60)
    
    generator = QRCodeGenerator()
    
    try:
        for table_id in table_ids:
            result = generator.generate_qrcode_for_table(
                table_id=table_id,
                base_url="http://example.com/order"
            )
            print(f"✓ 桌号 {table_id} 二维码生成成功:")
            print(f"  - 二维码内容: {result['qrcode_content']}")
            print(f"  - 二维码URL: {result['qrcode_url']}")
        
        print("\n✓ 二维码生成测试通过！")
        return True
        
    except Exception as e:
        print(f"\n✗ 二维码生成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_customer_api(store_id, table_id, menu_item_ids):
    """
    测试顾客端API
    """
    print("\n" + "=" * 60)
    print("步骤 3: 测试顾客端 API")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/customer"
    
    try:
        # 测试获取店铺信息
        print("\n[测试] 获取店铺信息...")
        response = requests.get(f"{base_url}/shop?store_id={store_id}")
        if response.status_code == 200:
            shop = response.json()
            print(f"✓ 店铺信息获取成功: {shop['name']}")
        else:
            print(f"✗ 获取店铺信息失败: {response.status_code}")
            return False
        
        # 测试获取菜品列表
        print("\n[测试] 获取菜品列表...")
        response = requests.get(f"{base_url}/menu?store_id={store_id}")
        if response.status_code == 200:
            categories = response.json()
            print(f"✓ 菜品列表获取成功，共 {len(categories)} 个分类")
            for category in categories:
                print(f"  - {category['name']}: {len(category['items'])} 个菜品")
        else:
            print(f"✗ 获取菜品列表失败: {response.status_code}")
            return False
        
        # 测试创建订单
        print("\n[测试] 创建订单...")
        order_data = {
            "store_id": store_id,
            "table_id": table_id,
            "customer_name": "测试顾客",
            "customer_phone": "13900139000",
            "items": [
                {
                    "menu_item_id": menu_item_ids[0],
                    "quantity": 2
                },
                {
                    "menu_item_id": menu_item_ids[1],
                    "quantity": 1
                }
            ],
            "special_instructions": "少放辣"
        }
        
        response = requests.post(
            f"{base_url}/order",
            json=order_data
        )
        
        if response.status_code == 200:
            order = response.json()
            print(f"✓ 订单创建成功:")
            print(f"  - 订单号: {order['order_number']}")
            print(f"  - 桌号: {order['table_number']}")
            print(f"  - 订单金额: ¥{order['final_amount']}")
            print(f"  - 订单状态: {order['order_status']}")
            print(f"  - 订单项数: {len(order['items'])}")
            order_id = order['id']
        else:
            print(f"✗ 创建订单失败: {response.status_code}")
            print(response.text)
            return False
        
        # 测试查询订单
        print("\n[测试] 查询订单详情...")
        response = requests.get(f"{base_url}/order/{order_id}")
        if response.status_code == 200:
            order = response.json()
            print(f"✓ 订单详情获取成功:")
            print(f"  - 订单号: {order['order_number']}")
            print(f"  - 支付状态: {order['payment_status']}")
        else:
            print(f"✗ 查询订单失败: {response.status_code}")
            return False
        
        print("\n✓ 顾客端API测试通过！")
        return order_id
        
    except Exception as e:
        print(f"\n✗ 顾客端API测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_staff_api(store_id, order_id, user_id):
    """
    测试店员端API
    """
    print("\n" + "=" * 60)
    print("步骤 4: 测试店员端 API")
    print("=" * 60)
    
    base_url = "http://localhost:8001/api/staff"
    
    try:
        # 测试获取订单列表
        print("\n[测试] 获取订单列表...")
        response = requests.get(f"{base_url}/orders?store_id={store_id}")
        if response.status_code == 200:
            orders = response.json()
            print(f"✓ 订单列表获取成功，共 {len(orders)} 个订单")
            for order in orders:
                print(f"  - {order['order_number']}: {order['table_number']} ({order['order_status']})")
        else:
            print(f"✗ 获取订单列表失败: {response.status_code}")
            return False
        
        # 测试获取订单详情
        print("\n[测试] 获取订单详情...")
        response = requests.get(f"{base_url}/order/{order_id}")
        if response.status_code == 200:
            order = response.json()
            print(f"✓ 订单详情获取成功")
            print(f"  - 订单项数: {len(order['items'])}")
            print(f"  - 状态日志数: {len(order['status_logs'])}")
        else:
            print(f"✗ 获取订单详情失败: {response.status_code}")
            return False
        
        # 测试更新订单状态
        print("\n[测试] 更新订单状态 (待确认 -> 已确认)...")
        response = requests.put(
            f"{base_url}/order/status",
            json={
                "order_id": order_id,
                "order_status": "confirmed",
                "notes": "订单确认",
                "operator_id": user_id
            }
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 订单状态更新成功: {result['from_status']} -> {result['to_status']}")
        else:
            print(f"✗ 更新订单状态失败: {response.status_code}")
            print(response.text)
            return False
        
        # 继续更新状态：准备中
        print("\n[测试] 更新订单状态 (已确认 -> 准备中)...")
        response = requests.put(
            f"{base_url}/order/status",
            json={
                "order_id": order_id,
                "order_status": "preparing",
                "notes": "开始准备",
                "operator_id": user_id
            }
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 订单状态更新成功: {result['from_status']} -> {result['to_status']}")
        else:
            print(f"✗ 更新订单状态失败: {response.status_code}")
            return False
        
        # 获取店铺桌号列表
        print("\n[测试] 获取店铺桌号列表...")
        response = requests.get(f"{base_url}/store/{store_id}/tables")
        if response.status_code == 200:
            tables = response.json()
            print(f"✓ 桌号列表获取成功，共 {len(tables)} 个桌号")
            for table in tables:
                if table['current_order_id']:
                    print(f"  - {table['table_number']}: 当前订单 {table['current_order_id']} ({table['current_order_status']})")
        else:
            print(f"✗ 获取桌号列表失败: {response.status_code}")
            return False
        
        print("\n✓ 店员端API测试通过！")
        return True
        
    except Exception as e:
        print(f"\n✗ 店员端API测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    主测试函数
    """
    print("\n" + "=" * 60)
    print("扫码点餐系统 - 完整流程测试")
    print("=" * 60)
    
    # 步骤1: 创建测试数据
    test_data = setup_test_data()
    store_id = test_data['store_id']
    table_ids = test_data['table_ids']
    menu_item_ids = test_data['menu_item_ids']
    user_id = test_data['user_id']
    
    # 步骤2: 测试二维码生成
    qrcode_ok = test_qrcode_generation(store_id, table_ids)
    if not qrcode_ok:
        print("\n✗ 二维码生成测试失败，停止测试")
        return False
    
    # 步骤3: 测试顾客端API
    order_id = test_customer_api(store_id, table_ids[0], menu_item_ids)
    if not order_id:
        print("\n✗ 顾客端API测试失败，停止测试")
        return False
    
    # 步骤4: 测试店员端API
    staff_ok = test_staff_api(store_id, order_id, user_id)
    if not staff_ok:
        print("\n✗ 店员端API测试失败，停止测试")
        return False
    
    # 测试总结
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)
    print("\n测试总结:")
    print(f"  - 店铺ID: {store_id}")
    print(f"  - 桌号数: {len(table_ids)}")
    print(f"  - 菜品数: {len(menu_item_ids)}")
    print(f"  - 测试订单ID: {order_id}")
    print("\n功能验证:")
    print("  ✓ 二维码生成与S3存储")
    print("  ✓ 顾客端API（获取店铺、菜品、创建订单、查询订单）")
    print("  ✓ 订单与桌号关联")
    print("  ✓ 店员端API（订单管理、状态流转）")
    print("  ✓ 订单状态流转机制")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
