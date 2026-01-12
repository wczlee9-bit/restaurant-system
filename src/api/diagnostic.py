"""
诊断端点
用于检查系统状态、环境变量、数据库连接等
"""
import os
import logging
from fastapi import APIRouter
from sqlalchemy import text

router = APIRouter(tags=["diagnostic"])
logger = logging.getLogger(__name__)


@router.get("/api/diagnostic/env")
def check_environment():
    """检查环境变量"""
    env_vars = {
        "PGDATABASE_URL": "✓ 已设置" if os.getenv("PGDATABASE_URL") else "✗ 未设置",
        "PORT": os.getenv("PORT", "8000"),
        "PYTHON_VERSION": os.getenv("PYTHON_VERSION", "未设置"),
    }

    # 检查其他重要环境变量（隐藏敏感信息）
    for key in os.environ:
        if key.startswith("AWS_") or key.startswith("S3_"):
            env_vars[key] = "✓ 已设置"

    return {
        "status": "success",
        "environment": env_vars
    }


@router.get("/api/diagnostic/database")
def check_database():
    """检查数据库连接"""
    from storage.database.db import get_engine, get_session

    result = {
        "engine_created": False,
        "connection_successful": False,
        "tables_exist": False,
        "error": None
    }

    try:
        # 尝试创建引擎
        engine = get_engine()
        result["engine_created"] = True
        logger.info("✓ Database engine created")

        # 尝试连接并执行简单查询
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            result["connection_successful"] = True
            logger.info("✓ Database connection successful")

        # 检查表是否存在
        from storage.database.shared.model import Base
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        result["tables"] = tables
        result["tables_count"] = len(tables)
        result["tables_exist"] = len(tables) > 0
        logger.info(f"✓ Found {len(tables)} tables")

        # 检查是否有数据
        session = get_session()
        from storage.database.shared.model import Stores, MenuCategories, Tables

        store_count = session.query(Stores).count()
        category_count = session.query(MenuCategories).count()
        table_count = session.query(Tables).count()

        result["data"] = {
            "stores": store_count,
            "categories": category_count,
            "tables": table_count
        }
        logger.info(f"✓ Data: stores={store_count}, categories={category_count}, tables={table_count}")

        session.close()

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"✗ Database check failed: {e}")
        import traceback
        result["traceback"] = traceback.format_exc()

    return result


@router.get("/api/diagnostic/health")
def health_check():
    """完整健康检查"""
    db_status = check_database()

    return {
        "status": "healthy" if db_status["connection_successful"] else "unhealthy",
        "database": db_status,
        "environment": check_environment()["environment"]
    }


@router.post("/api/diagnostic/reinit-data")
def reinitialize_data():
    """重新初始化测试数据"""
    from storage.database.init_db import ensure_test_data

    logger.info("Reinitializing test data...")

    # 先重置数据库表
    from storage.database.db import get_engine
    from storage.database.shared.model import Base
    from storage.database.init_db import init_database

    try:
        engine = get_engine()
        # 删除所有表并重新创建
        Base.metadata.drop_all(bind=engine)
        logger.info("Dropped all tables")

        # 重新创建表
        if init_database():
            logger.info("Database schema recreated")

            # 初始化测试数据
            success = ensure_test_data()

            if success:
                return {
                    "status": "success",
                    "message": "Database reset and test data initialized successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": "Database schema recreated but failed to initialize test data",
                    "detail": "Check server logs for more information"
                }, 500
        else:
            return {
                "status": "error",
                "message": "Failed to recreate database schema"
            }, 500
    except Exception as e:
        logger.error(f"Failed to reinitialize data: {e}")
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }, 500
