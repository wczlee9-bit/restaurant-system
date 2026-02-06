"""
模块化架构 - 服务接口定义
定义各个模块的服务接口，确保模块间通过接口通信
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


# ==================== 数据模型 ====================

class OrderItem(BaseModel):
    """订单项"""
    item_id: int
    quantity: int
    special_instructions: Optional[str] = None


class OrderCreate(BaseModel):
    """创建订单请求"""
    table_id: int
    store_id: int
    items: List[OrderItem]
    user_id: Optional[int] = None
    special_requirements: Optional[str] = None


class Order(BaseModel):
    """订单"""
    id: int
    order_number: str
    store_id: int
    table_id: int
    total_amount: float
    status: str
    payment_status: str
    created_at: datetime


class MenuItem(BaseModel):
    """菜单项"""
    id: int
    name: str
    price: float
    stock: int
    category: Optional[str] = None
    description: Optional[str] = None


class User(BaseModel):
    """用户"""
    id: int
    username: str
    role: str
    points: Optional[int] = 0


# ==================== 服务接口 ====================

class IMenuService(ABC):
    """菜单服务接口"""
    
    @abstractmethod
    def get_menu(self, store_id: int) -> List[MenuItem]:
        """获取菜单列表"""
        pass
    
    @abstractmethod
    def get_item(self, item_id: int) -> Optional[MenuItem]:
        """获取单个菜品"""
        pass
    
    @abstractmethod
    def update_stock(self, item_id: int, quantity: int) -> bool:
        """更新库存"""
        pass


class IUserService(ABC):
    """用户服务接口"""
    
    @abstractmethod
    def get_user(self, user_id: int) -> Optional[User]:
        """获取用户信息"""
        pass
    
    @abstractmethod
    def add_points(self, user_id: int, points: int) -> bool:
        """添加积分"""
        pass
    
    @abstractmethod
    def deduct_points(self, user_id: int, points: int) -> bool:
        """扣除积分"""
        pass


class IOrderService(ABC):
    """订单服务接口"""
    
    @abstractmethod
    def create_order(self, order_data: OrderCreate) -> Order:
        """创建订单"""
        pass
    
    @abstractmethod
    def get_order(self, order_id: int) -> Optional[Order]:
        """获取订单"""
        pass
    
    @abstractmethod
    def update_order_status(self, order_id: int, status: str) -> bool:
        """更新订单状态"""
        pass
    
    @abstractmethod
    def get_orders_by_status(self, status: str) -> List[Order]:
        """根据状态获取订单列表"""
        pass


class IStockService(ABC):
    """库存服务接口"""
    
    @abstractmethod
    def get_stock(self, item_id: int) -> int:
        """获取库存"""
        pass
    
    @abstractmethod
    def deduct_stock(self, item_id: int, quantity: int) -> bool:
        """扣减库存"""
        pass
    
    @abstractmethod
    def restock(self, item_id: int, quantity: int) -> bool:
        """补货"""
        pass
    
    @abstractmethod
    def get_low_stock_items(self, threshold: int) -> List[MenuItem]:
        """获取低库存商品"""
        pass


class IMemberService(ABC):
    """会员服务接口"""
    
    @abstractmethod
    def get_member_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取会员信息"""
        pass
    
    @abstractmethod
    def add_member_points(self, user_id: int, points: int) -> bool:
        """添加会员积分"""
        pass
    
    @abstractmethod
    def get_member_rankings(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取会员排行榜"""
        pass


class IStatsService(ABC):
    """统计服务接口"""
    
    @abstractmethod
    def get_daily_stats(self, date: datetime) -> Dict[str, Any]:
        """获取每日统计"""
        pass
    
    @abstractmethod
    def get_revenue_trend(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取营收趋势"""
        pass
    
    @abstractmethod
    def get_top_items(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热销商品"""
        pass


class IReceiptService(ABC):
    """小票服务接口"""
    
    @abstractmethod
    def generate_receipt(self, order_id: int, receipt_type: str) -> str:
        """生成小票"""
        pass
    
    @abstractmethod
    def print_receipt(self, order_id: int) -> bool:
        """打印小票"""
        pass


class IWebSocketService(ABC):
    """WebSocket 服务接口"""
    
    @abstractmethod
    def broadcast_order_update(self, store_id: int, order: Dict[str, Any]):
        """广播订单更新"""
        pass
    
    @abstractmethod
    def broadcast_new_order(self, store_id: int, table_id: int, order: Dict[str, Any]):
        """广播新订单"""
        pass
