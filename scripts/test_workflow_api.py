#!/usr/bin/env python3
"""
测试订单流程配置API
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
import json

BASE_URL = "http://localhost:8000"

def test_workflow_config_api():
    """测试工作流程配置API"""
    print("="*60)
    print("🧪 订单流程配置API测试")
    print("="*60)
    print()

    # 1. 获取所有配置
    print("1️⃣  获取所有配置")
    print("-"*60)
    response = requests.get(f"{BASE_URL}/api/workflow-config/")
    if response.status_code == 200:
        configs = response.json()
        print(f"✅ 成功获取 {len(configs)} 条配置")
        for config in configs:
            print(f"   - {config['role_name']} - {config['status_name']}: {config['action_mode_name']} ({'启用' if config['is_enabled'] else '禁用'})")
    else:
        print(f"❌ 获取配置失败: {response.status_code}")
        print(response.text)
    print()

    # 2. 获取厨师配置
    print("2️⃣  获取厨师配置")
    print("-"*60)
    response = requests.get(f"{BASE_URL}/api/workflow-config/by-role/kitchen")
    if response.status_code == 200:
        kitchen_configs = response.json()
        print(f"✅ 成功获取厨师配置 ({len(kitchen_configs)} 条)")
        for config in kitchen_configs:
            print(f"   - 状态 {config['status']}: {config['action_mode']} ({'启用' if config['is_enabled'] else '禁用'})")
    else:
        print(f"❌ 获取厨师配置失败: {response.status_code}")
    print()

    # 3. 获取传菜员配置
    print("3️⃣  获取传菜员配置")
    print("-"*60)
    response = requests.get(f"{BASE_URL}/api/workflow-config/by-role/waiter")
    if response.status_code == 200:
        waiter_configs = response.json()
        print(f"✅ 成功获取传菜员配置 ({len(waiter_configs)} 条)")
        for config in waiter_configs:
            print(f"   - 状态 {config['status']}: {config['action_mode']} ({'启用' if config['is_enabled'] else '禁用'})")
    else:
        print(f"❌ 获取传菜员配置失败: {response.status_code}")
    print()

    # 4. 获取操作模式
    print("4️⃣  获取操作模式")
    print("-"*60)
    test_cases = [
        ("kitchen", "pending"),
        ("kitchen", "preparing"),
        ("waiter", "ready"),
        ("waiter", "serving"),
    ]
    for role, status in test_cases:
        response = requests.get(f"{BASE_URL}/api/workflow-config/action-mode/{role}/{status}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {role}/{status}: {result['action_mode']} ({'启用' if result['is_enabled'] else '禁用'})")
        else:
            print(f"❌ {role}/{status}: 获取失败")
    print()

    # 5. 测试批量更新
    print("5️⃣  测试批量更新（修改第一个配置）")
    print("-"*60)
    # 先获取配置
    response = requests.get(f"{BASE_URL}/api/workflow-config/")
    if response.status_code == 200:
        configs = response.json()
        if configs:
            first_config = configs[0]
            original_mode = first_config['action_mode']

            # 切换模式
            new_mode = 'per_order' if original_mode == 'per_item' else 'per_item'

            update_data = {
                "configs": [
                    {"id": first_config['id'], "action_mode": new_mode, "is_enabled": True}
                ]
            }

            response = requests.post(
                f"{BASE_URL}/api/workflow-config/bulk-update",
                json=update_data
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 批量更新成功: {result['message']}")
                print(f"   配置ID {first_config['id']}: {original_mode} → {new_mode}")

                # 验证更新
                verify_response = requests.get(f"{BASE_URL}/api/workflow-config/{first_config['id']}")
                if verify_response.status_code == 200:
                    verified = verify_response.json()
                    if verified['action_mode'] == new_mode:
                        print(f"✅ 验证成功：配置已更新为 {new_mode}")
                    else:
                        print(f"❌ 验证失败：配置未正确更新")
            else:
                print(f"❌ 批量更新失败: {response.status_code}")
                print(response.text)
    print()

    # 6. 测试重置为默认
    print("6️⃣  测试重置为默认配置")
    print("-"*60)
    response = requests.post(f"{BASE_URL}/api/workflow-config/reset-defaults")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 重置成功: {result['message']}")
        print(f"   店铺ID: {result['store_id']}")
    else:
        print(f"❌ 重置失败: {response.status_code}")
    print()

    print("="*60)
    print("✅ API测试完成")
    print("="*60)
    print()
    print("💡 提示：")
    print("   - 访问 http://localhost:8000/docs 查看完整API文档")
    print("   - 在店铺设置页面可视化配置订单流程")
    print()

if __name__ == "__main__":
    try:
        test_workflow_config_api()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务，请确保后端服务正在运行：")
        print("   python scripts/start_restaurant_api.py")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
