"""
测试餐饮系统API接口
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(response):
    """打印响应"""
    print(f"状态码: {response.status_code}")
    try:
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    except:
        print(response.text)
    print()

def test_health():
    """测试健康检查"""
    print("=" * 60)
    print("测试健康检查")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)

def test_tables():
    """测试获取桌号列表"""
    print("=" * 60)
    print("测试获取桌号列表")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/api/tables/")
    print_response(response)
    return response.json() if response.status_code == 200 else None

def test_categories():
    """测试获取菜品分类"""
    print("=" * 60)
    print("测试获取菜品分类")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/api/menu-categories/")
    print_response(response)
    return response.json() if response.status_code == 200 else None

def test_menu_items():
    """测试获取菜品列表"""
    print("=" * 60)
    print("测试获取菜品列表")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/api/menu-items/")
    print_response(response)
    return response.json() if response.status_code == 200 else None

def test_create_order():
    """测试创建订单"""
    print("=" * 60)
    print("测试创建订单")
    print("=" * 60)
    
    # 获取桌号
    tables = test_tables()
    if not tables:
        print("无法获取桌号列表")
        return None
    
    # 选择第一个桌号
    table_id = tables[0]['id']
    print(f"使用桌号: {tables[0]['table_number']} (ID: {table_id})")
    
    # 获取菜品
    items = test_menu_items()
    if not items or len(items) < 2:
        print("菜品数量不足")
        return None
    
    # 创建订单
    order_data = {
        "table_id": table_id,
        "items": [
            {"menu_item_id": items[0]['id'], "quantity": 1},
            {"menu_item_id": items[1]['id'], "quantity": 2}
        ],
        "payment_method": "wechat",
        "notes": "API测试订单"
    }
    
    print("订单数据:")
    print(json.dumps(order_data, ensure_ascii=False, indent=2))
    print()
    
    response = requests.post(
        f"{BASE_URL}/api/orders/",
        json=order_data,
        headers={"Content-Type": "application/json"}
    )
    print_response(response)
    
    return response.json() if response.status_code == 200 else None

def test_get_orders():
    """测试获取订单列表"""
    print("=" * 60)
    print("测试获取订单列表")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/api/orders/")
    print_response(response)
    return response.json() if response.status_code == 200 else None

def test_update_order_status(order_id):
    """测试更新订单状态"""
    print("=" * 60)
    print(f"测试更新订单状态 (订单ID: {order_id})")
    print("=" * 60)
    
    status_flow = ['confirmed', 'preparing', 'ready', 'serving', 'completed']
    
    for status in status_flow:
        print(f"更新状态为: {status}")
        response = requests.patch(
            f"{BASE_URL}/api/orders/{order_id}/status",
            json={"status": status},
            headers={"Content-Type": "application/json"}
        )
        print_response(response)
        
        if response.status_code != 200:
            print(f"更新状态失败: {status}")
            break

def test_get_order(order_id):
    """测试获取订单详情"""
    print("=" * 60)
    print(f"测试获取订单详情 (订单ID: {order_id})")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/api/orders/{order_id}")
    print_response(response)

def test_update_item_status(order_id, item_id):
    """测试更新菜品状态"""
    print("=" * 60)
    print(f"测试更新菜品状态 (订单ID: {order_id}, 菜品ID: {item_id})")
    print("=" * 60)
    
    status_flow = ['preparing', 'ready', 'served']
    
    for status in status_flow:
        print(f"更新状态为: {status}")
        response = requests.patch(
            f"{BASE_URL}/api/orders/{order_id}/items/{item_id}/status",
            json={"item_status": status},
            headers={"Content-Type": "application/json"}
        )
        print_response(response)
        
        if response.status_code != 200:
            print(f"更新状态失败: {status}")
            break

def main():
    """主函数"""
    print("\n")
    print("🍽️ 餐饮系统API测试")
    print("=" * 60)
    print()
    
    # 测试基础接口
    test_health()
    test_categories()
    
    # 测试桌号和菜品
    tables = test_tables()
    menu_items = test_menu_items()
    
    # 测试创建订单
    order = test_create_order()
    
    if order:
        order_id = order['id']
        
        # 测试获取订单列表
        test_get_orders()
        
        # 测试获取订单详情
        test_get_order(order_id)
        
        # 测试更新订单状态
        test_update_order_status(order_id)
        
        # 获取订单详情（查看菜品）
        order_detail = requests.get(f"{BASE_URL}/api/orders/{order_id}").json()
        
        # 测试更新菜品状态
        if order_detail and len(order_detail['items']) > 0:
            item_id = order_detail['items'][0]['id']
            test_update_item_status(order_id, item_id)
    
    print("\n")
    print("✅ 所有测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
