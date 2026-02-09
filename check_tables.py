#!/usr/bin/env python3
"""临时脚本：查看tables表结构"""

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
        # 查看tables表结构
        print(f"\n📋 Tables表结构：")
        result = conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'tables'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        
        if len(columns) == 0:
            print(f"❌ 没有找到tables表")
            
            # 查看所有表
            print(f"\n📋 数据库中的所有表：")
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            for table in tables:
                print(f"      - {table[0]}")
        else:
            print(f"   可用字段：")
            for col in columns:
                print(f"      - {col[0]} ({col[1]})")
            
            # 查看所有桌号
            print(f"\n📋 所有桌号数据：")
            result = conn.execute(text("SELECT * FROM tables ORDER BY id LIMIT 20"))
            tables = result.fetchall()
            
            if len(tables) == 0:
                print(f"   ❌ 没有桌号数据")
            else:
                print(f"   共找到 {len(tables)} 个桌号:")
                for table in tables:
                    print(f"      {table}\n")
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
