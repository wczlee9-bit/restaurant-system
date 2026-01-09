"""
数据库迁移脚本：添加优惠配置和会员二维码表
创建日期：2024-01-15
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from src.storage.database.db import get_session

def migrate():
    """执行数据库迁移"""
    db = get_session()
    try:
        print("开始数据库迁移...")
        
        # 创建优惠配置表
        print("创建 discount_config 表...")
        db.execute(text("""
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
                description TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT now(),
                updated_at TIMESTAMP
            );
        """))
        
        # 创建索引
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_discount_config_store ON discount_config(store_id);
        """))
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_discount_config_company ON discount_config(company_id);
        """))
        
        # 创建会员二维码表
        print("创建 member_qrcodes 表...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS member_qrcodes (
                id SERIAL PRIMARY KEY,
                member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
                qr_code_url VARCHAR(500) NOT NULL,
                qr_code_key VARCHAR(255) NOT NULL,
                valid_from TIMESTAMP NOT NULL DEFAULT now(),
                valid_until TIMESTAMP,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                scan_count INTEGER NOT NULL DEFAULT 0,
                last_scan_time TIMESTAMP,
                created_at TIMESTAMP NOT NULL DEFAULT now(),
                updated_at TIMESTAMP,
                UNIQUE(member_id)
            );
        """))
        
        db.commit()
        print("数据库迁移完成！")
        print("✅ 已创建表：discount_config（优惠配置）")
        print("✅ 已创建表：member_qrcodes（会员二维码）")
        print("✅ 已创建索引")
        
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ 数据库迁移失败: {str(e)}")
        return False
    finally:
        db.close()

def rollback():
    """回滚数据库迁移"""
    db = get_session()
    try:
        print("开始回滚数据库迁移...")
        
        # 删除表
        db.execute(text("DROP TABLE IF EXISTS member_qrcodes;"))
        db.execute(text("DROP TABLE IF EXISTS discount_config;"))
        
        db.commit()
        print("数据库迁移回滚完成！")
        print("✅ 已删除表：member_qrcodes")
        print("✅ 已删除表：discount_config")
        
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ 回滚失败: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()
