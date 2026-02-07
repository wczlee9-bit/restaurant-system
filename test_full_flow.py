#!/usr/bin/env python3
"""
完整流程测试脚本
测试所有API端点和功能
"""

import requests
import json
from datetime import datetime

API_BASE = "https://restaurant-system-vzj0.onrender.com"

def test_api():
    """测试所有API端点"""
    print("=" * 60)
    print("开始测试完整流程")
    print("=" * 60)
    
    # 1. 测试餐桌列表
    print("\n1. 测试餐桌列表...")
    try:
        response = requests.get(f"{API_BASE}/api/tables/")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            tables = response.json()
            print(f"   成功获取 {len(tables)} 个餐桌")
            if tables:
                print(f"   示例餐桌: {tables[0]['table_number']}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   失败: {str(e)}")
    
    # 2. 测试菜品分类
    print("\n2. 测试菜品分类...")
    try:
        response = requests.get(f"{API_BASE}/api/menu-categories/")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            categories = response.json()
            print(f"   成功获取 {len(categories)} 个分类")
            for cat in categories:
                print(f"   - {cat['name']}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   失败: {str(e)}")
    
    # 3. 测试菜品列表
    print("\n3. 测试菜品列表...")
    try:
        response = requests.get(f"{API_BASE}/api/menu-items/")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            items = response.json()
            print(f"   成功获取 {len(items)} 个菜品")
            if items:
                item = items[0]
                print(f"   示例菜品: {item['name']} - ¥{item['price']}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   失败: {str(e)}")
    
    # 4. 测试订单列表
    print("\n4. 测试订单列表...")
    try:
        response = requests.get(f"{API_BASE}/api/orders/")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            orders = response.json()
            print(f"   成功获取 {len(orders)} 个订单")
            if orders:
                order = orders[0]
                print(f"   示例订单: {order['order_number']} - ¥{order['total_amount']}")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   失败: {str(e)}")
    
    # 5. 测试会员等级
    print("\n5. 测试会员等级...")
    try:
        response = requests.get(f"{API_BASE}/api/member/levels")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            levels = response.json()
            print(f"   成功获取 {len(levels)} 个会员等级")
            for level in levels:
                print(f"   - {level['name']}: {level['min_points']}积分, {level['discount']*100}折")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   失败: {str(e)}")
    
    # 6. 测试会员信息
    print("\n6. 测试会员信息...")
    try:
        response = requests.get(f"{API_BASE}/api/member/1")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            member = response.json()
            print(f"   成功获取会员信息")
            print(f"   - 手机号: {member['phone']}")
            print(f"   - 等级: {member['level_name']}")
            print(f"   - 积分: {member['points']}")
            print(f"   - 折扣: {member['discount']*100}折")
        else:
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"   失败: {str(e)}")
    
    # 7. 测试创建订单
    print("\n7. 测试创建订单...")
    try:
        # 先获取餐桌和菜品
        tables = requests.get(f"{API_BASE}/api/tables/").json()
        items = requests.get(f"{API_BASE}/api/menu-items/").json()
        
        if tables and items:
            order_data = {
                "table_id": tables[0]['id'],
                "items": [
                    {
                        "menu_item_id": items[0]['id'],
                        "quantity": 2
                    }
                ],
                "total_amount": items[0]['price'] * 2
            }
            
            response = requests.post(f"{API_BASE}/api/orders/", json=order_data)
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                order = response.json()
                print(f"   成功创建订单")
                print(f"   - 订单号: {order['order_number']}")
                print(f"   - 总金额: ¥{order['total_amount']}")
                print(f"   - 状态: {order['status']}")
            else:
                print(f"   错误: {response.text}")
        else:
            print("   失败: 无餐桌或菜品数据")
    except Exception as e:
        print(f"   失败: {str(e)}")
    
    # 8. 测试更新订单状态
    print("\n8. 测试更新订单状态...")
    try:
        orders = requests.get(f"{API_BASE}/api/orders/").json()
        if orders:
            order_id = orders[0]['id']
            response = requests.patch(
                f"{API_BASE}/api/orders/{order_id}/status",
                json={"status": "confirmed"}
            )
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"   成功更新订单状态为 'confirmed'")
            else:
                print(f"   错误: {response.text}")
        else:
            print("   失败: 无订单数据")
    except Exception as e:
        print(f"   失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
