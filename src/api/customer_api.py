"""
顾客端 API 接口
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from storage.database.db import get_session
from storage.database.shared.model import Stores, MenuItems, MenuCategories, Orders, OrderItems, Tables
import random
import string

# 创建 FastAPI 应用
app = FastAPI(title="扫码点餐系统 - 顾客端 API", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 数据模型 ============

class ShopInfo(BaseModel):
    """店铺信息响应"""
    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    opening_hours: Optional[dict] = None


class MenuItemInfo(BaseModel):
    """菜品信息"""
    id: int
    name: str
    description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    image_url: Optional[str] = None
    stock: int
    unit: Optional[str] = None
    cooking_time: Optional[int] = None
    is_available: bool
    is_recommended: bool


class CategoryInfo(BaseModel):
    """分类信息"""
    id: int
    name: str
    description: Optional[str] = None
    sort_order: int
    items: List[MenuItemInfo]


class OrderItemRequest(BaseModel):
    """订单项请求"""
    menu_item_id: int
    quantity: int = Field(..., gt=0)
    special_instructions: Optional[str] = None


class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    store_id: int
    table_id: int
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    items: List[OrderItemRequest]
    special_instructions: Optional[str] = None
    payment_method: Optional[str] = Field(None, description="支付方式：immediate(马上支付) 或 counter(柜台支付)")


class OrderItemResponse(BaseModel):
    """订单项响应"""
    id: int
    menu_item_name: str
    menu_item_price: float
    quantity: int
    subtotal: float
    special_instructions: Optional[str] = None
    status: str


class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    order_number: str
    store_id: int
    table_id: int
    table_number: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    total_amount: float
    discount_amount: float
    final_amount: float
    payment_status: str
    order_status: str
    special_instructions: Optional[str] = None
    created_at: datetime
    items: List[OrderItemResponse]


# ============ 工具函数 ============

def generate_order_number() -> str:
    """生成订单号"""
    now = datetime.now()
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"ORD{now.strftime('%Y%m%d%H%M%S')}{random_str}"


# ============ API 接口 ============

@app.get("/")
def root():
    """根路径"""
    return {
        "message": "扫码点餐系统 - 顾客端 API",
        "version": "1.0.0",
        "endpoints": {
            "GET /api/customer/shop": "获取店铺信息",
            "GET /api/customer/menu": "获取菜品列表",
            "POST /api/customer/order": "创建订单",
            "GET /api/customer/order/{order_id}": "获取订单详情"
        }
    }


@app.get("/api/customer/shop", response_model=ShopInfo)
def get_shop_info(store_id: int = Query(..., description="店铺ID")):
    """
    获取店铺信息
    """
    db = get_session()
    try:
        shop = db.query(Stores).filter(Stores.id == store_id, Stores.is_active == True).first()
        if not shop:
            raise HTTPException(status_code=404, detail="店铺不存在或已关闭")
        
        return ShopInfo(
            id=shop.id,
            name=shop.name,
            address=shop.address,
            phone=shop.phone,
            opening_hours=shop.opening_hours
        )
    finally:
        db.close()


@app.get("/api/customer/menu", response_model=List[CategoryInfo])
def get_menu(store_id: int = Query(..., description="店铺ID")):
    """
    获取菜品列表（按分类分组）
    """
    db = get_session()
    try:
        # 查询店铺的所有分类
        categories = db.query(MenuCategories).filter(
            MenuCategories.store_id == store_id,
            MenuCategories.is_active == True
        ).order_by(MenuCategories.sort_order).all()
        
        result = []
        for category in categories:
            # 查询该分类下的菜品
            items = db.query(MenuItems).filter(
                MenuItems.category_id == category.id,
                MenuItems.is_available == True
            ).order_by(MenuItems.sort_order, MenuItems.id).all()
            
            menu_items = []
            for item in items:
                menu_items.append(MenuItemInfo(
                    id=item.id,
                    name=item.name,
                    description=item.description,
                    price=item.price,
                    original_price=item.original_price,
                    image_url=item.image_url,
                    stock=item.stock,
                    unit=item.unit,
                    cooking_time=item.cooking_time,
                    is_available=item.is_available,
                    is_recommended=item.is_recommended
                ))
            
            result.append(CategoryInfo(
                id=category.id,
                name=category.name,
                description=category.description,
                sort_order=category.sort_order,
                items=menu_items
            ))
        
        return result
    finally:
        db.close()


@app.post("/api/customer/order", response_model=OrderResponse)
def create_order(request: CreateOrderRequest):
    """
    创建订单
    """
    db = get_session()
    try:
        # 验证店铺和桌号
        shop = db.query(Stores).filter(Stores.id == request.store_id).first()
        if not shop:
            raise HTTPException(status_code=404, detail="店铺不存在")
        
        table = db.query(Tables).filter(
            Tables.id == request.table_id,
            Tables.store_id == request.store_id
        ).first()
        if not table:
            raise HTTPException(status_code=404, detail="桌号不存在或不属于该店铺")
        
        # 生成订单号
        order_number = generate_order_number()

        # 确定支付状态：如果选择"马上支付"则标记为已支付，"柜台支付"则标记为未支付
        if request.payment_method == 'immediate':
            payment_status = 'paid'
            payment_time = datetime.now()
        else:
            payment_status = 'unpaid'
            payment_time = None

        # 计算订单金额
        total_amount = 0.0
        discount_amount = 0.0

        # 创建订单
        order = Orders(
            store_id=request.store_id,
            table_id=request.table_id,
            order_number=order_number,
            customer_name=request.customer_name,
            customer_phone=request.customer_phone,
            total_amount=0.0,  # 后面更新
            discount_amount=0.0,
            final_amount=0.0,  # 后面更新
            payment_status=payment_status,
            payment_method=request.payment_method,
            payment_time=payment_time,
            order_status="pending",
            special_instructions=request.special_instructions
        )
        db.add(order)
        db.flush()
        
        # 创建订单项
        order_items = []
        for item_request in request.items:
            # 获取菜品信息（快照）
            menu_item = db.query(MenuItems).filter(MenuItems.id == item_request.menu_item_id).first()
            if not menu_item:
                raise HTTPException(status_code=404, detail=f"菜品ID {item_request.menu_item_id} 不存在")
            
            if menu_item.stock < item_request.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"菜品 {menu_item.name} 库存不足，当前库存: {menu_item.stock}，需要: {item_request.quantity}"
                )
            
            subtotal = menu_item.price * item_request.quantity
            total_amount += subtotal
            
            order_item = OrderItems(
                order_id=order.id,
                menu_item_id=menu_item.id,
                menu_item_name=menu_item.name,
                menu_item_price=menu_item.price,
                quantity=item_request.quantity,
                subtotal=subtotal,
                special_instructions=item_request.special_instructions,
                status="pending"
            )
            db.add(order_item)
            order_items.append(order_item)
        
        # 更新订单金额
        order.total_amount = total_amount
        order.discount_amount = discount_amount
        order.final_amount = total_amount - discount_amount
        
        # 提交事务
        db.commit()
        db.refresh(order)
        
        # 构建响应
        response_items = []
        for oi in order_items:
            response_items.append(OrderItemResponse(
                id=oi.id,
                menu_item_name=oi.menu_item_name,
                menu_item_price=oi.menu_item_price,
                quantity=oi.quantity,
                subtotal=oi.subtotal,
                special_instructions=oi.special_instructions,
                status=oi.status
            ))
        
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            store_id=order.store_id,
            table_id=order.table_id,
            table_number=table.table_number,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            total_amount=order.total_amount,
            discount_amount=order.discount_amount,
            final_amount=order.final_amount,
            payment_status=order.payment_status,
            order_status=order.order_status,
            special_instructions=order.special_instructions,
            created_at=order.created_at,
            items=response_items
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建订单失败: {str(e)}")
    finally:
        db.close()


@app.get("/api/customer/order/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    """
    获取订单详情
    """
    db = get_session()
    try:
        order = db.query(Orders).filter(Orders.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        # 获取桌号信息
        table = db.query(Tables).filter(Tables.id == order.table_id).first()
        table_number = table.table_number if table else ""
        
        # 构建订单项
        response_items = []
        for oi in order.order_items:
            response_items.append(OrderItemResponse(
                id=oi.id,
                menu_item_name=oi.menu_item_name,
                menu_item_price=oi.menu_item_price,
                quantity=oi.quantity,
                subtotal=oi.subtotal,
                special_instructions=oi.special_instructions,
                status=oi.status
            ))
        
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            store_id=order.store_id,
            table_id=order.table_id,
            table_number=table_number,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            total_amount=order.total_amount,
            discount_amount=order.discount_amount,
            final_amount=order.final_amount,
            payment_status=order.payment_status,
            order_status=order.order_status,
            special_instructions=order.special_instructions,
            created_at=order.created_at,
            items=response_items
        )
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
