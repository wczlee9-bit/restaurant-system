"""
模块化架构 - 应用入口
展示如何使用模块注册器启动应用
"""

from fastapi import FastAPI
import logging

from core.module_base import registry
from core.service_interfaces import BaseModule

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class ModularApplication:
    """
    模块化应用
    
    使用模块注册器管理所有模块的生命周期
    """
    
    def __init__(self, title: str = "餐厅管理系统"):
        self.app = FastAPI(
            title=title,
            description="基于模块化架构的餐厅管理系统",
            version="1.0.0"
        )
        self._initialized = False
    
    def register_module(self, module: BaseModule):
        """
        注册模块
        
        Args:
            module: 模块实例
        """
        registry.register(module)
        logger.info(f"Module registered: {module.name}")
    
    def initialize_modules(self):
        """初始化所有模块"""
        if self._initialized:
            logger.warning("Modules already initialized")
            return
        
        registry.initialize_all()
        self._initialized = True
        
        # 注册所有路由
        for router in registry.get_all_routes():
            self.app.include_router(router)
        
        logger.info("All routes registered")
    
    def shutdown_modules(self):
        """关闭所有模块"""
        registry.shutdown_all()
        self._initialized = False
    
    def get_app(self) -> FastAPI:
        """获取 FastAPI 应用实例"""
        if not self._initialized:
            raise RuntimeError("Modules not initialized. Call initialize_modules() first.")
        return self.app
    
    @property
    def health(self) -> dict:
        """应用健康状态"""
        return registry.health_check()


def create_app() -> FastAPI:
    """
    创建应用
    
    使用示例：
    ```python
    app = create_app()
    
    # 添加中间件
    app.add_middleware(...)
    
    # 添加根路径
    @app.get("/")
    def root():
        return {"message": "餐厅管理系统", "version": "1.0.0"}
    
    return app
    ```
    """
    # 创建模块化应用
    mod_app = ModularApplication()
    
    # 注册基础设施模块
    # from infrastructure.database.module import DatabaseModule
    # mod_app.register_module(DatabaseModule())
    
    # 注册业务模块
    # from modules.auth.module import AuthModule
    # from modules.menu.module import MenuModule
    # from modules.user.module import UserModule
    # from modules.order.module import OrderModule
    # from modules.stock.module import StockModule
    # from modules.member.module import MemberModule
    # from modules.stats.module import StatsModule
    # from modules.receipt.module import ReceiptModule
    # from modules.websocket.module import WebSocketModule
    
    # mod_app.register_module(AuthModule())
    # mod_app.register_module(MenuModule())
    # mod_app.register_module(UserModule())
    # mod_app.register_module(OrderModule())
    # mod_app.register_module(StockModule())
    # mod_app.register_module(MemberModule())
    # mod_app.register_module(StatsModule())
    # mod_app.register_module(ReceiptModule())
    # mod_app.register_module(WebSocketModule())
    
    # 初始化所有模块（按依赖顺序）
    # mod_app.initialize_modules()
    
    # 获取 FastAPI 应用
    # return mod_app.get_app()
    
    # 临时返回一个简单应用用于演示
    app = FastAPI(title="餐厅管理系统")
    
    @app.get("/")
    def root():
        return {
            "message": "餐厅管理系统",
            "version": "1.0.0",
            "architecture": "Modular"
        }
    
    @app.get("/health")
    def health():
        return {"status": "ok"}
    
    return app


if __name__ == "__main__":
    import uvicorn
    
    # 创建应用
    app = create_app()
    
    # 启动服务
    uvicorn.run(app, host="0.0.0.0", port=8001)
