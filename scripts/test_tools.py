"""
测试工具函数
"""
from tools.order_management_tool import query_orders, analyze_order_anomalies
import json

# 测试查询订单
print("=" * 50)
print("测试查询订单...")
result = query_orders('{"store_id": 1}')
print(result)

# 解析并显示
data = json.loads(result)
if data["success"]:
    print(f"\n✅ 查询成功，共 {data['count']} 条订单")
    for order in data["orders"][:3]:
        print(f"  - 订单号: {order['order_number']}, 金额: {order['final_amount']}, 状态: {order['order_status']}")

# 测试分析异常订单
print("\n" + "=" * 50)
print("测试分析异常订单...")
result = analyze_order_anomalies(store_id=1)
print(result)

# 解析并显示
data = json.loads(result)
if data["success"]:
    print(f"\n✅ 分析成功，发现 {data['total_anomalies']} 个异常")
    for anomaly in data["anomalies"][:3]:
        print(f"  - 类型: {anomaly['type']}, 订单号: {anomaly['order_number']}, 建议: {anomaly['suggestion']}")

print("\n" + "=" * 50)
print("✅ 所有测试通过！")
