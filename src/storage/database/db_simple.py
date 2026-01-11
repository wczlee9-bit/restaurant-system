"""
简化的数据库连接模块
用于测试和快速部署
"""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

def get_db_url() -> str:
    """Build database URL from environment."""
    url = os.getenv("PGDATABASE_URL") or ""
    if url is not None and url != "":
        # 强制使用 psycopg2
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            logger.info("Using psycopg2 driver")
        logger.info("PGDATABASE_URL loaded from environment variable")
        return url
    
    logger.error("PGDATABASE_URL is not set in environment variables")
    raise ValueError("PGDATABASE_URL is not set. Please set PGDATABASE_URL environment variable.")

_engine = None
_SessionLocal = None

def get_engine():
    global _engine
    if _engine is None:
        url = get_db_url()
        _engine = create_engine(url, pool_pre_ping=True)
        
        # 测试连接
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("Database connected successfully")
    return _engine

def get_sessionmaker():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

def get_session():
    return get_sessionmaker()()

__all__ = [
    "get_db_url",
    "get_engine",
    "get_sessionmaker",
    "get_session",
]
