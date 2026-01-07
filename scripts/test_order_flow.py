"""
测试扫码点餐完整流程
"""
import json
import requests
import time

# API 基础 URL
BASE_URL = "http://localhost:8000"

def test_flow():
    """测试完整流程"""
    print("=" * 60)
    print("开始测试扫码点餐流程")
    print("=" * 60)

    # 1. 获取店铺信息
    print("\n1. 获取店铺信息...")
    shop_id = 2
    response = requests.get(f"{BASE_URL}/api/customer/shop?store_id={shop_id}")
    if response.status_code == 200:
        shop = response.json()
        print(f"✅ 店铺名称: {shop['name']}")
        print(f"   地址: {shop['address']}")
    else:
        print(f"❌ 获取店铺信息失败: {response.status_code}")
        return

    # 2. 获取菜品列表
    print("\n2. 获取菜品列表...")
    response = requests.get(f"{BASE_URL}/api/customer/menu?store_id={shop_id}")
    if response.status_code == 200:
        categories = response.json()
        print(f"✅ 共有 {len(categories)} 个分类")
        for cat in categories:
            print(f"   - {cat['name']}: {len(cat['items'])} 道菜")
    else:
        print(f"❌ 获取菜品列表失败: {response.status_code}")
        return

    # 3. 创建订单
    print("\n3. 创建订单...")
    table_id = 11  # T01
    
    # 选择菜品（取前3个分类的第一个菜品）
    items = []
    for cat in categories[:3]:
        if cat['items']:
            items.append({
                "menu_item_id": cat['items'][0]['id'],
                "quantity": 1
            })
            print(f"   选择菜品: {cat['items'][0]['name']} (¥{cat['items'][0]['price']})")

    order_data = {
        "store_id": shop_id,
        "table_id": table_id,
        "customer_name": "测试顾客",
        "customer_phone": "13800000000",
        "items": items,
        "special_instructions": "少辣"
    }

    response = requests.post(f"{BASE_URL}/api/customer/order", json=order_data)
    if response.status_code == 200:
        order = response.json()
        print(f"✅ 订单创建成功!")
        print(f"   订单号: {order['order_number']}")
        print(f"   桌号: {order['table_number']}")
        print(f"   订单金额: ¥{order['final_amount']}")
        print(f"   订单状态: {order['order_status']}")
        print(f"   订单项数: {len(order['items'])}")
        for item in order['items']:
            print(f"     - {item['menu_item_name']} x{item['quantity']}: ¥{item['subtotal']}")
        
        # 4. 查询订单详情
        print("\n4. 查询订单详情...")
        order_id = order['id']
        time.sleep(1)  # 等待一下
        response = requests.get(f"{BASE_URL}/api/customer/order/{order_id}")
        if response.status_code == 200:
            order_detail = response.json()
            print(f"✅ 订单详情查询成功")
            print(f"   订单号: {order_detail['order_number']}")
            print(f"   支付状态: {order_detail['payment_status']}")
        else:
            print(f"❌ 查询订单详情失败: {response.status_code}")
    else:
        print(f"❌ 创建订单失败: {response.status_code}")
        print(response.text)

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    # 首先检查 API 服务是否运行
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ API 服务运行正常")
            test_flow()
        else:
            print("❌ API 服务响应异常")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 API 服务，请先启动服务:")
        print("   cd /workspace/projects && PYTHONPATH=/workspace/projects/src python -m uvicorn src.api.customer_api:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
