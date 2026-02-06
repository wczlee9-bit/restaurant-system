#!/usr/bin/env python3
"""
餐饮系统全面测试脚本
测试所有主要功能模块
"""
import sys
import os
import requests
import json
from datetime import datetime

# API 基础 URL
BASE_URL = "http://127.0.0.1:8000"

# 测试结果
test_results = []

def test_api(name, method, endpoint, data=None):
    """测试 API"""
    try:
        print(f"\n{'='*60}")
        print(f"测试: {name}")
        print(f"方法: {method}")
        print(f"接口: {endpoint}")
        print(f"{'='*60}")

        url = f"{BASE_URL}{endpoint}"

        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PATCH":
            response = requests.patch(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            raise ValueError(f"不支持的 HTTP 方法: {method}")

        print(f"状态码: {response.status_code}")

        if response.status_code < 400:
            print(f"✅ 测试通过")

            # 显示返回数据
            try:
                result = response.json()
                if isinstance(result, list):
                    print(f"返回数据: {len(result)} 条记录")
                    if result:
                        print(f"第一条数据: {json.dumps(result[0], ensure_ascii=False)[:200]}...")
                else:
                    print(f"返回数据: {json.dumps(result, ensure_ascii=False)[:200]}...")

                test_results.append({
                    "name": name,
                    "status": "✅ 通过",
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                })
                return result
            except:
                print(f"返回数据: {response.text[:200]}...")
                test_results.append({
                    "name": name,
                    "status": "✅ 通过",
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                })
                return response.text
        else:
            print(f"❌ 测试失败")
            print(f"错误信息: {response.text}")
            test_results.append({
                "name": name,
                "status": "❌ 失败",
                "status_code": response.status_code,
                "error": response.text,
                "timestamp": datetime.now().isoformat()
            })
            return None

    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        test_results.append({
            "name": name,
            "status": "❌ 异常",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        return None

def main():
    """主测试函数"""
    print("="*60)
    print("餐饮系统全面测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 地址: {BASE_URL}")
    print("="*60)

    # 测试 1: 健康检查
    print("\n" + "="*60)
    print("第 1 部分: 系统健康检查")
    print("="*60)
    health_check = test_api("健康检查", "GET", "/health")
    if not health_check:
        print("❌ 后端服务未启动，无法继续测试")
        return

    # 测试 2: 数据库诊断
    print("\n" + "="*60)
    print("第 2 部分: 数据库诊断")
    print("="*60)
    test_api("环境检查", "GET", "/diagnostic/env")
    test_api("数据库检查", "GET", "/diagnostic/database")

    # 测试 3: 店铺信息
    print("\n" + "="*60)
    print("第 3 部分: 店铺信息")
    print("="*60)
    store_info = test_api("获取店铺信息", "GET", "/api/store")

    # 测试 4: 分类管理
    print("\n" + "="*60)
    print("第 4 部分: 分类管理")
    print("="*60)
    categories = test_api("获取分类列表", "GET", "/api/menu-categories/")
    if categories and isinstance(categories, list):
        print(f"✅ 共有 {len(categories)} 个分类")

    # 测试 5: 菜品管理
    print("\n" + "="*60)
    print("第 5 部分: 菜品管理")
    print("="*60)
    menu_items = test_api("获取菜品列表", "GET", "/api/menu-items/")
    if menu_items and isinstance(menu_items, list):
        print(f"✅ 共有 {len(menu_items)} 个菜品")
        if menu_items:
            print(f"第一个菜品: {menu_items[0]['name']} - ¥{menu_items[0]['price']}")
    else:
        print("❌ 没有菜品数据，需要初始化")

    # 测试 6: 桌号管理
    print("\n" + "="*60)
    print("第 6 部分: 桌号管理")
    print("="*60)
    tables = test_api("获取桌号列表", "GET", "/api/tables/")
    if tables and isinstance(tables, list):
        print(f"✅ 共有 {len(tables)} 个桌号")
        if tables:
            print(f"第一个桌号: {tables[0]['table_number']}号桌 - {tables[0]['seats']}座")
    else:
        print("❌ 没有桌号数据，需要初始化")

    # 测试 7: 订单创建（如果有菜品和桌号）
    print("\n" + "="*60)
    print("第 7 部分: 订单管理")
    print("="*60)

    if menu_items and tables:
        # 获取第一个菜品和第一个桌号
        first_item = menu_items[0]
        first_table = tables[0]

        print(f"使用菜品: {first_item['name']}")
        print(f"使用桌号: {first_table['table_number']}号桌")

        # 创建订单
        order_data = {
            "table_id": first_table['id'],
            "items": [
                {
                    "menu_item_id": first_item['id'],
                    "quantity": 1,
                    "special_instructions": "测试订单"
                }
            ]
        }

        created_order = test_api(
            "创建订单",
            "POST",
            "/api/orders/",
            order_data
        )

        if created_order:
            print(f"✅ 订单创建成功: {created_order.get('order_number', created_order.get('id'))}")

            # 获取订单详情
            if 'id' in created_order:
                order_detail = test_api(
                    "获取订单详情",
                    "GET",
                    f"/api/orders/{created_order['id']}"
                )

                # 确认支付
                payment_data = {
                    "payment_method": "counter"
                }
                test_api(
                    "确认支付",
                    "POST",
                    f"/api/orders/{created_order['id']}/confirm-payment",
                    payment_data
                )
    else:
        print("⚠️ 跳过订单测试（缺少菜品或桌号数据）")

    # 测试 8: 订单列表
    print("\n" + "="*60)
    print("第 8 部分: 订单列表")
    print("="*60)
    orders = test_api("获取订单列表", "GET", "/api/orders/")
    if orders and isinstance(orders, list):
        print(f"✅ 共有 {len(orders)} 个订单")

    # 测试 9: API 文档
    print("\n" + "="*60)
    print("第 9 部分: API 文档")
    print("="*60)
    test_api("API 文档", "GET", "/docs")

    # 输出测试结果摘要
    print("\n" + "="*60)
    print("测试结果摘要")
    print("="*60)

    passed = sum(1 for r in test_results if r['status'] == '✅ 通过')
    failed = sum(1 for r in test_results if r['status'] in ['❌ 失败', '❌ 异常'])

    print(f"总计: {len(test_results)} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")

    print("\n详细结果:")
    for result in test_results:
        status_emoji = result['status'].split()[0]
        print(f"{status_emoji} {result['name']}: {result['status']}")

    # 保存测试结果
    with open('/workspace/projects/test_results.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)

    print(f"\n测试结果已保存到: /workspace/projects/test_results.json")

    if failed == 0:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️ 有 {failed} 个测试失败，需要修复")
        return 1

if __name__ == "__main__":
    sys.exit(main())
