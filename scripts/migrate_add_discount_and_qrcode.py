#!/usr/bin/env python3
"""
数据库迁移脚本：添加优惠配置和会员二维码功能
创建表：discount_config, member_qrcodes
"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from storage.database.db import get_session

def migrate():
    """执行数据库迁移"""
    print("开始执行数据库迁移：添加优惠配置和会员二维码功能...")

    try:
        session = get_session()

        # 创建 discount_config 表
        print("创建 discount_config 表...")
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS discount_config (
                id SERIAL PRIMARY KEY,
                store_id INTEGER REFERENCES stores(id) ON DELETE CASCADE,
                company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                discount_type VARCHAR(50) NOT NULL,
                discount_value DOUBLE PRECISION NOT NULL,
                min_amount DOUBLE PRECISION,
                max_discount DOUBLE PRECISION,
                member_level INTEGER,
                points_required INTEGER,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                valid_from TIMESTAMP,
                valid_until TIMESTAMP,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                description TEXT,
                updated_at TIMESTAMP
            );
        """))

        # 创建索引
        session.execute(text("CREATE INDEX IF NOT EXISTS ix_discount_config_store ON discount_config(store_id);"))
        session.execute(text("CREATE INDEX IF NOT EXISTS ix_discount_config_company ON discount_config(company_id);"))
        print("✓ discount_config 表创建成功")

        # 创建 member_qrcodes 表
        print("创建 member_qrcodes 表...")
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS member_qrcodes (
                id SERIAL PRIMARY KEY,
                member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
                qr_code_url VARCHAR(500) NOT NULL,
                qr_code_key VARCHAR(255) NOT NULL,
                valid_from TIMESTAMP NOT NULL DEFAULT NOW(),
                valid_until TIMESTAMP,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                scan_count INTEGER NOT NULL DEFAULT 0,
                last_scan_time TIMESTAMP,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP,
                UNIQUE (member_id)
            );
        """))
        print("✓ member_qrcodes 表创建成功")

        # 提交事务
        session.commit()
        print("\n✅ 数据库迁移成功完成！")
        print("\n已创建的表：")
        print("  - discount_config (优惠配置表)")
        print("  - member_qrcodes (会员二维码表)")
        print("\n接下来可以运行增强API服务：")
        print("  python scripts/start_api_services.py")

    except Exception as e:
        print(f"\n❌ 数据库迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    migrate()
