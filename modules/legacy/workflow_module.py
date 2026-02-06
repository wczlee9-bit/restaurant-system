"""
遗留工作流模块
封装现有的工作流 API
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from modules.legacy.base_module import LegacyModule

# 导入现有的工作流路由
try:
    from src.api.workflow_api import router as workflow_router
except ImportError as e:
    print(f"Warning: Could not import workflow_api: {e}")
    from fastapi import APIRouter
    workflow_router = APIRouter()

# 创建模块实例
module_instance = LegacyModule(
    name="LegacyWorkflowModule",
    router=workflow_router,
    version="1.0.0"
)
