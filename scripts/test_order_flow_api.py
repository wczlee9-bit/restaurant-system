#!/usr/bin/env python3
"""
测试新的订单流程配置API（支持动态角色和功能分配）
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
import json

BASE_URL = "http://localhost:8000"
STORE_ID = 1

def test_order_flow_api():
    """测试订单流程配置API"""
    print("="*80)
    print("🧪 订单流程配置API测试（支持动态角色和功能分配）")
    print("="*80)
    print()

    # 1. 获取店铺的所有角色
    print("1️⃣  获取店铺的所有角色")
    print("-"*80)
    response = requests.get(f"{BASE_URL}/order-flow/stores/{STORE_ID}/roles")
    if response.status_code == 200:
        roles = response.json()
        print(f"✅ 成功获取 {len(roles)} 个角色")
        for role in roles:
            status = "启用" if role['是否启用'] else "禁用"
            print(f"   - [{role['id']}] {role['角色名称']} - {role['角色描述'] or '无描述'} ({status}, 排序: {role['排序']})")
    else:
        print(f"❌ 获取角色失败: {response.status_code}")
        print(response.text)
    print()

    # 2. 获取店铺的流程配置（按角色分组）
    print("2️⃣  获取店铺的流程配置（按角色分组）")
    print("-"*80)
    response = requests.get(f"{BASE_URL}/order-flow/stores/{STORE_ID}/flow-configs/grouped")
    if response.status_code == 200:
        grouped_configs = response.json()
        print(f"✅ 成功获取流程配置")
        for role_name, configs in grouped_configs.items():
            print(f"\n   📋 {role_name}:")
            for config in configs:
                enabled = "启用" if config['是否启用'] else "禁用"
                print(f"      - {config['订单状态']}: {config['操作方式']} ({enabled})")
    else:
        print(f"❌ 获取流程配置失败: {response.status_code}")
        print(response.text)
    print()

    # 3. 获取指定角色的订单状态
    print("3️⃣  获取指定角色的订单状态")
    print("-"*80)
    test_roles = ["厨师", "传菜员", "收银员"]
    for role_name in test_roles:
        response = requests.get(f"{BASE_URL}/order-flow/stores/{STORE_ID}/roles/{role_name}/statuses")
        if response.status_code == 200:
            result = response.json()
            status_list = result['订单状态列表']
            print(f"✅ {role_name}: {len(status_list)} 个订单状态")
            for status_info in status_list:
                print(f"      - {status_info['订单状态']}: {status_info['操作方式']}")
        else:
            print(f"⚠️  {role_name}: 获取失败或角色不存在")
    print()

    # 4. 测试创建新角色
    print("4️⃣  测试创建新角色")
    print("-"*80)
    new_role = {
        "角色名称": "测试角色",
        "角色描述": "这是一个测试创建的角色",
        "是否启用": True,
        "排序": 99
    }
    response = requests.post(f"{BASE_URL}/order-flow/stores/{STORE_ID}/roles", json=new_role)
    if response.status_code == 200:
        created_role = response.json()
        print(f"✅ 成功创建角色: {created_role['角色名称']} (ID: {created_role['id']})")
        test_role_id = created_role['id']
    else:
        print(f"❌ 创建角色失败: {response.status_code}")
        print(response.text)
        test_role_id = None
    print()

    # 5. 测试为测试角色添加流程配置
    if test_role_id:
        print("5️⃣  为测试角色添加流程配置")
        print("-"*80)
        flow_config = {
            "角色名称": "测试角色",
            "订单状态": "待确认",
            "操作方式": "逐项确认",
            "是否启用": True,
            "排序": 100
        }
        response = requests.post(f"{BASE_URL}/order-flow/stores/{STORE_ID}/flow-configs", json=flow_config)
        if response.status_code == 200:
            created_config = response.json()
            print(f"✅ 成功添加流程配置 (ID: {created_config['id']})")
            test_config_id = created_config['id']
        else:
            print(f"❌ 添加流程配置失败: {response.status_code}")
            print(response.text)
            test_config_id = None
        print()

    # 6. 测试更新流程配置
    if test_config_id:
        print("6️⃣  测试更新流程配置")
        print("-"*80)
        update_data = {
            "操作方式": "订单确认",
            "是否启用": False
        }
        response = requests.put(
            f"{BASE_URL}/order-flow/stores/{STORE_ID}/flow-configs/{test_config_id}",
            json=update_data
        )
        if response.status_code == 200:
            updated_config = response.json()
            print(f"✅ 成功更新流程配置")
            print(f"   操作方式: {updated_config['操作方式']}")
            print(f"   是否启用: {updated_config['是否启用']}")
        else:
            print(f"❌ 更新流程配置失败: {response.status_code}")
            print(response.text)
        print()

    # 7. 测试获取店铺完整配置
    print("7️⃣  获取店铺完整配置")
    print("-"*80)
    response = requests.get(f"{BASE_URL}/order-flow/stores/{STORE_ID}/full-config")
    if response.status_code == 200:
        full_config = response.json()
        print(f"✅ 成功获取店铺完整配置")
        print(f"   店铺ID: {full_config['店铺ID']}")
        print(f"   店铺名称: {full_config['店铺名称']}")
        print(f"   角色数: {len(full_config['角色列表'])}")
        print(f"   流程配置数: {len(full_config['流程配置'])}")
    else:
        print(f"❌ 获取店铺完整配置失败: {response.status_code}")
    print()

    # 8. 测试重置为默认配置
    print("8️⃣  测试重置为默认配置")
    print("-"*80)
    response = requests.post(f"{BASE_URL}/order-flow/stores/{STORE_ID}/reset")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功重置为默认配置")
        print(f"   消息: {result['message']}")
    else:
        print(f"❌ 重置为默认配置失败: {response.status_code}")
        print(response.text)
    print()

    # 9. 清理测试数据
    if test_role_id:
        print("9️⃣  清理测试数据")
        print("-"*80)
        response = requests.delete(f"{BASE_URL}/order-flow/stores/{STORE_ID}/roles/{test_role_id}")
        if response.status_code == 200:
            print(f"✅ 成功删除测试角色")
        else:
            print(f"⚠️  删除测试角色失败: {response.status_code}")
        print()

    print("="*80)
    print("✅ API测试完成")
    print("="*80)
    print()
    print("💡 提示：")
    print("   - 访问 http://localhost:8000/docs 查看完整API文档")
    print("   - 访问 assets/order_flow_config.html 进行可视化配置")
    print("   - 支持功能：自定义角色、灵活分配订单状态、独立配置操作方式")
    print()


if __name__ == "__main__":
    try:
        test_order_flow_api()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务，请确保后端服务正在运行：")
        print("   python -m uvicorn src.api.restaurant_api:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        import traceback
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
