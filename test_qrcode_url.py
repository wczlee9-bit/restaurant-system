#!/usr/bin/env python3
"""临时脚本：检查二维码图片URL是否可访问"""

import os
import requests
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
        # 查看二维码图片URL
        print(f"\n📋 检查二维码图片URL：")
        result = conn.execute(text("""
            SELECT id, table_name, qrcode_url
            FROM tables
            WHERE store_id = 2
            ORDER BY id
            LIMIT 3
        """))

        tables = result.fetchall()

        print(f"   测试二维码图片是否可访问：\n")

        for table in tables:
            url = table[2]
            print(f"      桌号{table[0]} ({table[1]}):")
            print(f"      URL: {url}")

            if url:
                try:
                    response = requests.head(url, timeout=5)
                    status = "✅ 可访问" if response.status_code == 200 else f"❌ 失败 ({response.status_code})"
                    print(f"      状态: {status}")
                except Exception as e:
                    print(f"      状态: ❌ 错误 - {str(e)[:50]}")
            else:
                print(f"      状态: ❌ URL为空")

            print(f"\n")

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
