"""
遗留模块适配器
将现有的 API 路由封装为模块
"""

from typing import List, Dict, Any
import logging

from core.module_base import BaseModule

logger = logging.getLogger(__name__)


class LegacyModule(BaseModule):
    """
    遗留模块适配器
    
    职责：
    - 将现有的 FastAPI 路由封装为模块
    - 保持现有功能不变
    - 提供模块化接口
    
    使用场景：
    - 将现有系统快速迁移到模块化架构
    - 无需重写业务逻辑
    - 保持向后兼容
    """
    
    def __init__(self, name: str, router, version: str = "1.0.0"):
        """
        初始化遗留模块
        
        Args:
            name: 模块名称
            router: FastAPI 路由对象
            version: 模块版本
        """
        self._name = name
        self._router = router
        self._version = version
        self._initialized = False
        
        logger.info(f"LegacyModule created: {name}")
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def description(self) -> str:
        return f"遗留模块 - {self._name}"
    
    def initialize(self, dependencies: Dict[str, BaseModule]):
        """
        初始化模块
        
        对于遗留模块，无需特殊初始化
        路由已经在外部定义好了
        """
        logger.info(f"LegacyModule initialized: {self._name}")
        self._initialized = True
    
    def shutdown(self):
        """关闭模块"""
        logger.info(f"LegacyModule shutdown: {self._name}")
        self._initialized = False
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            Dict[str, Any]: 健康状态
        """
        return {
            "name": self._name,
            "version": self._version,
            "status": "healthy",
            "type": "legacy"
        }
    
    def get_routes(self) -> List:
        """
        获取模块的路由
        
        Returns:
            List: FastAPI 路由列表
        """
        if self._router:
            return [self._router]
        return []
    
    @property
    def router(self):
        """获取路由对象"""
        return self._router
