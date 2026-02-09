#!/usr/bin/env python3
"""临时脚本：修复二维码内容"""

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
        # 修复二维码内容
        print(f"\n🔄 修复二维码内容...")

        # 将所有占位符URL替换为正确的地址
        conn.execute(text("""
            UPDATE tables
            SET qrcode_content = 'http://129.226.196.76/restaurant/customer_order.html?store_id=2&table_id=' || id
            WHERE store_id = 2
            AND qrcode_content LIKE 'https://your-domain.com%'
        """))
        conn.commit()

        # 验证修复结果
        print(f"\n✅ 修复后的二维码内容：")
        result = conn.execute(text("""
            SELECT id, table_name, qrcode_content
            FROM tables
            WHERE store_id = 2
            ORDER BY id
            LIMIT 5
        """))

        tables = result.fetchall()
        for table in tables:
            print(f"      桌号{table[0]}: {table[2]}")

        print(f"\n🎉 二维码内容已修复！")

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
