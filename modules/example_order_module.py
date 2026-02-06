"""
模块化架构示例 - 订单模块
展示如何创建一个独立的、可插拔的业务模块
"""

from typing import List, Dict
from fastapi import APIRouter
import logging

from core.module_base import BaseModule
from core.service_interfaces import (
    IMenuService, IUserService, IOrderService,
    OrderCreate, Order
)

logger = logging.getLogger(__name__)


class OrderModule(BaseModule):
    """
    订单模块
    
    职责：
    - 订单创建与查询
    - 订单状态管理
    - 与其他模块通过接口通信
    
    依赖：
    - MenuModule（获取菜品信息）
    - UserModule（获取用户信息）
    """
    
    @property
    def name(self) -> str:
        return "OrderModule"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "订单管理模块，负责订单的创建、查询和状态管理"
    
    def dependencies(self) -> List[str]:
        return ["MenuModule", "UserModule"]
    
    def initialize(self, dependencies: Dict[str, BaseModule]):
        """初始化订单模块"""
        # 通过依赖注入获取其他模块的服务
        menu_module = dependencies.get("MenuModule")
        user_module = dependencies.get("UserModule")
        
        if menu_module:
            self.menu_service = menu_module.service
            logger.info(f"OrderModule connected to MenuModule")
        
        if user_module:
            self.user_service = user_module.service
            logger.info(f"OrderModule connected to UserModule")
        
        # 创建订单服务
        self.service = OrderServiceImpl(self.menu_service, self.user_service)
        
        logger.info(f"{self.name} v{self.version} initialized")
    
    def get_routes(self) -> List:
        """获取模块的路由"""
        return [self._create_router()]
    
    def _create_router(self) -> APIRouter:
        """创建路由"""
        router = APIRouter(prefix="/api/orders", tags=["订单管理"])
        
        @router.post("/")
        def create_order(order_data: OrderCreate):
            """创建订单"""
            return self.service.create_order(order_data)
        
        @router.get("/{order_id}")
        def get_order(order_id: int):
            """获取订单"""
            return self.service.get_order(order_id)
        
        @router.put("/{order_id}/status")
        def update_status(order_id: int, status: str):
            """更新订单状态"""
            return {"success": self.service.update_order_status(order_id, status)}
        
        @router.get("/status/{status}")
        def get_orders_by_status(status: str):
            """根据状态获取订单"""
            return self.service.get_orders_by_status(status)
        
        return router


class OrderServiceImpl(IOrderService):
    """
    订单服务实现
    
    注意：这个类只实现业务逻辑
    不直接依赖其他模块的具体实现
    """
    
    def __init__(self, menu_service: IMenuService, user_service: IUserService):
        """
        初始化订单服务
        
        Args:
            menu_service: 菜单服务接口（通过依赖注入）
            user_service: 用户服务接口（通过依赖注入）
        """
        self.menu_service = menu_service
        self.user_service = user_service
        # 这里可以注入数据库仓库
        # self.order_repository = OrderRepository()
        self._orders = {}  # 临时存储，实际应使用数据库
    
    def create_order(self, order_data: OrderCreate) -> Order:
        """
        创建订单
        
        业务逻辑：
        1. 验证菜品是否存在
        2. 验证库存是否充足
        3. 计算订单金额
        4. 扣减库存
        5. 保存订单
        """
        total_amount = 0.0
        
        # 遍历订单项，验证菜品和库存
        for item in order_data.items:
            # 通过接口获取菜品信息（不依赖具体实现）
            menu_item = self.menu_service.get_item(item.item_id)
            if not menu_item:
                raise ValueError(f"菜品 {item.item_id} 不存在")
            
            # 计算金额
            subtotal = menu_item.price * item.quantity
            total_amount += subtotal
            
            # 通过接口扣减库存（不依赖具体实现）
            if not self.menu_service.update_stock(item.item_id, -item.quantity):
                raise ValueError(f"菜品 {menu_item.name} 库存不足")
        
        # 创建订单
        order = Order(
            id=len(self._orders) + 1,
            order_number=f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{len(self._orders) + 1}",
            store_id=order_data.store_id,
            table_id=order_data.table_id,
            total_amount=total_amount,
            status="pending",
            payment_status="unpaid",
            created_at=datetime.now()
        )
        
        # 保存订单
        self._orders[order.id] = order
        
        logger.info(f"Order created: {order.order_number}, amount: {total_amount}")
        
        return order
    
    def get_order(self, order_id: int) -> Order:
        """获取订单"""
        return self._orders.get(order_id)
    
    def update_order_status(self, order_id: int, status: str) -> bool:
        """更新订单状态"""
        order = self._orders.get(order_id)
        if not order:
            return False
        
        # 状态流转验证
        valid_transitions = {
            "pending": ["confirmed", "cancelled"],
            "confirmed": ["preparing", "cancelled"],
            "preparing": ["ready", "cancelled"],
            "ready": ["served"],
            "served": ["completed"],
            "completed": [],
            "cancelled": []
        }
        
        if status not in valid_transitions.get(order.status, []):
            raise ValueError(f"Invalid status transition: {order.status} -> {status}")
        
        order.status = status
        logger.info(f"Order {order_id} status updated to: {status}")
        
        return True
    
    def get_orders_by_status(self, status: str) -> List[Order]:
        """根据状态获取订单列表"""
        return [order for order in self._orders.values() if order.status == status]


from datetime import datetime  # 补充导入
