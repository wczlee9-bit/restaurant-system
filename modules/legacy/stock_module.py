"""
遗留库存模块
封装现有的库存 API
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from modules.legacy.base_module import LegacyModule

# 导入现有的库存路由（可能在 restaurant_api 中）
try:
    from src.api.restaurant_api import router as stock_router
except ImportError as e:
    print(f"Warning: Could not import stock_api: {e}")
    from fastapi import APIRouter
    stock_router = APIRouter()

# 创建模块实例
module_instance = LegacyModule(
    name="LegacyStockModule",
    router=stock_router,
    version="1.0.0"
)
