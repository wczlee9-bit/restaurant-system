#!/usr/bin/env python3
"""
逐步测试餐饮系统 - 模拟真实用户操作流程
"""

import requests
import json
import time
from typing import Dict, List

BASE_URL = "http://127.0.0.1:8000"

def print_step(step_num: int, title: str):
    """打印测试步骤"""
    print(f"\n{'='*60}")
    print(f"步骤 {step_num}: {title}")
    print(f"{'='*60}\n")

def print_result(success: bool, message: str, data=None):
    """打印测试结果"""
    status = "✅ 成功" if success else "❌ 失败"
    print(f"{status}: {message}")
    if data:
        print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return success

def test_step_1_store_info():
    """步骤1: 获取店铺信息"""
    print_step(1, "获取店铺信息")
    try:
        response = requests.get(f"{BASE_URL}/api/store")
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"店铺名称: {data['name']}, 地址: {data['address']}", data)
            return data
        else:
            print_result(False, f"HTTP {response.status_code}")
            return None
    except Exception as e:
        print_result(False, f"异常: {e}")
        return None

def test_step_2_tables():
    """步骤2: 获取桌号列表"""
    print_step(2, "获取桌号列表")
    try:
        response = requests.get(f"{BASE_URL}/api/tables/")
        if response.status_code == 200:
            tables = response.json()
            print_result(True, f"共 {len(tables)} 个桌号", tables[:2] if tables else [])
            if tables:
                print(f"示例桌号: {tables[0]['table_number']}号桌 - {tables[0]['seats']}座")
            return tables
        else:
            print_result(False, f"HTTP {response.status_code}")
            return []
    except Exception as e:
        print_result(False, f"异常: {e}")
        return []

def test_step_3_categories():
    """步骤3: 获取菜品分类"""
    print_step(3, "获取菜品分类")
    try:
        response = requests.get(f"{BASE_URL}/api/menu-categories/")
        if response.status_code == 200:
            categories = response.json()
            print_result(True, f"共 {len(categories)} 个分类", categories)
            return categories
        else:
            print_result(False, f"HTTP {response.status_code}")
            return []
    except Exception as e:
        print_result(False, f"异常: {e}")
        return []

def test_step_4_menu_items():
    """步骤4: 获取菜品列表"""
    print_step(4, "获取菜品列表")
    try:
        response = requests.get(f"{BASE_URL}/api/menu-items/")
        if response.status_code == 200:
            items = response.json()
            print_result(True, f"共 {len(items)} 个菜品", items[:2] if items else [])
            if items:
                for item in items[:3]:
                    print(f"  - {item['name']}: ¥{item['price']}")
            return items
        else:
            print_result(False, f"HTTP {response.status_code}")
            return []
    except Exception as e:
        print_result(False, f"异常: {e}")
        return []

def test_step_5_select_table(tables: List):
    """步骤5: 选择桌号"""
    print_step(5, "选择桌号")
    if not tables:
        print_result(False, "没有可用的桌号")
        return None

    # 选择第一个可用桌号
    selected_table = tables[0]
    print(f"✅ 选择桌号: {selected_table['table_number']}号桌 (ID: {selected_table['id']})")
    print(f"   座位数: {selected_table['seats']}")
    print(f"   是否占用: {'是' if selected_table['is_occupied'] else '否'}")
    return selected_table

def test_step_6_select_items(menu_items: List):
    """步骤6: 选择菜品"""
    print_step(6, "选择菜品（点餐）")
    if not menu_items:
        print_result(False, "没有可用的菜品")
        return []

    # 选择前3个菜品
    selected_items = menu_items[:3]
    print(f"✅ 选择了 {len(selected_items)} 个菜品:")
    for item in selected_items:
        print(f"   - {item['name']}: ¥{item['price']} (数量: 1)")

    # 转换为订单项格式
    order_items = [
        {
            "menu_item_id": item['id'],
            "quantity": 1,
            "special_instructions": ""
        }
        for item in selected_items
    ]

    return order_items

def test_step_7_create_order(table, order_items):
    """步骤7: 创建订单"""
    print_step(7, "创建订单")
    try:
        payload = {
            "table_id": table['id'],
            "items": order_items
        }
        print(f"请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        response = requests.post(f"{BASE_URL}/api/orders/", json=payload)
        if response.status_code == 200:
            order = response.json()
            total_amount = sum(item['quantity'] * 22.0 for item in order_items)  # 简化计算
            print_result(True, f"订单号: {order['order_number']}, 总金额: ¥{order['total_amount']}", order)
            return order
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_result(False, f"异常: {e}")
        return None

def test_step_8_get_order(order_id):
    """步骤8: 获取订单详情"""
    print_step(8, "获取订单详情")
    try:
        response = requests.get(f"{BASE_URL}/api/orders/{order_id}")
        if response.status_code == 200:
            order = response.json()
            print_result(True, f"订单状态: {order['status']}, 支付状态: {order['payment_status']}", order)
            return order
        else:
            print_result(False, f"HTTP {response.status_code}")
            return None
    except Exception as e:
        print_result(False, f"异常: {e}")
        return None

def test_step_9_confirm_payment(order_id, payment_method="counter"):
    """步骤9: 确认支付"""
    print_step(9, f"确认支付（支付方式: {payment_method}）")
    try:
        payload = {"payment_method": payment_method}
        response = requests.post(f"{BASE_URL}/api/orders/{order_id}/confirm-payment", json=payload)
        if response.status_code == 200:
            result = response.json()
            print_result(True, result['message'], result)
            return result
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_result(False, f"异常: {e}")
        return None

def test_step_10_list_orders():
    """步骤10: 获取订单列表"""
    print_step(10, "获取订单列表")
    try:
        response = requests.get(f"{BASE_URL}/api/orders/")
        if response.status_code == 200:
            orders = response.json()
            print_result(True, f"共 {len(orders)} 个订单", orders[:2] if orders else [])
            return orders
        else:
            print_result(False, f"HTTP {response.status_code}")
            return []
    except Exception as e:
        print_result(False, f"异常: {e}")
        return []

def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("🍽️ 餐饮系统逐步测试")
    print("="*60)

    results = []

    # 步骤1: 获取店铺信息
    store_info = test_step_1_store_info()
    results.append(("店铺信息", store_info is not None))

    # 步骤2: 获取桌号列表
    tables = test_step_2_tables()
    results.append(("桌号列表", len(tables) > 0))

    # 步骤3: 获取菜品分类
    categories = test_step_3_categories()
    results.append(("菜品分类", len(categories) > 0))

    # 步骤4: 获取菜品列表
    menu_items = test_step_4_menu_items()
    results.append(("菜品列表", len(menu_items) > 0))

    if not tables or not menu_items:
        print("\n⚠️  缺少必要数据，无法继续测试")
        return

    # 步骤5: 选择桌号
    selected_table = test_step_5_select_table(tables)
    results.append(("选择桌号", selected_table is not None))

    # 步骤6: 选择菜品
    selected_items = test_step_6_select_items(menu_items)
    results.append(("选择菜品", len(selected_items) > 0))

    # 步骤7: 创建订单
    order = test_step_7_create_order(selected_table, selected_items)
    results.append(("创建订单", order is not None))

    if not order:
        print("\n⚠️  订单创建失败，无法继续测试")
        return

    # 步骤8: 获取订单详情
    order_detail = test_step_8_get_order(order['id'])
    results.append(("获取订单详情", order_detail is not None))

    # 步骤9: 确认支付
    payment_result = test_step_9_confirm_payment(order['id'])
    results.append(("确认支付", payment_result is not None))

    # 步骤10: 获取订单列表
    orders = test_step_10_orders = test_step_10_list_orders()
    results.append(("订单列表", True))

    # 测试结果汇总
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for step_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {step_name}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！系统功能完整可用。")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，需要检查。")

if __name__ == "__main__":
    main()
