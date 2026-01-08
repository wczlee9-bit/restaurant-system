"""
测试顾客点餐流程
"""
import requests
import time

API_URL = "http://localhost:8000"

def test_get_tables():
    """测试获取桌号列表"""
    print("测试1: 获取桌号列表...")

    try:
        response = requests.get(f"{API_URL}/api/tables/")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            tables = response.json()
            print(f"成功获取 {len(tables)} 个桌号")
            for table in tables[:5]:
                occupied_status = "已占用" if table.get('is_occupied') else "空闲"
                print(f"  - {table['table_number']}号桌 (ID: {table['id']}): {occupied_status}")
            return True
        else:
            print(f"失败: {response.text}")
            return False
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

def test_get_menu_categories():
    """测试获取菜品分类"""
    print("\n测试2: 获取菜品分类...")

    try:
        response = requests.get(f"{API_URL}/api/menu-categories/")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            categories = response.json()
            print(f"成功获取 {len(categories)} 个分类")
            for cat in categories[:5]:
                print(f"  - {cat['name']}")
            return True
        else:
            print(f"失败: {response.text}")
            return False
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

def test_get_menu_items():
    """测试获取菜品列表"""
    print("\n测试3: 获取菜品列表...")

    try:
        response = requests.get(f"{API_URL}/api/menu-items/")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            items = response.json()
            print(f"成功获取 {len(items)} 个菜品")
            for item in items[:5]:
                available = "可用" if item.get('is_available') else "不可用"
                print(f"  - {item['name']}: ¥{item['price']} (库存: {item.get('stock', 0)}, {available})")
            return True
        else:
            print(f"失败: {response.text}")
            return False
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

def test_create_order():
    """测试创建订单"""
    print("\n测试4: 创建订单...")

    try:
        # 先获取桌号和菜品
        tables_resp = requests.get(f"{API_URL}/api/tables/")
        tables = tables_resp.json()

        if not tables:
            print("错误: 没有可用的桌号")
            return False

        table = tables[0]

        items_resp = requests.get(f"{API_URL}/api/menu-items/")
        items = items_resp.json()

        if not items:
            print("错误: 没有可用的菜品")
            return False

        # 创建订单
        order_data = {
            "table_id": table['id'],
            "items": [
                {
                    "menu_item_id": items[0]['id'],
                    "quantity": 1
                }
            ],
            "payment_method": "immediate"
        }

        response = requests.post(f"{API_URL}/api/orders/", json=order_data)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            order = response.json()
            print(f"成功创建订单")
            print(f"  - 订单号: {order['order_number']}")
            print(f"  - 桌号: {order['table_number']}")
            print(f"  - 总金额: ¥{order['total_amount']}")
            print(f"  - 支付方式: {order['payment_method']}")
            return True
        else:
            print(f"失败: {response.text}")
            return False
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

def test_get_table_by_table_number():
    """测试通过桌号获取桌号信息"""
    print("\n测试5: 通过桌号获取桌号信息...")

    try:
        # 先获取所有桌号
        tables_resp = requests.get(f"{API_URL}/api/tables/")
        tables = tables_resp.json()

        if not tables:
            print("错误: 没有可用的桌号")
            return False

        table_number = tables[0]['table_number']

        # 通过桌号过滤
        response = requests.get(f"{API_URL}/api/tables/")
        if response.status_code == 200:
            all_tables = response.json()
            found_table = next((t for t in all_tables if t['table_number'] == table_number), None)

            if found_table:
                print(f"成功找到桌号: {found_table['table_number']}")
                print(f"  - ID: {found_table['id']}")
                print(f"  - 座位数: {found_table['seats']}")
                print(f"  - 状态: {'活跃' if found_table.get('is_active') else '不活跃'}")
                print(f"  - 占用: {'已占用' if found_table.get('is_occupied') else '空闲'}")
                return True
            else:
                print(f"未找到桌号: {table_number}")
                return False
        else:
            print(f"失败: {response.text}")
            return False
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("测试顾客点餐流程")
    print("=" * 60)

    # 检查API服务是否运行
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"API服务状态: {response.json()}")
    except Exception as e:
        print(f"错误: 无法连接到API服务")
        exit(1)

    # 运行所有测试
    results = []
    results.append(("获取桌号列表", test_get_tables()))
    results.append(("获取菜品分类", test_get_menu_categories()))
    results.append(("获取菜品列表", test_get_menu_items()))
    results.append(("通过桌号获取桌号信息", test_get_table_by_table_number()))
    results.append(("创建订单", test_create_order()))

    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n🎉 所有测试通过!")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息")
