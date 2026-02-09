#!/usr/bin/env python3
"""临时脚本：检查二维码数据"""

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
        # 查看桌号和二维码数据
        print(f"\n📋 桌号和二维码数据：")
        result = conn.execute(text("""
            SELECT id, table_name, table_number, qrcode_url, qrcode_content, is_active
            FROM tables
            WHERE store_id = 2
            ORDER BY id
            LIMIT 5
        """))
        
        tables = result.fetchall()
        
        print(f"   店铺2的桌号数据：\n")
        for table in tables:
            print(f"      桌号ID: {table[0]}")
            print(f"      桌号名称: {table[1]} ({table[2]})")
            print(f"      状态: {'✅ 激活' if table[5] else '❌ 未激活'}")
            print(f"      二维码URL: {table[3][:80]}..." if table[3] else "      二维码URL: 空")
            print(f"      二维码内容: {table[4][:80]}..." if table[4] else "      二维码内容: 空")
            print(f"\n")
        
        # 检查是否有二维码数据
        has_qrcode = any(t[3] for t in tables)
        print(f"\n💡 数据库中的二维码状态：")
        print(f"   {'✅ 有二维码数据' if has_qrcode else '❌ 没有二维码数据'}")
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
