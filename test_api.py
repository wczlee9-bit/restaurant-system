#!/usr/bin/env python3
"""临时脚本：测试API是否正常工作"""

import requests
import json

print(f"🧪 测试API是否正常工作...\n")

# 测试菜单API
menu_url = "http://129.226.196.76/restaurant/api/menu-items?store_id=2"
print(f"1️⃣ 测试菜单API：")
print(f"   URL: {menu_url}")

try:
    response = requests.get(menu_url, timeout=5)
    print(f"   状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            print(f"   ✅ 成功！返回 {len(data)} 个菜品")
            if len(data) > 0:
                print(f"   示例菜品: {data[0].get('name', 'N/A')}")
        else:
            print(f"   ✅ 成功！返回数据: {data}")
    else:
        print(f"   ❌ 失败！响应: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print(f"\n2️⃣ 测试店铺信息API：")
store_url = "http://129.226.196.76/restaurant/api/stores/2"
print(f"   URL: {store_url}")

try:
    response = requests.get(store_url, timeout=5)
    print(f"   状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ 成功！店铺: {data.get('name', 'N/A')}")
    else:
        print(f"   ❌ 失败！响应: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print(f"\n3️⃣ 测试桌号API：")
tables_url = "http://129.226.196.76/restaurant/api/tables?store_id=2"
print(f"   URL: {tables_url}")

try:
    response = requests.get(tables_url, timeout=5)
    print(f"   状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            print(f"   ✅ 成功！返回 {len(data)} 个桌号")
        else:
            print(f"   ✅ 成功！")
    else:
        print(f"   ❌ 失败！响应: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print(f"\n💡 测试完成！")
