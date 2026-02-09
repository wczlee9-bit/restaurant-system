#!/usr/bin/env python3
"""临时脚本：查看所有订单并修改为待支付状态"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取数据库URL
db_url = os.getenv("PGDATABASE_URL")

print(f"📡 连接数据库...")

# 创建引擎
engine = create_engine(db_url)

try:
    with engine.connect() as conn:
        # 查看所有订单
        print(f"\n📋 所有订单列表：")
        result = conn.execute(text("""
            SELECT id, table_id, order_number, order_status, payment_status, final_amount
            FROM orders
            ORDER BY id DESC
            LIMIT 10
        """))
        
        orders = result.fetchall()
        
        print(f"   共找到 {len(orders)} 条订单:\n")
        for order in orders:
            print(f"      ID: {order[0]}, 桌号: {order[1]}, 单号: {order[2]}")
            print(f"         状态: {order[3]}, 支付状态: {order[4]}, 金额: ¥{order[5]}\n")
        
        # 查询订单3
        print(f"\n📋 订单3详细信息：")
        result = conn.execute(text("""
            SELECT id, table_id, order_number, order_status, payment_status, 
                   final_amount, customer_name, customer_phone
            FROM orders
            WHERE id = 3
        """))
        order = result.fetchone()
        
        if not order:
            print("❌ 未找到订单3")
            exit(1)
        
        print(f"   订单ID: {order[0]}")
        print(f"   桌号: {order[1]}")
        print(f"   单号: {order[2]}")
        print(f"   订单状态: {order[3]}")
        print(f"   支付状态: {order[4]}")
        print(f"   金额: ¥{order[5]}")
        print(f"   客户: {order[6]} {order[7]}")
        
        # 修改状态为待支付
        print(f"\n🔄 修改订单状态...")
        print(f"   - order_status: 'serving' (上菜中)")
        print(f"   - payment_status: 'unpaid' (未支付)")
        
        conn.execute(text("""
            UPDATE orders 
            SET order_status = 'serving', 
                payment_status = 'unpaid',
                final_amount = 32.0,
                payment_method = NULL,
                payment_time = NULL
            WHERE id = 3
        """))
        conn.commit()
        
        # 验证修改结果
        print(f"\n✅ 订单3修改后状态：")
        result = conn.execute(text("""
            SELECT id, table_id, order_status, payment_status, final_amount
            FROM orders
            WHERE id = 3
        """))
        order = result.fetchone()
        
        print(f"   订单ID: {order[0]}")
        print(f"   桌号: {order[1]}")
        print(f"   订单状态: {order[2]} ⭐")
        print(f"   支付状态: {order[3]} ⭐")
        print(f"   金额: ¥{order[4]}")
        
        print(f"\n🎉 成功！订单3已修改为待支付状态")
        print(f"💡 现在可以在浏览器中刷新页面：")
        print(f"   http://129.226.196.76/restaurant/staff_workflow.html")
        print(f"\n💡 提示：切换到'收银员'角色，点击'处理支付'按钮")
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
