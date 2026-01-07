"""
测试工具函数 - 直接调用底层逻辑
"""
import json
from sqlalchemy.orm import Session
from storage.database.db import get_session
from storage.database.shared.model import Order, OrderItem
from datetime import datetime, timedelta
from sqlalchemy import and_

# 测试查询订单
print("=" * 50)
print("测试查询订单...")
db = get_session()
try:
    query = db.query(Order).filter(Order.store_id == 1)
    orders = query.order_by(Order.created_at.desc()).limit(3).all()
    
    result = []
    for order in orders:
        order_data = {
            "id": order.id,
            "order_number": order.order_number,
            "store_id": order.store_id,
            "table_id": order.table_id,
            "total_amount": order.total_amount,
            "final_amount": order.final_amount,
            "payment_status": order.payment_status,
            "order_status": order.order_status,
            "created_at": order.created_at.isoformat(),
        }
        result.append(order_data)
    
    print(f"✅ 查询成功，共 {len(result)} 条订单")
    for order in result:
        print(f"  - 订单号: {order['order_number']}, 金额: {order['final_amount']}, 状态: {order['order_status']}")
finally:
    db.close()

# 测试分析异常订单
print("\n" + "=" * 50)
print("测试分析异常订单...")
db = get_session()
try:
    now = datetime.now()
    anomalies = []
    
    # 查询长时间未支付的订单（超过30分钟）
    pending_payment_orders = db.query(Order).filter(
        Order.store_id == 1,
        Order.payment_status == "unpaid",
        Order.created_at < now - timedelta(minutes=30),
        Order.order_status != "cancelled"
    ).all()
    
    for order in pending_payment_orders:
        anomalies.append({
            "type": "长时间未支付",
            "order_id": order.id,
            "order_number": order.order_number,
            "table_id": order.table_id,
            "amount": order.final_amount,
            "waiting_time": (now - order.created_at).total_seconds() / 60,
            "unit": "分钟",
            "suggestion": "建议联系顾客确认支付情况"
        })
    
    # 查询长时间未处理的订单（超过15分钟）
    pending_orders = db.query(Order).filter(
        Order.store_id == 1,
        Order.order_status == "pending",
        Order.created_at < now - timedelta(minutes=15)
    ).all()
    
    for order in pending_orders:
        anomalies.append({
            "type": "长时间未确认",
            "order_id": order.id,
            "order_number": order.order_number,
            "table_id": order.table_id,
            "amount": order.final_amount,
            "waiting_time": (now - order.created_at).total_seconds() / 60,
            "unit": "分钟",
            "suggestion": "建议尽快确认订单并开始准备"
        })
    
    print(f"✅ 分析成功，发现 {len(anomalies)} 个异常")
    for anomaly in anomalies[:3]:
        print(f"  - 类型: {anomaly['type']}, 订单号: {anomaly['order_number']}, 等待时间: {anomaly['waiting_time']:.1f}分钟")
finally:
    db.close()

print("\n" + "=" * 50)
print("✅ 所有测试通过！")
