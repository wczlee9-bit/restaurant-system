#!/usr/bin/env python3
"""
餐饮点餐系统 - 快速功能测试
用于验证系统核心功能是否正常工作
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
import json
from datetime import datetime

# API基础URL
API_BASE = "http://localhost:8000"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(test_name, result, details=""):
    """打印测试结果"""
    if result:
        print(f"{Colors.GREEN}✅{Colors.END} {test_name}")
    else:
        print(f"{Colors.RED}❌{Colors.END} {test_name}")
    if details:
        print(f"   {details}")
    print()

def check_api_health():
    """检查API服务是否运行"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def test_api():
    """测试API功能"""
    print(f"{Colors.BLUE}{'='*50}{Colors.END}")
    print(f"{Colors.BLUE}开始API功能测试{Colors.END}")
    print(f"{Colors.BLUE}{'='*50}{Colors.END}\n")

    # 1. 健康检查
    print_test("1. API健康检查", check_api_health())

    # 2. 获取店铺信息
    try:
        response = requests.get(f"{API_BASE}/api/store")
        print_test("2. 获取店铺信息", response.status_code == 200, json.dumps(response.json(), indent=2, ensure_ascii=False))
        store_data = response.json()
    except Exception as e:
        print_test("2. 获取店铺信息", False, str(e))
        return False

    # 3. 获取菜品分类
    try:
        response = requests.get(f"{API_BASE}/api/menu-categories/")
        print_test("3. 获取菜品分类", response.status_code == 200, f"共 {len(response.json())} 个分类")
    except Exception as e:
        print_test("3. 获取菜品分类", False, str(e))

    # 4. 获取菜品列表
    try:
        response = requests.get(f"{API_BASE}/api/menu-items/")
        print_test("4. 获取菜品列表", response.status_code == 200, f"共 {len(response.json())} 道菜")
        menu_items = response.json()
    except Exception as e:
        print_test("4. 获取菜品列表", False, str(e))
        return False

    # 5. 获取桌号列表
    try:
        response = requests.get(f"{API_BASE}/api/tables/")
        print_test("5. 获取桌号列表", response.status_code == 200, f"共 {len(response.json())} 个桌号")
        tables = response.json()
    except Exception as e:
        print_test("5. 获取桌号列表", False, str(e))
        return False

    # 6. 创建测试订单
    try:
        if tables and menu_items:
            order_data = {
                "table_id": tables[0]["id"],
                "items": [
                    {
                        "menu_item_id": menu_items[0]["id"],
                        "quantity": 2
                    }
                ],
                "payment_method": "wechat"
            }
            response = requests.post(f"{API_BASE}/api/orders/", json=order_data)
            print_test("6. 创建测试订单", response.status_code == 200, f"订单号: {response.json().get('id')}")
            order_id = response.json().get('id')
        else:
            print_test("6. 创建测试订单", False, "缺少桌号或菜品数据")
            return False
    except Exception as e:
        print_test("6. 创建测试订单", False, str(e))
        return False

    # 7. 获取订单列表
    try:
        response = requests.get(f"{API_BASE}/api/orders/")
        print_test("7. 获取订单列表", response.status_code == 200, f"共 {len(response.json())} 个订单")
    except Exception as e:
        print_test("7. 获取订单列表", False, str(e))

    # 8. 获取订单详情
    try:
        if order_id:
            response = requests.get(f"{API_BASE}/api/orders/{order_id}")
            print_test("8. 获取订单详情", response.status_code == 200, json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print_test("8. 获取订单详情", False, str(e))

    # 9. 更新订单状态
    try:
        if order_id:
            response = requests.patch(f"{API_BASE}/api/orders/{order_id}/status", json={"status": "confirmed"})
            print_test("9. 更新订单状态", response.status_code == 200)
    except Exception as e:
        print_test("9. 更新订单状态", False, str(e))

    # 10. 更新菜品状态
    try:
        if order_id:
            response = requests.get(f"{API_BASE}/api/orders/{order_id}")
            order = response.json()
            if order.get('items'):
                item_id = order['items'][0]['id']
                response = requests.patch(
                    f"{API_BASE}/api/orders/{order_id}/items/{item_id}/status",
                    json={"item_status": "preparing"}
                )
                print_test("10. 更新菜品状态", response.status_code == 200)
    except Exception as e:
        print_test("10. 更新菜品状态", False, str(e))

    print(f"{Colors.BLUE}{'='*50}{Colors.END}")
    print(f"{Colors.GREEN}API功能测试完成！{Colors.END}")
    print(f"{Colors.BLUE}{'='*50}{Colors.END}\n")

    return True

def main():
    print("\n")
    print(f"{Colors.YELLOW}╔════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.YELLOW}║                                        ║{Colors.END}")
    print(f"{Colors.YELLOW}║   🍽️  餐饮点餐系统 - 快速功能测试       ║{Colors.END}")
    print(f"{Colors.YELLOW}║                                        ║{Colors.END}")
    print(f"{Colors.YELLOW}╚════════════════════════════════════════╝{Colors.END}")
    print("\n")

    # 检查API是否运行
    if not check_api_health():
        print(f"{Colors.RED}⚠️  API服务未运行！{Colors.END}")
        print(f"{Colors.YELLOW}请先启动API服务:{Colors.END}")
        print(f"  Linux/Mac:  bash scripts/start_test_system.sh")
        print(f"  Windows:    scripts\\start_test_system.bat")
        print(f"  或者:       python scripts/start_restaurant_api.py\n")
        return 1

    # 运行测试
    success = test_api()

    if success:
        print(f"{Colors.GREEN}🎉 所有核心功能测试通过！{Colors.END}")
        print(f"\n{Colors.YELLOW}下一步:{Colors.END}")
        print(f"  1. 打开测试页面: assets/restaurant_full_test.html")
        print(f"  2. 参考测试指南: assets/TEST_SYSTEM_GUIDE.md")
        print(f"  3. 开始模拟真实场景测试\n")
        return 0
    else:
        print(f"{Colors.RED}❌ 部分测试失败，请检查错误信息{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
