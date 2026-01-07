"""
测试营收分析功能
"""
import json
from sqlalchemy.orm import Session
from storage.database.db import get_session
from storage.database.shared.model import Order, DailyRevenue, Store
from datetime import date, datetime, timedelta
from sqlalchemy import func

print("=" * 50)
print("测试营收分析...")

db = get_session()
try:
    # 获取店铺
    store = db.query(Store).first()
    if not store:
        print("❌ 没有找到店铺")
    else:
        store_id = store.id
        print(f"✅ 找到店铺: {store.name} (ID: {store_id})")
        
        # 计算今天的营收
        today = date.today()
        start_datetime = datetime.combine(today, datetime.min.time())
        end_datetime = datetime.combine(today, datetime.max.time())
        
        orders = db.query(Order).filter(
            Order.store_id == store_id,
            Order.created_at >= start_datetime,
            Order.created_at <= end_datetime
        ).all()
        
        total_orders = len(orders)
        total_amount = sum(o.total_amount for o in orders)
        total_discount = sum(o.discount_amount for o in orders)
        
        refunded_orders = db.query(Order).filter(
            Order.store_id == store_id,
            Order.created_at >= start_datetime,
            Order.created_at <= end_datetime,
            Order.order_status == "cancelled"
        ).all()
        total_refund = sum(o.final_amount for o in refunded_orders)
        
        net_revenue = total_amount - total_discount - total_refund
        
        # 统计支付方式
        payment_methods = {}
        for order in orders:
            if order.payment_method:
                payment_methods[order.payment_method] = payment_methods.get(order.payment_method, 0) + order.final_amount
        
        print(f"\n✅ 今日营收统计:")
        print(f"  - 订单数: {total_orders}")
        print(f"  - 总金额: ¥{total_amount:.2f}")
        print(f"  - 折扣: ¥{total_discount:.2f}")
        print(f"  - 退款: ¥{total_refund:.2f}")
        print(f"  - 净营收: ¥{net_revenue:.2f}")
        print(f"  - 支付方式: {payment_methods}")
        
        # 查询过去7天的营收趋势
        print(f"\n" + "=" * 50)
        print(f"查询过去7天的营收趋势...")
        
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        revenues = db.query(DailyRevenue).filter(
            DailyRevenue.store_id == store_id,
            func.date(DailyRevenue.date) >= start_date,
            func.date(DailyRevenue.date) <= end_date
        ).order_by(DailyRevenue.date).all()
        
        print(f"✅ 找到 {len(revenues)} 条营收记录")
        for rev in revenues:
            print(f"  - {rev.date.strftime('%Y-%m-%d')}: 订单 {rev.total_orders}, 营收 ¥{rev.net_revenue:.2f}")
        
finally:
    db.close()

print("\n" + "=" * 50)
print("✅ 营收分析测试完成！")
