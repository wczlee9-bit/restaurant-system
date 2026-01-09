#!/usr/bin/env python3
"""
测试新的两步订单流程
第一步：确认下单（不选择支付方式）
第二步：确认支付（选择支付方式）
"""
import asyncio
import websockets
import json
import requests

BASE_URL = "http://localhost:8000"

# 测试数据
TABLE_ID = 55  # 使用存在的桌号
STORE_ID = 2

async def test_websocket():
    """测试WebSocket连接和接收消息"""
    print("\n" + "="*50)
    print("测试WebSocket连接...")
    print("="*50)
    
    ws_url = f"ws://localhost:8000/ws/store/{STORE_ID}"
    print(f"连接到: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✓ WebSocket连接成功")
            
            # 等待连接确认消息
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(message)
            print(f"✓ 收到消息: {data}")
            
            # 监听消息
            print("\n监听消息...")
            try:
                # 监听多条消息（新订单、支付状态更新等）
                for i in range(3):
                    order_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    order_data = json.loads(order_message)
                    print(f"\n{'='*50}")
                    print(f"✓✓✓ 收到消息 {i+1}: {order_data.get('type')}")
                    print(f"{'='*50}")
                    print(json.dumps(order_data, indent=2, ensure_ascii=False))
            except asyncio.TimeoutError:
                print("✗ 超时：没有收到更多消息")
                return False
                
    except Exception as e:
        print(f"✗ WebSocket连接失败: {str(e)}")
        return False

def step1_submit_order():
    """第一步：提交订单（不选择支付方式）"""
    print("\n" + "="*50)
    print("第一步：提交订单（不选择支付方式）")
    print("="*50)
    
    order_data = {
        "table_id": TABLE_ID,
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
        ]
        # 不包含payment_method
    }
    
    print(f"订单数据: {json.dumps(order_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/orders/",
            json=order_data,
            timeout=10
        )
        
        if response.status_code == 200:
            order_info = response.json()
            print(f"✓ 订单提交成功！")
            print(f"  订单ID: {order_info['id']}")
            print(f"  订单号: {order_info['order_number']}")
            print(f"  支付方式: {order_info['payment_method'] or '未选择'}")
            print(f"  支付状态: {order_info['payment_status']}")
            print(f"  订单状态: {order_info['status']}")
            return order_info
        else:
            print(f"✗ 订单提交失败: {response.status_code}")
            print(f"错误: {response.text}")
            return None
    except Exception as e:
        print(f"✗ 订单提交异常: {str(e)}")
        return None

def step2_confirm_payment(order_id, payment_method='counter'):
    """第二步：确认支付（选择支付方式）"""
    print("\n" + "="*50)
    print(f"第二步：确认支付（选择{payment_method}支付）")
    print("="*50)
    
    payment_data = {
        "payment_method": payment_method
    }
    
    print(f"支付数据: {json.dumps(payment_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/orders/{order_id}/confirm-payment",
            json=payment_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 确认支付成功！")
            print(f"  订单ID: {result['order_id']}")
            print(f"  支付方式: {result['payment_method']}")
            print(f"  支付状态: {result['payment_status']}")
            return True
        else:
            print(f"✗ 确认支付失败: {response.status_code}")
            print(f"错误: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 确认支付异常: {str(e)}")
        return False

async def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("新的两步订单流程测试")
    print("第一步：确认下单 → 厨师开始制作")
    print("第二步：确认支付 → 选择支付方式")
    print("="*60)
    
    # 启动WebSocket监听
    ws_task = asyncio.create_task(test_websocket())
    
    # 等待WebSocket连接成功
    await asyncio.sleep(1)
    
    # 第一步：提交订单
    order_info = step1_submit_order()
    
    if not order_info:
        print("\n✗✗✗ 订单提交失败，无法继续测试")
        return 1
    
    # 等待WebSocket接收消息
    await asyncio.sleep(2)
    
    # 第二步：确认支付
    payment_success = step2_confirm_payment(order_info['id'], payment_method='counter')
    
    # 等待WebSocket接收消息
    await asyncio.sleep(2)
    
    # 取消WebSocket任务
    ws_task.cancel()
    try:
        await ws_task
    except asyncio.CancelledError:
        pass
    
    # 总结
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    print(f"第一步（提交订单）: {'✓ 成功' if order_info else '✗ 失败'}")
    print(f"第二步（确认支付）: {'✓ 成功' if payment_success else '✗ 失败'}")
    
    if order_info and payment_success:
        print("\n✓✓✓ 新的两步订单流程测试通过！")
        print("\n流程说明：")
        print("  1. 顾客确认下单 → 厨师收到订单，开始制作")
        print("  2. 顾客选择支付方式 → 支付状态更新")
        print("  3. 订单状态实时同步到厨师端")
        return 0
    else:
        print("\n✗✗✗ 新的两步订单流程测试失败！")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
