#!/usr/bin/env python3
"""
测试会员中心和总公司管理后台功能
"""
import requests
import json

# API 基础地址
MEMBER_API_URL = "http://localhost:8004"
HEADQUARTERS_API_URL = "http://localhost:8006"

def test_member_api():
    """测试会员 API"""
    print("=" * 50)
    print("测试会员 API")
    print("=" * 50)

    # 1. 测试注册会员
    print("\n1. 测试注册会员...")
    response = requests.post(
        f"{MEMBER_API_URL}/api/member/register",
        json={"phone": "13800138000", "name": "测试会员"}
    )
    if response.status_code == 200:
        member_data = response.json()
        print(f"✓ 注册成功: {member_data}")
        member_id = member_data['id']
    else:
        print(f"✗ 注册失败: {response.text}")
        return

    # 2. 测试获取会员信息
    print("\n2. 测试获取会员信息...")
    response = requests.get(f"{MEMBER_API_URL}/api/member/{member_id}")
    if response.status_code == 200:
        member_info = response.json()
        print(f"✓ 获取成功: {member_info}")
    else:
        print(f"✗ 获取失败: {response.text}")

    # 3. 测试通过手机号获取会员
    print("\n3. 测试通过手机号获取会员...")
    response = requests.get(f"{MEMBER_API_URL}/api/member/phone/13800138000")
    if response.status_code == 200:
        member_info = response.json()
        print(f"✓ 获取成功")
    else:
        print(f"✗ 获取失败: {response.text}")

    # 4. 测试获取积分日志
    print("\n4. 测试获取积分日志...")
    response = requests.get(f"{MEMBER_API_URL}/api/member/{member_id}/points-logs")
    if response.status_code == 200:
        point_logs = response.json()
        print(f"✓ 获取成功，共 {len(point_logs)} 条记录")
    else:
        print(f"✗ 获取失败: {response.text}")

    # 5. 测试获取订单列表
    print("\n5. 测试获取订单列表...")
    response = requests.get(f"{MEMBER_API_URL}/api/member/{member_id}/orders")
    if response.status_code == 200:
        orders = response.json()
        print(f"✓ 获取成功，共 {len(orders)} 条订单")
    else:
        print(f"✗ 获取失败: {response.text}")

    # 6. 测试获取会员等级列表
    print("\n6. 测试获取会员等级列表...")
    response = requests.get(f"{MEMBER_API_URL}/api/member/levels")
    if response.status_code == 200:
        levels = response.json()
        print(f"✓ 获取成功，共 {len(levels)} 个等级")
    else:
        print(f"✗ 获取失败: {response.text}")

    print("\n会员 API 测试完成！")

def test_headquarters_api():
    """测试总公司管理 API"""
    print("\n" + "=" * 50)
    print("测试总公司管理 API")
    print("=" * 50)

    # 1. 测试获取总体统计
    print("\n1. 测试获取总体统计...")
    response = requests.get(f"{HEADQUARTERS_API_URL}/api/headquarters/overall-stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"✓ 获取成功:")
        print(f"  - 总店铺数: {stats['total_stores']}")
        print(f"  - 活跃店铺: {stats['active_stores']}")
        print(f"  - 总订单数: {stats['total_orders']}")
        print(f"  - 总营收: {stats['total_revenue']}")
        print(f"  - 总会员数: {stats['total_members']}")
        print(f"  - 总员工数: {stats['total_staff']}")
    else:
        print(f"✗ 获取失败: {response.text}")

    # 2. 测试获取店铺列表
    print("\n2. 测试获取店铺列表...")
    response = requests.get(f"{HEADQUARTERS_API_URL}/api/headquarters/stores")
    if response.status_code == 200:
        stores = response.json()
        print(f"✓ 获取成功，共 {len(stores)} 家店铺")
    else:
        print(f"✗ 获取失败: {response.text}")

    # 3. 测试获取营收排名
    print("\n3. 测试获取营收排名...")
    response = requests.get(f"{HEADQUARTERS_API_URL}/api/headquarters/stores/revenue-ranking?days=30&top=5")
    if response.status_code == 200:
        ranking = response.json()
        print(f"✓ 获取成功，前 {len(ranking)} 名店铺:")
        for idx, store in enumerate(ranking[:3], 1):
            print(f"  {idx}. {store['store_name']}: ¥{store['total_revenue']}")
    else:
        print(f"✗ 获取失败: {response.text}")

    # 4. 测试获取营收趋势
    print("\n4. 测试获取营收趋势...")
    response = requests.get(f"{HEADQUARTERS_API_URL}/api/headquarters/revenue-trend?days=7")
    if response.status_code == 200:
        trend = response.json()
        print(f"✓ 获取成功，共 {len(trend)} 天的数据")
    else:
        print(f"✗ 获取失败: {response.text}")

    # 5. 测试获取员工列表
    print("\n5. 测试获取员工列表...")
    response = requests.get(f"{HEADQUARTERS_API_URL}/api/headquarters/staff?limit=10")
    if response.status_code == 200:
        staff_list = response.json()
        print(f"✓ 获取成功，共 {len(staff_list)} 名员工")
    else:
        print(f"✗ 获取失败: {response.text}")

    # 6. 测试获取会员统计
    print("\n6. 测试获取会员统计...")
    response = requests.get(f"{HEADQUARTERS_API_URL}/api/headquarters/members?days=30")
    if response.status_code == 200:
        member_stats = response.json()
        print(f"✓ 获取成功:")
        print(f"  - 总会员数: {member_stats['total_members']}")
        print(f"  - 活跃会员: {member_stats['active_members']}")
        print(f"  - 新增会员: {member_stats['new_members_count']}")
    else:
        print(f"✗ 获取失败: {response.text}")

    print("\n总公司管理 API 测试完成！")

if __name__ == "__main__":
    try:
        test_member_api()
        test_headquarters_api()
        print("\n" + "=" * 50)
        print("✓ 所有测试完成！")
        print("=" * 50)
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
