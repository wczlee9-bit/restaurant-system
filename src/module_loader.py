"""
模块加载器
负责加载和管理所有业务模块
"""

import json
import logging
from pathlib import Path
from typing import Dict, List
import sys

# 添加项目根目录到 Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.module_base import ModuleRegistry

logger = logging.getLogger(__name__)


class ModuleLoader:
    """模块加载器"""
    
    def __init__(self, config_path: str = "config/modules.json"):
        """
        初始化模块加载器
        
        Args:
            config_path: 模块配置文件路径
        """
        self.config_path = config_path
        self.config = None
        self.registry = ModuleRegistry()
        self._initialized = False
    
    def load_config(self) -> Dict:
        """加载模块配置"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            logger.warning(f"Module config not found: {self.config_path}")
            return {"modules": [], "legacy_mode": False}
        
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        logger.info(f"Loaded module config: {len(self.config.get('modules', []))} modules")
        return self.config
    
    def load_modules(self) -> ModuleRegistry:
        """
        加载所有模块
        
        Returns:
            ModuleRegistry: 模块注册器
        """
        if self._initialized:
            logger.warning("Modules already loaded")
            return self.registry
        
        config = self.load_config()
        
        # 按优先级排序模块
        modules_config = sorted(
            config.get('modules', []),
            key=lambda x: x.get('priority', 0)
        )
        
        loaded_count = 0
        failed_count = 0
        
        for module_config in modules_config:
            if not module_config.get('enabled', True):
                logger.info(f"Skipping disabled module: {module_config.get('name')}")
                continue
            
            try:
                self._load_single_module(module_config)
                loaded_count += 1
            except Exception as e:
                logger.error(f"Failed to load module {module_config.get('name')}: {e}")
                failed_count += 1
                if not config.get('fallback_to_traditional', True):
                    raise
        
        logger.info(f"Modules loaded: {loaded_count} success, {failed_count} failed")
        
        return self.registry
    
    def _load_single_module(self, module_config: Dict):
        """
        加载单个模块
        
        Args:
            module_config: 模块配置
        """
        module_path = module_config['module']
        module_name = module_config['name']
        
        logger.info(f"Loading module: {module_name}")
        
        # 动态导入模块
        import importlib
        module = importlib.import_module(module_path)
        
        # 获取模块实例
        if hasattr(module, 'module_instance'):
            module_instance = module.module_instance
        elif hasattr(module, 'create_module'):
            module_instance = module.create_module()
        else:
            # 尝试直接获取模块类
            module_class = getattr(module, module_name.replace('Legacy', '').replace('Module', ''))
            module_instance = module_class()
        
        # 注册模块
        self.registry.register(module_instance)
    
    def initialize_all(self) -> bool:
        """
        初始化所有模块
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.registry.initialize_all()
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize modules: {e}")
            return False
    
    def get_registry(self) -> ModuleRegistry:
        """获取模块注册器"""
        return self.registry
    
    def shutdown_all(self):
        """关闭所有模块"""
        self.registry.shutdown_all()
        self._initialized = False


def create_modular_app() -> ModuleRegistry:
    """
    创建模块化应用
    
    Returns:
        ModuleRegistry: 模块注册器
    """
    loader = ModuleLoader()
    loader.load_modules()
    loader.initialize_all()
    return loader.get_registry()


# 导出全局注册器实例
_global_registry = None


def get_global_registry() -> ModuleRegistry:
    """
    获取全局模块注册器
    
    Returns:
        ModuleRegistry: 模块注册器
    """
    global _global_registry
    
    if _global_registry is None:
        _global_registry = create_modular_app()
    
    return _global_registry


def reset_global_registry():
    """重置全局模块注册器（用于测试）"""
    global _global_registry
    
    if _global_registry is not None:
        _global_registry.shutdown_all()
        _global_registry = None


if __name__ == "__main__":
    # 测试模块加载
    logging.basicConfig(level=logging.INFO)
    
    try:
        registry = create_modular_app()
        
        print("\n=== 已加载模块 ===")
        for name, module in registry.get_all_modules().items():
            print(f"  - {name} v{module.version}")
        
        print("\n=== 健康检查 ===")
        health = registry.health_check()
        print(json.dumps(health, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
