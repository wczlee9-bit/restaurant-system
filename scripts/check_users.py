"""
查看用户列表
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy.orm import Session
from storage.database.db import get_session
from storage.database.shared.model import Users

def check_users():
    """查看用户列表"""
    db: Session = get_session()

    try:
        users = db.query(Users).all()

        print(f"数据库中的用户列表（共 {len(users)} 个）：")
        for user in users:
            print(f"  ID: {user.id}, 用户名: {user.username}, 姓名: {user.name}, 手机: {user.phone}")

    finally:
        db.close()

if __name__ == "__main__":
    check_users()
