"""
检查数据库表是否存在
"""
from sqlalchemy import inspect

def check_tables_exist(engine):
    """检查表是否存在"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    required_tables = [
        'companies', 'users', 'stores', 'menu_categories', 'menu_items',
        'tables', 'orders', 'order_items', 'member_level_rules', 'members'
    ]

    missing_tables = [t for t in required_tables if t not in tables]

    return {
        'exists_tables': tables,
        'missing_tables': missing_tables,
        'all_exist': len(missing_tables) == 0
    }
