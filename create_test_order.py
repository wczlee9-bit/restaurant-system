#!/usr/bin/env python3
"""临时脚本：查看order_items表结构并创建测试订单"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv()

# 获取数据库URL
db_url = os.getenv("PGDATABASE_URL")

print(f"📡 连接数据库...")

# 创建引擎
engine = create_engine(db_url)

try:
    with engine.connect() as conn:
        # 查看order_items表结构
        print(f"\n📋 order_items表结构：")
        result = conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'order_items'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        print(f"   可用字段：")
        for col in columns:
            print(f"      - {col[0]} ({col[1]})")
        
        # 查看已有的order_items
        print(f"\n📋 查看现有的order_items：")
        result = conn.execute(text("SELECT * FROM order_items LIMIT 3"))
        items = result.fetchall()
        
        if len(items) > 0:
            print(f"   示例数据：")
            for item in items:
                print(f"      {item}\n")
        
        # 创建测试订单（只创建订单，不创建order_items）
        print(f"\n📝 创建测试订单...")
        
        table_id = 11
        store_id = 2
        
        # 删除之前可能存在的测试订单
        conn.execute(text("DELETE FROM orders WHERE order_number LIKE 'ORD20260209%' AND final_amount = 32.0"))
        conn.commit()
        
        # 创建新订单
        result = conn.execute(text("""
            INSERT INTO orders (
                store_id, table_id, order_number,
                total_amount, discount_amount, final_amount,
                payment_status, order_status,
                customer_name, customer_phone,
                created_at
            ) VALUES (
                :store_id, :table_id, :order_number,
                :total_amount, :discount_amount, :final_amount,
                :payment_status, :order_status,
                :customer_name, :customer_phone,
                :created_at
            )
            RETURNING id, order_number
        """), {
            "store_id": store_id,
            "table_id": table_id,
            "order_number": f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "total_amount": 32.0,
            "discount_amount": 0.0,
            "final_amount": 32.0,
            "payment_status": "unpaid",
            "order_status": "serving",
            "customer_name": "测试顾客",
            "customer_phone": "13800138000",
            "created_at": datetime.now()
        })
        
        order = result.fetchone()
        order_id = order[0]
        order_number = order[1]
        conn.commit()
        
        print(f"✅ 测试订单创建成功！")
        print(f"   订单ID: {order_id}")
        print(f"   订单号: {order_number}")
        print(f"   桌号ID: {table_id} (桌号 T01)")
        print(f"   金额: ¥32.0")
        print(f"   状态: serving (上菜中)")
        print(f"   支付状态: unpaid (未支付)")
        
        print(f"\n🎉 订单创建完成！")
        print(f"💡 现在可以在工作人员端测试支付功能：")
        print(f"   1. 访问: http://129.226.196.76/restaurant/staff_workflow.html")
        print(f"   2. 切换到'收银员'角色")
        print(f"   3. 查找订单ID: {order_id} (订单号: {order_number})")
        print(f"   4. 点击'处理支付'按钮测试")
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
