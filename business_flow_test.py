#!/usr/bin/env python3
"""
餐饮系统端到端业务流程自动化测试
完整测试6个业务流程：客户点餐、厨师做菜、传菜、收款、店铺设置、财务统计
"""

import requests
import json
import time
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8080"

def print_section(title):
    """打印测试部分标题"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_step(step_num, description):
    """打印测试步骤"""
    print(f"步骤 {step_num}: {description}")

def print_result(success, message, data=None):
    """打印测试结果"""
    status = "✅ 通过" if success else "❌ 失败"
    print(f"  {status}: {message}")
    if data:
        print(f"  数据: {json.dumps(data, ensure_ascii=False, indent=4)}")
    return success

def test_customer_ordering():
    """测试1：客户点餐流程"""
    print_section("测试1：客户点餐流程")
    
    results = []
    
    # 步骤1.1：获取店铺信息
    print_step(1.1, "获取店铺信息")
    try:
        response = requests.get(f"{BASE_URL}/api/store")
        if response.status_code == 200:
            store = response.json()
            print_result(True, f"店铺: {store['name']}", store)
            results.append(True)
        else:
            print_result(False, f"HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print_result(False, str(e))
        results.append(False)
    
    # 步骤1.2：获取桌号列表
    print_step(1.2, "获取桌号列表")
    try:
        response = requests.get(f"{BASE_URL}/api/tables/")
        if response.status_code == 200:
            tables = response.json()
            selected_table = tables[0] if tables else None
            print_result(True, f"共 {len(tables)} 个桌号，选择桌号 {selected_table['table_number'] if selected_table else '无'}", selected_table)
            results.append(True)
        else:
            print_result(False, f"HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print_result(False, str(e))
        results.append(False)
    
    # 步骤1.3：获取菜品列表
    print_step(1.3, "获取菜品列表")
    try:
        response = requests.get(f"{BASE_URL}/api/menu-items/")
        if response.status_code == 200:
            items = response.json()
            print_result(True, f"共 {len(items)} 个菜品")
            results.append(True)
        else:
            print_result(False, f"HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print_result(False, str(e))
        results.append(False)
    
    # 步骤1.4：创建订单
    print_step(1.4, "创建订单")
    order_id = None
    try:
        order_data = {
            "table_id": 55,
            "items": [
                {"menu_item_id": 2, "quantity": 1, "special_instructions": "少辣"},
                {"menu_item_id": 3, "quantity": 1, "special_instructions": ""}
            ]
        }
        response = requests.post(f"{BASE_URL}/api/orders/", json=order_data)
        if response.status_code == 200:
            order = response.json()
            order_id = order['id']
            print_result(True, f"订单创建成功: {order['order_number']}, 总价 ¥{order['total_amount']}", order)
            results.append(True)
        else:
            print_result(False, f"HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print_result(False, str(e))
        results.append(False)
    
    # 步骤1.5：查看订单状态
    print_step(1.5, "查看订单状态")
    if order_id:
        try:
            response = requests.get(f"{BASE_URL}/api/orders/{order_id}")
            if response.status_code == 200:
                order = response.json()
                print_result(True, f"订单状态: {order['status']}", order)
                results.append(True)
            else:
                print_result(False, f"HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print_result(False, str(e))
            results.append(False)
    else:
        print_result(False, "订单未创建")
        results.append(False)
    
    return sum(results) / len(results) if results else 0, order_id


def test_kitchen_cooking():
    """测试2：厨师做菜流程"""
    print_section("测试2：厨师做菜流程")
    
    results = []
    
    # 步骤2.1：获取待制作订单
    print_step(2.1, "获取待制作订单")
    try:
        response = requests.get(f"{BASE_URL}/api/orders/?status=pending")
        if response.status_code == 200:
            orders = response.json()
            selected_order = orders[0] if orders else None
            print_result(True, f"共 {len(orders)} 个待制作订单", selected_order)
            results.append(True)
            order_id = selected_order['id'] if selected_order else None
            if selected_order and selected_order['items']:
                item_id = selected_order['items'][0]['id']
            else:
                item_id = None
        else:
            print_result(False, f"HTTP {response.status_code}")
            results.append(False)
            order_id = None
            item_id = None
    except Exception as e:
        print_result(False, str(e))
        results.append(False)
        order_id = None
        item_id = None
    
    # 步骤2.2：更新订单状态为制作中
    print_step(2.2, "更新订单状态为制作中")
    if order_id:
        try:
            response = requests.put(f"{BASE_URL}/api/orders/{order_id}/status", json={"status": "preparing"})
            if response.status_code == 200:
                result = response.json()
                print_result(True, f"订单状态更新: {result['status']}", result)
                results.append(True)
            else:
                print_result(False, f"HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print_result(False, str(e))
            results.append(False)
    else:
        print_result(False, "没有订单")
        results.append(False)
    
    # 步骤2.3：更新菜品状态为制作中
    print_step(2.3, "更新菜品状态为制作中")
    if item_id:
        try:
            response = requests.put(f"{BASE_URL}/api/order-items/{item_id}/status", json={"item_status": "preparing"})
            if response.status_code == 200:
                result = response.json()
                print_result(True, f"菜品状态更新: {result['status']}", result)
                results.append(True)
            else:
                print_result(False, f"HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print_result(False, str(e))
            results.append(False)
    else:
        print_result(False, "没有菜品")
        results.append(False)
    
    # 步骤2.4：更新菜品状态为完成
    print_step(2.4, "更新菜品状态为完成")
    if item_id:
        try:
            response = requests.put(f"{BASE_URL}/api/order-items/{item_id}/status", json={"item_status": "ready"})
            if response.status_code == 200:
                result = response.json()
                print_result(True, f"菜品状态更新: {result['status']}", result)
                results.append(True)
            else:
                print_result(False, f"HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print_result(False, str(e))
            results.append(False)
    else:
        print_result(False, "没有菜品")
        results.append(False)
    
    # 步骤2.5：更新订单状态为可传菜
    print_step(2.5, "更新订单状态为可传菜")
    if order_id:
        try:
            response = requests.put(f"{BASE_URL}/api/orders/{order_id}/status", json={"status": "ready"})
            if response.status_code == 200:
                result = response.json()
                print_result(True, f"订单状态更新: {result['status']}", result)
                results.append(True)
            else:
                print_result(False, f"HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print_result(False, str(e))
            results.append(False)
    else:
        print_result(False, "没有订单")
        results.append(False)
    
    return sum(results) / len(results) if results else 0, order_id


def test_delivery():
    """测试3：传菜员流程"""
    print_section("测试3：传菜员流程")
    
    results = []
    
    # 步骤3.1：获取待传菜订单
    print_step(3.1, "获取待传菜订单")
    try:
        response = requests.get(f"{BASE_URL}/api/orders/?status=ready")
        if response.status_code == 200:
            orders = response.json()
            selected_order = orders[0] if orders else None
            print_result(True, f"共 {len(orders)} 个待传菜订单", selected_order)
            results.append(True)
            order_id = selected_order['id'] if selected_order else None
        else:
            print_result(False, f"HTTP {response.status_code}")
            results.append(False)
            order_id = None
    except Exception as e:
        print_result(False, str(e))
        results.append(False)
        order_id = None
    
    # 步骤3.2：确认传菜
    print_step(3.2, "确认传菜")
    if order_id:
        try:
            response = requests.put(f"{BASE_URL}/api/orders/{order_id}/status", json={"status": "serving"})
            if response.status_code == 200:
                result = response.json()
                print_result(True, f"订单状态更新: {result['status']}", result)
                results.append(True)
            else:
                print_result(False, f"HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print_result(False, str(e))
            results.append(False)
    else:
        print_result(False, "没有订单")
        results.append(False)
    
    # 步骤3.3：传菜完成
    print_step(3.3, "传菜完成")
    if order_id:
        try:
            response = requests.put(f"{BASE_URL}/api/orders/{order_id}/status", json={"status": "completed"})
            if response.status_code == 200:
                result = response.json()
                print_result(True, f"订单状态更新: {result['status']}", result)
                results.append(True)
            else:
                print_result(False, f"HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print_result(False, str(e))
            results.append(False)
    else:
        print_result(False, "没有订单")
        results.append(False)
    
    return sum(results) / len(results) if results else 0


def test_cashier():
    """测试4：收款员流程"""
    print_section("测试4：收款员流程")
    
    results = []
    
    # 步骤4.1：获取待收款订单
    print_step(4.1, "获取待收款订单")
    try:
        response = requests.get(f"{BASE_URL}/api/orders/?status=completed")
        if response.status_code == 200:
            orders = response.json()
            selected_order = orders[0] if orders else None
            print_result(True, f"共 {len(orders)} 个待收款订单", selected_order)
            results.append(True)
            order_id = selected_order['id'] if selected_order else None
        else:
            print_result(False, f"HTTP {response.status_code}")
            results.append(False)
            order_id = None
    except Exception as e:
        print_result(False, str(e))
        results.append(False)
        order_id = None
    
    # 步骤4.2：确认收款
    print_step(4.2, "确认收款")
    if order_id:
        try:
            response = requests.post(f"{BASE_URL}/api/orders/{order_id}/confirm-payment", json={"payment_method": "immediate"})
            if response.status_code == 200:
                result = response.json()
                print_result(True, f"收款成功: {result['message']}", result)
                results.append(True)
            else:
                print_result(False, f"HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print_result(False, str(e))
            results.append(False)
    else:
        print_result(False, "没有订单")
        results.append(False)
    
    return sum(results) / len(results) if results else 0


def test_shop_settings():
    """测试5：店铺设置流程"""
    print_section("测试5：店铺设置流程")
    
    results = []
    new_item_id = None
    new_table_id = None
    
    # 步骤5.1：新增菜品
    print_step(5.1, "新增菜品")
    try:
        item_data = {
            "category_id": 1,
            "name": "测试菜品",
            "description": "这是一个测试菜品",
            "price": 99.0,
            "stock": 50,
            "is_available": True,
            "is_recommended": False
        }
        response = requests.post(f"{BASE_URL}/api/menu-items/", json=item_data)
        if response.status_code == 200:
            result = response.json()
            new_item_id = result.get('id')
            print_result(True, f"菜品创建成功: ID {new_item_id}", result)
            results.append(True)
        else:
            print_result(False, f"HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print_result(False, str(e))
        results.append(False)
    
    # 步骤5.2：修改菜品
    print_step(5.2, "修改菜品")
    if new_item_id:
        try:
            update_data = {
                "name": "测试菜品（已修改）",
                "price": 88.0
            }
            response = requests.put(f"{BASE_URL}/api/menu-items/{new_item_id}", json=update_data)
            if response.status_code == 200:
                result = response.json()
                print_result(True, f"菜品修改成功", result)
                results.append(True)
            else:
                print_result(False, f"HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print_result(False, str(e))
            results.append(False)
    else:
        print_result(False, "没有菜品")
        results.append(False)
    
    # 步骤5.3：删除菜品
    print_step(5.3, "删除菜品")
    if new_item_id:
        try:
            response = requests.delete(f"{BASE_URL}/api/menu-items/{new_item_id}")
            if response.status_code == 200:
                result = response.json()
                print_result(True, f"菜品删除成功", result)
                results.append(True)
            else:
                print_result(False, f"HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print_result(False, str(e))
            results.append(False)
    else:
        print_result(False, "没有菜品")
        results.append(False)
    
    # 步骤5.4：新增桌号
    print_step(5.4, "新增桌号")
    try:
        table_data = {
            "table_number": "T99",
            "seats": 6,
            "is_active": True
        }
        response = requests.post(f"{BASE_URL}/api/tables/", json=table_data)
        if response.status_code == 200:
            result = response.json()
            new_table_id = result['id']
            print_result(True, f"桌号创建成功: ID {new_table_id}", result)
            results.append(True)
        else:
            print_result(False, f"HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print_result(False, str(e))
        results.append(False)
    
    # 步骤5.5：修改桌号
    print_step(5.5, "修改桌号")
    if new_table_id:
        try:
            update_data = {
                "seats": 8
            }
            response = requests.patch(f"{BASE_URL}/api/tables/{new_table_id}", json=update_data)
            if response.status_code == 200:
                result = response.json()
                print_result(True, f"桌号修改成功", result)
                results.append(True)
            else:
                print_result(False, f"HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print_result(False, str(e))
            results.append(False)
    else:
        print_result(False, "没有桌号")
        results.append(False)
    
    # 步骤5.6：删除桌号
    print_step(5.6, "删除桌号")
    if new_table_id:
        try:
            response = requests.delete(f"{BASE_URL}/api/tables/{new_table_id}")
            if response.status_code == 200:
                result = response.json()
                print_result(True, f"桌号删除成功", result)
                results.append(True)
            else:
                print_result(False, f"HTTP {response.status_code}")
                results.append(False)
        except Exception as e:
            print_result(False, str(e))
            results.append(False)
    else:
        print_result(False, "没有桌号")
        results.append(False)
    
    return sum(results) / len(results) if results else 0


def test_financial_stats():
    """测试6：财务统计流程"""
    print_section("测试6：财务统计流程")
    
    results = []
    
    # 步骤6.1：今日营业额统计
    print_step(6.1, "今日营业额统计")
    try:
        response = requests.get(f"{BASE_URL}/api/stats/daily")
        if response.status_code == 200:
            result = response.json()
            print_result(True, f"今日订单: {result['total_orders']}单, 总额: ¥{result['total_amount']}", result)
            results.append(True)
        else:
            print_result(False, f"HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print_result(False, str(e))
        results.append(False)
    
    # 步骤6.2：桌次统计
    print_step(6.2, "桌次统计")
    try:
        response = requests.get(f"{BASE_URL}/api/stats/tables")
        if response.status_code == 200:
            result = response.json()
            print_result(True, f"今日使用桌数: {result['total_tables']}", result)
            results.append(True)
        else:
            print_result(False, f"HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print_result(False, str(e))
        results.append(False)
    
    # 步骤6.3：菜品销售统计
    print_step(6.3, "菜品销售统计")
    try:
        response = requests.get(f"{BASE_URL}/api/stats/menu-sales")
        if response.status_code == 200:
            result = response.json()
            print_result(True, f"今日销售菜品数: {result['total_items']}", result)
            results.append(True)
        else:
            print_result(False, f"HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print_result(False, str(e))
        results.append(False)
    
    # 步骤6.4：库存统计
    print_step(6.4, "库存统计")
    try:
        response = requests.get(f"{BASE_URL}/api/stats/inventory")
        if response.status_code == 200:
            result = response.json()
            print_result(True, f"总菜品数: {result['total_items']}", result)
            results.append(True)
        else:
            print_result(False, f"HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print_result(False, str(e))
        results.append(False)
    
    # 步骤6.5：收入报表
    print_step(6.5, "收入报表（最近7天）")
    try:
        response = requests.get(f"{BASE_URL}/api/revenue/")
        if response.status_code == 200:
            result = response.json()
            print_result(True, f"总收入: ¥{result['total_revenue']}, 已收: ¥{result['total_paid']}", result)
            results.append(True)
        else:
            print_result(False, f"HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print_result(False, str(e))
        results.append(False)
    
    return sum(results) / len(results) if results else 0


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("  餐饮系统端到端业务流程自动化测试")
    print("="*80)
    
    test_results = []
    
    # 测试1：客户点餐流程
    score1, order_id = test_customer_ordering()
    test_results.append(("测试1：客户点餐流程", score1))
    
    # 测试2：厨师做菜流程
    score2, _ = test_kitchen_cooking()
    test_results.append(("测试2：厨师做菜流程", score2))
    
    # 测试3：传菜员流程
    score3 = test_delivery()
    test_results.append(("测试3：传菜员流程", score3))
    
    # 测试4：收款员流程
    score4 = test_cashier()
    test_results.append(("测试4：收款员流程", score4))
    
    # 测试5：店铺设置流程
    score5 = test_shop_settings()
    test_results.append(("测试5：店铺设置流程", score5))
    
    # 测试6：财务统计流程
    score6 = test_financial_stats()
    test_results.append(("测试6：财务统计流程", score6))
    
    # 汇总结果
    print_section("测试结果汇总")
    
    total_score = 0
    for name, score in test_results:
        percentage = score * 100
        status = "✅" if score == 1.0 else "⚠️" if score >= 0.8 else "❌"
        print(f"{status} {name}: {percentage:.0f}%")
        total_score += score
    
    avg_score = total_score / len(test_results) if test_results else 0
    print(f"\n平均得分: {avg_score * 100:.0f}%")
    
    if avg_score == 1.0:
        print("\n🎉 所有测试通过！系统功能完整！")
    elif avg_score >= 0.8:
        print("\n⚠️ 大部分测试通过，有少量问题需要修复")
    else:
        print("\n❌ 测试失败较多，需要修复问题")


if __name__ == "__main__":
    main()
