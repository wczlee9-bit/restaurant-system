#!/usr/bin/env python3
"""
测试订单创建和WebSocket通知流程
"""
import asyncio
import websockets
import json
import requests
import time

BASE_URL = "http://localhost:8000"

# 测试数据 - 先获取店铺和桌号信息
def get_test_data():
    """获取测试数据"""
    print("获取店铺和桌号信息...")
    
    # 获取店铺
    stores_response = requests.get(f"{BASE_URL}/api/store")
    store = stores_response.json()
    store_id = store['id']
    print(f"店铺ID: {store_id}")
    
    # 获取桌号
    tables_response = requests.get(f"{BASE_URL}/api/tables/")
    tables = tables_response.json()
    if tables:
        table_id = tables[0]['id']
        table_number = tables[0]['table_number']
        print(f"桌号ID: {table_id}, 桌号: {table_number}")
    else:
        table_id = 11
        print(f"使用默认桌号ID: {table_id}")
    
    return store_id, table_id

async def test_websocket(store_id):
    """测试WebSocket连接和接收消息"""
    print("\n" + "="*50)
    print("测试WebSocket连接...")
    print("="*50)
    
    ws_url = f"ws://localhost:8000/ws/store/{store_id}"
    print(f"连接到: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✓ WebSocket连接成功")
            
            # 等待连接确认消息
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(message)
            print(f"✓ 收到消息: {data}")
            
            # 监听新订单消息
            print("\n等待新订单消息...")
            try:
                # 等待10秒接收订单消息
                order_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                order_data = json.loads(order_message)
                print(f"\n{'='*50}")
                print(f"✓✓✓ 收到新订单消息！")
                print(f"{'='*50}")
                print(json.dumps(order_data, indent=2, ensure_ascii=False))
                return True
            except asyncio.TimeoutError:
                print("✗ 超时：没有收到新订单消息")
                return False
                
    except Exception as e:
        print(f"✗ WebSocket连接失败: {str(e)}")
        return False

def create_test_order(table_id):
    """创建测试订单"""
    print("\n" + "="*50)
    print("创建测试订单...")
    print("="*50)
    
    order_data = {
        "table_id": table_id,
        "items": [
            {
                "menu_item_id": 1,
                "quantity": 2,
                "special_instructions": "少放辣"
            },
            {
                "menu_item_id": 2,
                "quantity": 1,
                "special_instructions": ""
            }
        ],
        "payment_method": "counter"
    }
    
    print(f"订单数据: {json.dumps(order_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/orders/",
            json=order_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✓ 订单创建成功！")
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"✗ 订单创建失败: {response.status_code}")
            print(f"错误: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 订单创建异常: {str(e)}")
        return False

async def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("订单流程测试 - 顾客下单 → 厨师接收")
    print("="*60)
    
    # 获取测试数据
    store_id, table_id = get_test_data()
    
    # 先启动WebSocket监听
    ws_task = asyncio.create_task(test_websocket(store_id))
    
    # 等待WebSocket连接成功
    await asyncio.sleep(1)
    
    # 创建订单
    order_success = create_test_order(table_id)
    
    # 等待WebSocket接收消息
    ws_success = await ws_task
    
    # 总结
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    print(f"订单创建: {'✓ 成功' if order_success else '✗ 失败'}")
    print(f"WebSocket通知: {'✓ 成功' if ws_success else '✗ 失败'}")
    
    if order_success and ws_success:
        print("\n✓✓✓ 订单流程测试通过！")
        return 0
    else:
        print("\n✗✗✗ 订单流程测试失败！")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
