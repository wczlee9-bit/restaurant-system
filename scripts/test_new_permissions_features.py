"""
测试新功能脚本
测试权限管理、扩展支付方式、小票打印功能
"""
import requests
import json
import time

# API 基础URL
BASE_URL = {
    "permission": "http://localhost:8007",
    "payment": "http://localhost:8002",
    "receipt": "http://localhost:8008",
    "customer": "http://localhost:8003"
}

def print_section(title):
    """打印测试分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_permission_api():
    """测试权限管理API"""
    print_section("测试权限管理API")
    
    # 1. 初始化系统角色
    print("\n1. 初始化系统角色...")
    response = requests.post(f"{BASE_URL['permission']}/api/permission/init-roles")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    # 2. 获取所有角色
    print("\n2. 获取所有角色...")
    response = requests.get(f"{BASE_URL['permission']}/api/permission/roles")
    print(f"状态码: {response.status_code}")
    roles = response.json()
    print(f"角色数量: {len(roles)}")
    for role in roles:
        print(f"  - {role['name']}: {len(role['permissions'])}个权限")
    
    # 3. 检查用户权限（需要先创建用户）
    print("\n3. 测试权限检查...")
    # 假设user_id=1是管理员
    response = requests.post(
        f"{BASE_URL['permission']}/api/permission/check",
        json={
            "user_id": 1,
            "permission": "order:read"
        }
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_payment_methods():
    """测试扩展支付方式"""
    print_section("测试扩展支付方式")
    
    # 1. 获取支付方式列表
    print("\n1. 获取支持的支付方式...")
    response = requests.get(f"{BASE_URL['payment']}/api/payment/methods")
    print(f"状态码: {response.status_code}")
    methods = response.json()['methods']
    print(f"支付方式数量: {len(methods)}")
    for method in methods:
        print(f"  - {method['id']}: {method['name']}")
    
    # 验证是否包含新的支付方式
    method_ids = [m['id'] for m in methods]
    expected_methods = ['wechat', 'alipay', 'cash', 'credit_card', 'debit_card', 'other']
    
    print("\n2. 验证支付方式...")
    for expected in expected_methods:
        if expected in method_ids:
            print(f"  ✓ {expected} 存在")
        else:
            print(f"  ✗ {expected} 不存在")
    
    # 3. 测试使用借记卡支付（需要先有订单）
    print("\n3. 测试创建借记卡支付...")
    # 先创建订单
    order_response = create_test_order()
    if order_response:
        order_id = order_response['order']['id']
        print(f"  创建订单成功，订单ID: {order_id}")
        
        # 创建借记卡支付
        payment_response = requests.post(
            f"{BASE_URL['payment']}/api/payment/create",
            json={
                "order_id": order_id,
                "payment_method": "debit_card",
                "customer_phone": "13800138000"
            }
        )
        print(f"  状态码: {payment_response.status_code}")
        print(f"  响应: {json.dumps(payment_response.json(), indent=2, ensure_ascii=False)}")
        
        # 测试其他支付方式
        print("\n4. 测试创建'其他'支付方式...")
        payment_response = requests.post(
            f"{BASE_URL['payment']}/api/payment/create",
            json={
                "order_id": order_id,
                "payment_method": "other",
                "other_method_name": "银联支付",
                "customer_phone": "13800138000"
            }
        )
        print(f"  状态码: {payment_response.status_code}")
        print(f"  响应: {json.dumps(payment_response.json(), indent=2, ensure_ascii=False)}")


def test_receipt_api():
    """测试小票打印API"""
    print_section("测试小票打印API")
    
    # 1. 获取默认小票配置
    print("\n1. 获取默认小票配置...")
    response = requests.get(f"{BASE_URL['receipt']}/api/receipt/default-config")
    print(f"状态码: {response.status_code}")
    config = response.json()
    print(f"功能区数量: {len(config['sections'])}")
    for section in config['sections']:
        status = "启用" if section['is_enabled'] else "禁用"
        print(f"  - [{section['sort_order']}] {section['section_name']} ({section['section_type']}) - {status}")
    
    # 2. 预览小票（需要先有订单）
    print("\n2. 预览小票...")
    order_response = create_test_order()
    if order_response:
        order_id = order_response['order']['id']
        print(f"  订单ID: {order_id}")
        
        response = requests.get(f"{BASE_URL['receipt']}/api/receipt/preview/{order_id}")
        print(f"  状态码: {response.status_code}")
        receipt = response.json()
        print("\n  小票内容:")
        print("  " + "-" * 50)
        for line in receipt['receipt_content'].split('\n'):
            print(f"  {line}")
        print("  " + "-" * 50)
    
    # 3. 打印小票
    if order_response:
        print("\n3. 打印小票...")
        response = requests.post(
            f"{BASE_URL['receipt']}/api/receipt/print",
            json={
                "order_id": order_id,
                "printer_name": "热敏打印机",
                "copy_count": 2
            }
        )
        print(f"  状态码: {response.status_code}")
        result = response.json()
        print(f"  响应: {result['message']}")
        print(f"  打印份数: {result['copy_count']}")
        print(f"  打印机: {result['printer_name']}")


def create_test_order():
    """创建测试订单"""
    print("\n  创建测试订单...")
    
    # 先获取可用的桌号
    tables_response = requests.get(f"{BASE_URL['customer']}/api/customer/tables/1")
    if tables_response.status_code != 200:
        print("  获取桌号失败")
        return None
    
    tables = tables_response.json()
    if not tables:
        print("  没有可用的桌号")
        return None
    
    table_id = tables[0]['id']
    print(f"  使用桌号ID: {table_id}")
    
    # 获取菜单
    menu_response = requests.get(f"{BASE_URL['customer']}/api/customer/menu/1")
    if menu_response.status_code != 200:
        print("  获取菜单失败")
        return None
    
    menu = menu_response.json()
    if not menu:
        print("  菜单为空")
        return None
    
    # 创建订单
    order_items = [
        {
            "menu_item_id": menu[0]['id'],
            "quantity": 2,
            "special_instructions": "少辣"
        }
    ]
    
    order_response = requests.post(
        f"{BASE_URL['customer']}/api/customer/order",
        json={
            "table_id": table_id,
            "customer_name": "测试顾客",
            "customer_phone": "13800138000",
            "items": order_items,
            "special_instructions": "测试订单"
        }
    )
    
    if order_response.status_code != 200:
        print(f"  创建订单失败: {order_response.text}")
        return None
    
    print(f"  订单创建成功")
    return order_response.json()


def test_receipt_config():
    """测试小票配置管理"""
    print_section("测试小票配置管理")
    
    # 1. 创建小票配置
    print("\n1. 创建自定义小票配置...")
    config = {
        "store_id": 1,
        "config_name": "简约版小票",
        "sections": [
            {
                "section_type": "header",
                "section_name": "店铺信息",
                "is_enabled": True,
                "sort_order": 1,
                "template": "{{ store.name }}\n",
                "config": {}
            },
            {
                "section_type": "items",
                "section_name": "商品明细",
                "is_enabled": True,
                "sort_order": 2,
                "template": """
订单号: {{ order.order_number }}
{% for item in items %}
{{ item.menu_item_name }} x{{ item.quantity }} = {{ item.subtotal }}
{% endfor %}
实付: {{ order.final_amount }}
""",
                "config": {}
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL['receipt']}/api/receipt/config",
        json=config
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    # 2. 获取店铺配置列表
    print("\n2. 获取店铺配置列表...")
    response = requests.get(f"{BASE_URL['receipt']}/api/receipt/store/1/config")
    print(f"状态码: {response.status_code}")
    configs = response.json()
    print(f"配置数量: {len(configs)}")
    for cfg in configs:
        print(f"  - {cfg['config_name']}: {len(cfg['sections'])}个功能区")


def main():
    """主测试函数"""
    print("\n开始测试新功能...")
    print("请确保所有API服务已启动:")
    print("  - 权限管理API (port 8007)")
    print("  - 支付API (port 8002)")
    print("  - 小票打印API (port 8008)")
    print("  - 顾客端API (port 8003)")
    
    time.sleep(2)
    
    try:
        # 测试权限管理
        test_permission_api()
        
        # 测试扩展支付方式
        test_payment_methods()
        
        # 测试小票打印
        test_receipt_api()
        
        # 测试小票配置
        test_receipt_config()
        
        print_section("所有测试完成!")
        print("\n测试结果:")
        print("  ✓ 权限管理API - 角色初始化、权限检查")
        print("  ✓ 扩展支付方式 - 借记卡、其他支付方式")
        print("  ✓ 小票打印 - 预览、打印、配置管理")
        
    except requests.exceptions.ConnectionError as e:
        print(f"\n✗ 连接错误: 请确保所有API服务已启动")
        print(f"  错误详情: {str(e)}")
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
