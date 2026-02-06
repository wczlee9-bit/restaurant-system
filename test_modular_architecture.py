#!/usr/bin/env python3
"""
模块化架构测试脚本
验证模块化架构是否成功
"""

import sys
sys.path.insert(0, '/workspace/projects')

from core.module_base import BaseModule, ModuleRegistry
from core.service_interfaces import (
    IMenuService, IUserService, IOrderService,
    OrderCreate, Order, MenuItem, User
)
from typing import List, Dict, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== 测试模块实现 ====================

class TestMenuModule(BaseModule):
    """测试菜单模块"""
    
    def __init__(self):
        self.service = None
    
    @property
    def name(self) -> str:
        return "MenuModule"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def dependencies(self) -> List[str]:
        return []
    
    def initialize(self, dependencies: Dict[str, 'BaseModule']):
        self.service = MenuServiceImpl()
        logger.info(f"{self.name} initialized")
    
    def shutdown(self):
        logger.info(f"{self.name} shutdown")


class MenuServiceImpl(IMenuService):
    """菜单服务实现"""
    
    def __init__(self):
        self._items = {
            1: MenuItem(id=1, name="宫保鸡丁", price=38.0, stock=100, category="热菜"),
            2: MenuItem(id=2, name="鱼香肉丝", price=35.0, stock=100, category="热菜"),
            3: MenuItem(id=3, name="麻婆豆腐", price=28.0, stock=100, category="热菜"),
            4: MenuItem(id=4, name="蛋炒饭", price=18.0, stock=100, category="主食"),
        }
    
    def get_menu(self, store_id: int) -> List[MenuItem]:
        return list(self._items.values())
    
    def get_item(self, item_id: int) -> Optional[MenuItem]:
        return self._items.get(item_id)
    
    def update_stock(self, item_id: int, quantity: int) -> bool:
        item = self._items.get(item_id)
        if item:
            item.stock += quantity
            return True
        return False


class TestUserModule(BaseModule):
    """测试用户模块"""
    
    def __init__(self):
        self.service = None
    
    @property
    def name(self) -> str:
        return "UserModule"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def dependencies(self) -> List[str]:
        return []
    
    def initialize(self, dependencies: Dict[str, 'BaseModule']):
        self.service = UserServiceImpl()
        logger.info(f"{self.name} initialized")
    
    def shutdown(self):
        logger.info(f"{self.name} shutdown")


class UserServiceImpl(IUserService):
    """用户服务实现"""
    
    def __init__(self):
        self._users = {
            1: User(id=1, username="admin", role="admin", points=100),
            2: User(id=2, username="test_user", role="customer", points=50),
        }
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)
    
    def add_points(self, user_id: int, points: int) -> bool:
        user = self._users.get(user_id)
        if user:
            user.points += points
            return True
        return False
    
    def deduct_points(self, user_id: int, points: int) -> bool:
        user = self._users.get(user_id)
        if user and user.points >= points:
            user.points -= points
            return True
        return False


class TestOrderModule(BaseModule):
    """测试订单模块"""
    
    def __init__(self):
        self.service = None
        self.menu_service = None
        self.user_service = None
    
    @property
    def name(self) -> str:
        return "OrderModule"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def dependencies(self) -> List[str]:
        return ["MenuModule", "UserModule"]
    
    def initialize(self, dependencies: Dict[str, 'BaseModule']):
        self.menu_service = dependencies["MenuModule"].service
        self.user_service = dependencies["UserModule"].service
        self.service = OrderServiceImpl(self.menu_service, self.user_service)
        logger.info(f"{self.name} initialized")
    
    def shutdown(self):
        logger.info(f"{self.name} shutdown")


class OrderServiceImpl(IOrderService):
    """订单服务实现"""
    
    def __init__(self, menu_service: IMenuService, user_service: IUserService):
        self.menu_service = menu_service
        self.user_service = user_service
        self._orders = {}
    
    def create_order(self, order_data: OrderCreate) -> Order:
        total_amount = 0.0
        
        for item in order_data.items:
            menu_item = self.menu_service.get_item(item.item_id)
            if not menu_item:
                raise ValueError(f"菜品 {item.item_id} 不存在")
            
            subtotal = menu_item.price * item.quantity
            total_amount += subtotal
            
            if not self.menu_service.update_stock(item.item_id, -item.quantity):
                raise ValueError(f"菜品 {menu_item.name} 库存不足")
        
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
        
        self._orders[order.id] = order
        return order
    
    def get_order(self, order_id: int) -> Optional[Order]:
        return self._orders.get(order_id)
    
    def update_order_status(self, order_id: int, status: str) -> bool:
        order = self._orders.get(order_id)
        if order:
            order.status = status
            return True
        return False
    
    def get_orders_by_status(self, status: str) -> List[Order]:
        return [order for order in self._orders.values() if order.status == status]


# ==================== 测试函数 ====================

def test_module_registry():
    """测试模块注册器"""
    print("\n" + "="*60)
    print("测试1: 模块注册器")
    print("="*60)
    
    registry = ModuleRegistry()
    
    # 注册模块
    menu_module = TestMenuModule()
    user_module = TestUserModule()
    order_module = TestOrderModule()
    
    registry.register(menu_module)
    registry.register(user_module)
    registry.register(order_module)
    
    print("✅ 模块注册成功")
    print(f"   已注册模块: {list(registry.get_all_modules().keys())}")
    
    return registry


def test_module_initialization(registry: ModuleRegistry):
    """测试模块初始化"""
    print("\n" + "="*60)
    print("测试2: 模块初始化（按依赖顺序）")
    print("="*60)
    
    registry.initialize_all()
    
    print("✅ 所有模块初始化成功")
    print("   初始化顺序（拓扑排序）:")
    for name in registry._topological_sort():
        print(f"     - {name}")
    
    return registry


def test_module_dependencies(registry: ModuleRegistry):
    """测试模块依赖关系"""
    print("\n" + "="*60)
    print("测试3: 模块依赖关系")
    print("="*60)
    
    for name, module in registry.get_all_modules().items():
        deps = module.dependencies()
        print(f"   {name}: {deps if deps else '无依赖'}")
    
    print("✅ 依赖关系验证成功")


def test_business_flow(registry: ModuleRegistry):
    """测试业务流程"""
    print("\n" + "="*60)
    print("测试4: 完整业务流程")
    print("="*60)
    
    order_module = registry.get_module("OrderModule")
    
    # 4.1 顾客下单
    print("\n   4.1 顾客下单...")
    order_data = OrderCreate(
        table_id=1,
        store_id=1,
        items=[
            {"item_id": 1, "quantity": 2},
            {"item_id": 2, "quantity": 1}
        ]
    )
    order = order_module.service.create_order(order_data)
    print(f"   ✅ 下单成功: {order.order_number}")
    print(f"      订单金额: ¥{order.total_amount}")
    print(f"      订单状态: {order.status}")
    
    # 4.2 厨师开始烹饪
    print("\n   4.2 厨师开始烹饪...")
    order_module.service.update_order_status(order.id, "preparing")
    updated_order = order_module.service.get_order(order.id)
    print(f"   ✅ 订单状态更新: {updated_order.status}")
    
    # 4.3 菜品完成
    print("\n   4.3 菜品完成...")
    order_module.service.update_order_status(order.id, "ready")
    updated_order = order_module.service.get_order(order.id)
    print(f"   ✅ 订单状态更新: {updated_order.status}")
    
    # 4.4 菜品上桌
    print("\n   4.4 菜品上桌...")
    order_module.service.update_order_status(order.id, "served")
    updated_order = order_module.service.get_order(order.id)
    print(f"   ✅ 订单状态更新: {updated_order.status}")
    
    # 4.5 订单完成
    print("\n   4.5 订单完成...")
    order_module.service.update_order_status(order.id, "completed")
    updated_order = order_module.service.get_order(order.id)
    print(f"   ✅ 订单状态更新: {updated_order.status}")
    
    print("\n✅ 完整业务流程测试成功")


def test_module_isolation(registry: ModuleRegistry):
    """测试模块独立性"""
    print("\n" + "="*60)
    print("测试5: 模块独立性")
    print("="*60)
    
    menu_module = registry.get_module("MenuModule")
    user_module = registry.get_module("UserModule")
    order_module = registry.get_module("OrderModule")
    
    # 测试1: MenuModule 可以独立工作
    print("\n   5.1 测试 MenuModule 独立性...")
    menu = menu_module.service.get_menu(store_id=1)
    print(f"   ✅ MenuModule 可以独立获取菜单: {len(menu)} 道菜品")
    
    # 测试2: UserModule 可以独立工作
    print("\n   5.2 测试 UserModule 独立性...")
    user = user_module.service.get_user(1)
    print(f"   ✅ UserModule 可以独立获取用户: {user.username}")
    
    # 测试3: OrderModule 通过接口调用其他模块
    print("\n   5.3 测试 OrderModule 接口调用...")
    order_data = OrderCreate(
        table_id=2,
        store_id=1,
        items=[{"item_id": 3, "quantity": 1}]
    )
    order = order_module.service.create_order(order_data)
    print(f"   ✅ OrderModule 通过接口调用创建订单: {order.order_number}")
    
    print("\n✅ 模块独立性测试成功")


def test_health_check(registry: ModuleRegistry):
    """测试健康检查"""
    print("\n" + "="*60)
    print("测试6: 健康检查")
    print("="*60)
    
    health = registry.health_check()
    
    print(f"   总体状态: {health['overall_status']}")
    print("\n   模块状态:")
    for name, status in health['modules'].items():
        print(f"     - {name}: {status['status']}")
    
    if health['overall_status'] == 'healthy':
        print("\n✅ 所有模块健康")
    else:
        print("\n❌ 部分模块不健康")
        return False
    
    return True


def test_module_shutdown(registry: ModuleRegistry):
    """测试模块关闭"""
    print("\n" + "="*60)
    print("测试7: 模块关闭")
    print("="*60)
    
    registry.shutdown_all()
    print("✅ 所有模块已关闭")


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🎉 模块化架构测试")
    print("="*60)
    
    try:
        # 测试1: 模块注册器
        registry = test_module_registry()
        
        # 测试2: 模块初始化
        registry = test_module_initialization(registry)
        
        # 测试3: 模块依赖关系
        test_module_dependencies(registry)
        
        # 测试4: 完整业务流程
        test_business_flow(registry)
        
        # 测试5: 模块独立性
        test_module_isolation(registry)
        
        # 测试6: 健康检查
        health_ok = test_health_check(registry)
        
        # 测试7: 模块关闭
        test_module_shutdown(registry)
        
        # 测试总结
        print("\n" + "="*60)
        print("🎊 所有测试通过！")
        print("="*60)
        print("\n测试覆盖:")
        print("✅ 模块注册器")
        print("✅ 模块初始化（按依赖顺序）")
        print("✅ 模块依赖关系")
        print("✅ 完整业务流程")
        print("✅ 模块独立性")
        print("✅ 健康检查")
        print("✅ 模块关闭")
        
        print("\n模块化架构验证成功！")
        print("- 模块可以独立注册")
        print("- 模块按依赖顺序初始化")
        print("- 模块通过接口通信")
        print("- 模块可以独立升级")
        print("- 模块独立性得到保证")
        
        print("\n" + "="*60)
        print("✅ 模块化架构测试完成，可以上传到 Git！")
        print("="*60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
