"""
遗留订单模块
封装现有的订单流程 API
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from modules.legacy.base_module import LegacyModule

# 导入现有的订单路由
try:
    from src.api.order_flow_api import router as order_router
except ImportError as e:
    print(f"Warning: Could not import order_flow_api: {e}")
    from fastapi import APIRouter
    order_router = APIRouter()

# 创建模块实例
module_instance = LegacyModule(
    name="LegacyOrderModule",
    router=order_router,
    version="1.0.0"
)
