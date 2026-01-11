"""
初始化数据库
在 API 启动时自动创建表结构和初始化基础数据
"""
import sys
import os
import logging

logger = logging.getLogger(__name__)

def init_database():
    """初始化数据库表结构"""
    try:
        from storage.database.db import get_engine
        from storage.database.shared.model import Base

        engine = get_engine()
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        return False

def ensure_test_data():
    """确保基础测试数据存在"""
    try:
        from storage.database.db import get_session
        from storage.database.shared.model import (
            Companies, Users, Stores, MenuCategories, MenuItems, Tables
        )

        db = get_session()

        # 检查是否已有数据
        store_count = db.query(Stores).count()
        if store_count > 0:
            logger.info(f"Database already has {store_count} stores, skipping init")
            return True

        logger.info("Initializing test data...")

        # 创建公司
        company = Companies(
            name="测试餐饮公司",
            is_active=True,
            contact_person="管理员",
            contact_phone="13800138000",
            address="测试地址"
        )
        db.add(company)
        db.flush()

        # 创建店铺
        store = Stores(
            company_id=company.id,
            name="美味餐厅",
            is_active=True,
            address="北京市海淀区测试街88号",
            phone="010-12345678",
            opening_hours={
                "monday": {"open": "09:00", "close": "22:00"},
                "tuesday": {"open": "09:00", "close": "22:00"},
                "wednesday": {"open": "09:00", "close": "22:00"},
                "thursday": {"open": "09:00", "close": "22:00"},
                "friday": {"open": "09:00", "close": "22:00"},
                "saturday": {"open": "10:00", "close": "23:00"},
                "sunday": {"open": "10:00", "close": "23:00"}
            }
        )
        db.add(store)
        db.flush()

        # 创建菜品分类
        categories = [
            {"name": "热菜", "description": "各种热炒菜肴"},
            {"name": "凉菜", "description": "清爽凉菜"},
            {"name": "主食", "description": "米饭、面条等"},
            {"name": "饮品", "description": "各种饮料"}
        ]

        for i, cat_data in enumerate(categories):
            category = MenuCategories(
                store_id=store.id,
                name=cat_data["name"],
                description=cat_data["description"],
                is_active=True,
                sort_order=i + 1
            )
            db.add(category)
            db.flush()

        # 创建桌号
        for i in range(1, 11):
            table = Tables(
                store_id=store.id,
                table_number=f"A{i:02d}",
                seats=4,
                is_active=True,
                status="available"
            )
            db.add(table)

        db.commit()
        logger.info("✓ Test data initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize test data: {e}")
        import traceback
        traceback.print_exc()
        return False
