"""
模块化架构 - 核心框架
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseModule(ABC):
    """
    所有模块的基础接口
    
    每个业务模块都必须继承这个基类
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """模块名称（必须唯一）"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """模块版本号（遵循语义化版本）"""
        pass
    
    @property
    def description(self) -> str:
        """模块描述"""
        return ""
    
    def dependencies(self) -> List[str]:
        """
        依赖的模块列表
        
        Returns:
            List[str]: 依赖的模块名称列表
        """
        return []
    
    @abstractmethod
    def initialize(self, dependencies: Dict[str, 'BaseModule']):
        """
        初始化模块
        
        Args:
            dependencies: 依赖的模块字典 {模块名: 模块实例}
        """
        pass
    
    def shutdown(self):
        """关闭模块，清理资源"""
        logger.info(f"Module {self.name} shutdown")
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            Dict[str, Any]: 健康状态信息
        """
        return {
            "name": self.name,
            "version": self.version,
            "status": "healthy"
        }
    
    def get_routes(self) -> List:
        """
        获取模块的路由列表
        
        Returns:
            List: FastAPI 路由列表
        """
        return []


class ModuleRegistry:
    """
    模块注册器
    
    负责管理所有模块的生命周期
    """
    
    def __init__(self):
        self._modules: Dict[str, BaseModule] = {}
        self._initialized = False
    
    def register(self, module: BaseModule):
        """
        注册模块
        
        Args:
            module: 模块实例
        """
        if module.name in self._modules:
            raise ValueError(f"Module {module.name} already registered")
        
        self._modules[module.name] = module
        logger.info(f"Module {module.name} v{module.version} registered")
    
    def get_module(self, name: str) -> Optional[BaseModule]:
        """
        获取模块
        
        Args:
            name: 模块名称
        
        Returns:
            BaseModule: 模块实例，如果不存在返回 None
        """
        return self._modules.get(name)
    
    def get_all_modules(self) -> Dict[str, BaseModule]:
        """获取所有模块"""
        return self._modules.copy()
    
    def initialize_all(self):
        """初始化所有模块（按依赖顺序）"""
        if self._initialized:
            logger.warning("Modules already initialized")
            return
        
        # 拓扑排序，按依赖顺序初始化
        sorted_modules = self._topological_sort()
        
        for module_name in sorted_modules:
            module = self._modules[module_name]
            
            # 准备依赖
            dependencies = {}
            for dep_name in module.dependencies():
                dep_module = self._modules.get(dep_name)
                if dep_module is None:
                    raise RuntimeError(f"Dependency {dep_name} not found for module {module.name}")
                dependencies[dep_name] = dep_module
            
            # 初始化模块
            try:
                module.initialize(dependencies)
                logger.info(f"Module {module.name} initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize module {module.name}: {e}")
                raise
        
        self._initialized = True
        logger.info(f"All {len(self._modules)} modules initialized")
    
    def shutdown_all(self):
        """关闭所有模块"""
        for module in self._modules.values():
            try:
                module.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down module {module.name}: {e}")
        
        self._initialized = False
        logger.info("All modules shutdown")
    
    def health_check(self) -> Dict[str, Any]:
        """
        检查所有模块的健康状态
        
        Returns:
            Dict[str, Any]: 健康状态
        """
        health_status = {}
        for name, module in self._modules.items():
            try:
                health_status[name] = module.health_check()
            except Exception as e:
                health_status[name] = {
                    "name": name,
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "overall_status": "healthy" if all(m["status"] == "healthy" for m in health_status.values()) else "degraded",
            "modules": health_status
        }
    
    def get_all_routes(self) -> List:
        """
        获取所有模块的路由
        
        Returns:
            List: 所有路由列表
        """
        routes = []
        for module in self._modules.values():
            routes.extend(module.get_routes())
        return routes
    
    def _topological_sort(self) -> List[str]:
        """
        拓扑排序，返回模块初始化顺序
        
        Returns:
            List[str]: 排序后的模块名称列表
        """
        # 构建依赖图
        in_degree = {name: 0 for name in self._modules}
        adj_list = {name: [] for name in self._modules}
        
        for name, module in self._modules.items():
            for dep in module.dependencies():
                if dep in self._modules:
                    adj_list[dep].append(name)
                    in_degree[name] += 1
        
        # 拓扑排序
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in adj_list[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(self._modules):
            raise RuntimeError("Circular dependency detected in modules")
        
        return result


# 全局模块注册器实例
registry = ModuleRegistry()
