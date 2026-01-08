"""
创建Staff记录
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy.orm import Session
from storage.database.db import get_session
from storage.database.shared.model import Staff

def create_staff():
    """创建Staff记录"""
    db: Session = get_session()

    try:
        # 检查是否已存在
        existing = db.query(Staff).filter(
            Staff.user_id == 28,
            Staff.store_id == 9
        ).first()

        if existing:
            print(f"✓ Staff记录已存在: 用户ID {existing.user_id}, 店铺ID {existing.store_id}")
            return existing

        # 创建新记录
        staff = Staff(
            user_id=28,
            store_id=9,
            position="店长",
            is_active=True
        )
        db.add(staff)
        db.commit()
        db.refresh(staff)

        print(f"✓ 创建Staff记录成功: 用户ID {staff.user_id}, 店铺ID {staff.store_id}")
        return staff

    except Exception as e:
        db.rollback()
        print(f"❌ 创建失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_staff()
