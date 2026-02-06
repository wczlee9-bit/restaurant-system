"""
遗留小票模块
封装现有的小票 API
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from modules.legacy.base_module import LegacyModule

# 导入现有的小票路由
try:
    from src.api.receipt_api import router as receipt_router
except ImportError as e:
    print(f"Warning: Could not import receipt_api: {e}")
    from fastapi import APIRouter
    receipt_router = APIRouter()

# 创建模块实例
module_instance = LegacyModule(
    name="LegacyReceiptModule",
    router=receipt_router,
    version="1.0.0"
)
