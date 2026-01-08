"""
餐饮系统完整 API 服务
整合顾客端、管理端、厨房端、传菜端等所有接口
"""
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import random
import string

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from storage.database.db import get_session
from storage.database.shared.model import (
    Companies, Users, Stores, MenuCategories, MenuItems,
    Tables, Orders, OrderItems, MemberLevelRules
)

# 创建 FastAPI 应用
app = FastAPI(title="多店铺扫码点餐系统 - 完整API", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 数据模型 ============

class MenuItemInfo(BaseModel):
    """菜品信息"""
    id: int
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    stock: int
    is_available: bool
    is_recommended: bool
    category_id: int
    category_name: Optional[str] = None
    sort_order: Optional[int] = 0

class CategoryInfo(BaseModel):
    """分类信息"""
    id: int
    name: str
    description: Optional[str] = None
    sort_order: int

class TableInfo(BaseModel):
    """桌号信息"""
    id: int
    table_number: str
    seats: int
    is_active: bool
    is_occupied: bool = False

class OrderItemRequest(BaseModel):
    """订单项请求"""
    menu_item_id: int
    quantity: int = Field(..., gt=0)
    special_instructions: Optional[str] = None

class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    table_id: int
    items: List[OrderItemRequest]
    payment_method: str = "wechat"

class OrderItemResponse(BaseModel):
    """订单项响应"""
    id: int
    menu_item_id: int
    menu_item_name: str
    price: float
    quantity: int
    subtotal: float
    special_instructions: Optional[str] = None
    item_status: str  # API中保持使用item_status，但映射到数据库的status字段

class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    store_id: int
    table_id: int
    table_number: str
    total_amount: float
    payment_method: str
    status: str
    created_at: str
    items: List[OrderItemResponse]

class MenuItemCreate(BaseModel):
    """创建菜品请求"""
    name: str
    category_id: int
    price: float
    stock: int = 100
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_recommended: bool = False
    is_available: bool = True

class MenuItemUpdate(BaseModel):
    """更新菜品请求"""
    name: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_recommended: Optional[bool] = None
    is_available: Optional[bool] = None

class TableCreate(BaseModel):
    """创建桌号请求"""
    table_number: str
    seats: int = 4
    is_active: bool = True

class TableUpdate(BaseModel):
    """更新桌号请求"""
    table_number: Optional[str] = None
    seats: Optional[int] = None
    is_active: Optional[bool] = None

class UpdateOrderStatusRequest(BaseModel):
    """更新订单状态请求"""
    status: str

class UpdateItemStatusRequest(BaseModel):
    """更新菜品状态请求"""
    item_status: str


# ============ 辅助函数 ============

def generate_order_number():
    """生成订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"ORD{timestamp}{random_str}"


# ============ 店铺和基础信息 ============

@app.get("/api/store")
def get_store_info():
    """获取店铺信息（默认返回第一个店铺）"""
    db = get_session()
    try:
        store = db.query(Stores).filter(Stores.is_active == True).first()
        if not store:
            raise HTTPException(status_code=404, detail="未找到店铺")
        
        return {
            "id": store.id,
            "name": store.name,
            "address": store.address,
            "phone": store.phone,
            "opening_hours": store.opening_hours
        }
    finally:
        db.close()


# ============ 菜品分类 ============

@app.get("/api/menu-categories/", response_model=List[CategoryInfo])
def get_menu_categories(store_id: Optional[int] = None):
    """获取菜品分类列表"""
    db = get_session()
    try:
        query = db.query(MenuCategories)
        if store_id:
            query = query.filter(MenuCategories.store_id == store_id)
        else:
            # 如果没有指定store_id，获取第一个店铺的分类
            first_store = db.query(Stores).first()
            if first_store:
                query = query.filter(MenuCategories.store_id == first_store.id)
        
        categories = query.order_by(MenuCategories.sort_order).all()
        return [
            CategoryInfo(
                id=cat.id,
                name=cat.name,
                description=cat.description,
                sort_order=cat.sort_order or 0
            )
            for cat in categories
        ]
    finally:
        db.close()


# ============ 菜品管理 ============

@app.get("/api/menu-items/", response_model=List[MenuItemInfo])
def get_menu_items(
    category_id: Optional[int] = None,
    store_id: Optional[int] = None
):
    """获取菜品列表"""
    db = get_session()
    try:
        query = db.query(MenuItems)
        
        if store_id:
            query = query.filter(MenuItems.store_id == store_id)
        else:
            # 如果没有指定store_id，获取第一个店铺的菜品
            first_store = db.query(Stores).first()
            if first_store:
                query = query.filter(MenuItems.store_id == first_store.id)
        
        if category_id:
            query = query.filter(MenuItems.category_id == category_id)
        
        items = query.order_by(MenuItems.sort_order).all()
        
        return [
            MenuItemInfo(
                id=item.id,
                name=item.name,
                description=item.description,
                price=float(item.price),
                image_url=item.image_url,
                stock=item.stock,
                is_available=item.is_available,
                is_recommended=item.is_recommended,
                category_id=item.category_id,
                category_name=item.category.name if item.category else None,
                sort_order=item.sort_order or 0
            )
            for item in items
        ]
    finally:
        db.close()


@app.post("/api/menu-items/", response_model=MenuItemInfo)
def create_menu_item(item: MenuItemCreate):
    """创建菜品"""
    db = get_session()
    try:
        # 获取店铺ID
        first_store = db.query(Stores).first()
        if not first_store:
            raise HTTPException(status_code=404, detail="未找到店铺")
        
        # 获取最大sort_order
        max_sort = db.query(MenuItems).filter(
            MenuItems.store_id == first_store.id
        ).count()
        
        db_item = MenuItems(
            store_id=first_store.id,
            category_id=item.category_id,
            name=item.name,
            description=item.description,
            price=item.price,
            image_url=item.image_url,
            stock=item.stock,
            is_available=item.is_available,
            is_recommended=item.is_recommended,
            sort_order=max_sort + 1
        )
        
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        return MenuItemInfo(
            id=db_item.id,
            name=db_item.name,
            description=db_item.description,
            price=float(db_item.price),
            image_url=db_item.image_url,
            stock=db_item.stock,
            is_available=db_item.is_available,
            is_recommended=db_item.is_recommended,
            category_id=db_item.category_id,
            category_name=db_item.category.name if db_item.category else None,
            sort_order=db_item.sort_order or 0
        )
    finally:
        db.close()


@app.patch("/api/menu-items/{item_id}", response_model=MenuItemInfo)
def update_menu_item(item_id: int, item: MenuItemUpdate):
    """更新菜品"""
    db = get_session()
    try:
        db_item = db.query(MenuItems).filter(MenuItems.id == item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="菜品不存在")
        
        update_data = item.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        
        db.commit()
        db.refresh(db_item)
        
        return MenuItemInfo(
            id=db_item.id,
            name=db_item.name,
            description=db_item.description,
            price=float(db_item.price),
            image_url=db_item.image_url,
            stock=db_item.stock,
            is_available=db_item.is_available,
            is_recommended=db_item.is_recommended,
            category_id=db_item.category_id,
            category_name=db_item.category.name if db_item.category else None,
            sort_order=db_item.sort_order or 0
        )
    finally:
        db.close()


@app.delete("/api/menu-items/{item_id}")
def delete_menu_item(item_id: int):
    """删除菜品"""
    db = get_session()
    try:
        db_item = db.query(MenuItems).filter(MenuItems.id == item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="菜品不存在")
        
        db.delete(db_item)
        db.commit()
        return {"message": "菜品删除成功"}
    finally:
        db.close()


# ============ 桌号管理 ============

@app.get("/api/tables/", response_model=List[TableInfo])
def get_tables(store_id: Optional[int] = None):
    """获取桌号列表"""
    db = get_session()
    try:
        query = db.query(Tables)
        
        if store_id:
            query = query.filter(Tables.store_id == store_id)
        else:
            # 如果没有指定store_id，获取第一个店铺的桌号
            first_store = db.query(Stores).first()
            if first_store:
                query = query.filter(Tables.store_id == first_store.id)
        
        tables = query.order_by(Tables.table_number).all()
        
        # 检查是否有正在进行的订单
        result = []
        for table in tables:
            active_order = db.query(Orders).filter(
                Orders.table_id == table.id,
                Orders.order_status.in_(['pending', 'confirmed', 'preparing', 'ready', 'serving'])
            ).first()
            
            result.append(TableInfo(
                id=table.id,
                table_number=table.table_number,
                seats=table.seats,
                is_active=table.is_active,
                is_occupied=bool(active_order)
            ))
        
        return result
    finally:
        db.close()


@app.post("/api/tables/", response_model=TableInfo)
def create_table(table: TableCreate):
    """创建桌号"""
    db = get_session()
    try:
        first_store = db.query(Stores).first()
        if not first_store:
            raise HTTPException(status_code=404, detail="未找到店铺")
        
        db_table = Tables(
            store_id=first_store.id,
            table_number=table.table_number,
            seats=table.seats,
            is_active=table.is_active
        )
        
        db.add(db_table)
        db.commit()
        db.refresh(db_table)
        
        return TableInfo(
            id=db_table.id,
            table_number=db_table.table_number,
            seats=db_table.seats,
            is_active=db_table.is_active,
            is_occupied=False
        )
    finally:
        db.close()


@app.patch("/api/tables/{table_id}", response_model=TableInfo)
def update_table(table_id: int, table: TableUpdate):
    """更新桌号"""
    db = get_session()
    try:
        db_table = db.query(Tables).filter(Tables.id == table_id).first()
        if not db_table:
            raise HTTPException(status_code=404, detail="桌号不存在")
        
        update_data = table.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_table, key, value)
        
        db.commit()
        db.refresh(db_table)
        
        return TableInfo(
            id=db_table.id,
            table_number=db_table.table_number,
            seats=db_table.seats,
            is_active=db_table.is_active,
            is_occupied=False
        )
    finally:
        db.close()


@app.delete("/api/tables/{table_id}")
def delete_table(table_id: int):
    """删除桌号"""
    db = get_session()
    try:
        db_table = db.query(Tables).filter(Tables.id == table_id).first()
        if not db_table:
            raise HTTPException(status_code=404, detail="桌号不存在")
        
        db.delete(db_table)
        db.commit()
        return {"message": "桌号删除成功"}
    finally:
        db.close()


@app.post("/api/tables/generate-qr")
def generate_qrcode(data: Dict[str, int]):
    """生成桌号二维码（模拟）"""
    table_id = data.get("table_id")
    if not table_id:
        raise HTTPException(status_code=400, detail="缺少table_id参数")
    
    db = get_session()
    try:
        table = db.query(Tables).filter(Tables.id == table_id).first()
        if not table:
            raise HTTPException(status_code=404, detail="桌号不存在")
        
        # 生成模拟二维码URL
        qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=table_{table.id}"
        
        return {
            "table_id": table.id,
            "table_number": table.table_number,
            "qr_code_url": qr_code_url
        }
    finally:
        db.close()


# ============ 订单管理 ============

@app.get("/api/orders/", response_model=List[OrderResponse])
def get_orders(
    status: Optional[str] = None,
    table_id: Optional[int] = None,
    store_id: Optional[int] = None
):
    """获取订单列表"""
    db = get_session()
    try:
        query = db.query(Orders)
        
        if store_id:
            query = query.filter(Orders.store_id == store_id)
        else:
            first_store = db.query(Stores).first()
            if first_store:
                query = query.filter(Orders.store_id == first_store.id)
        
        if status:
            query = query.filter(Orders.order_status == status)
        
        if table_id:
            query = query.filter(Orders.table_id == table_id)
        
        orders = query.order_by(Orders.created_at.desc()).all()
        
        result = []
        for order in orders:
            # 获取桌号
            table = db.query(Tables).filter(Tables.id == order.table_id).first()
            table_number = table.table_number if table else ""
            
            # 构建订单项
            order_items = []
            for oi in order.order_items:
                order_items.append(OrderItemResponse(
                    id=oi.id,
                    menu_item_id=oi.menu_item_id,
                    menu_item_name=oi.menu_item_name,
                    price=float(oi.menu_item_price),
                    quantity=oi.quantity,
                    subtotal=float(oi.subtotal),
                    special_instructions=oi.special_instructions,
                    item_status=oi.item_status or order.order_status
                ))
            
            result.append(OrderResponse(
                id=order.id,
                store_id=order.store_id,
                table_id=order.table_id,
                table_number=table_number,
                total_amount=float(order.total_amount),
                payment_method=order.payment_method,
                status=order.order_status,
                created_at=order.created_at.isoformat() if order.created_at else "",
                items=order_items
            ))
        
        return result
    finally:
        db.close()


@app.post("/api/orders/", response_model=OrderResponse)
def create_order(order: CreateOrderRequest):
    """创建订单"""
    db = get_session()
    try:
        first_store = db.query(Stores).first()
        if not first_store:
            raise HTTPException(status_code=404, detail="未找到店铺")
        
        table = db.query(Tables).filter(Tables.id == order.table_id).first()
        if not table:
            raise HTTPException(status_code=404, detail="桌号不存在")
        
        # 计算总金额
        total_amount = 0
        order_items_data = []
        
        for item_req in order.items:
            menu_item = db.query(MenuItems).filter(MenuItems.id == item_req.menu_item_id).first()
            if not menu_item:
                raise HTTPException(status_code=404, detail=f"菜品ID {item_req.menu_item_id} 不存在")
            
            if not menu_item.is_available:
                raise HTTPException(status_code=400, detail=f"菜品 {menu_item.name} 已下架")
            
            if menu_item.stock < item_req.quantity:
                raise HTTPException(status_code=400, detail=f"菜品 {menu_item.name} 库存不足")
            
            subtotal = float(menu_item.price) * item_req.quantity
            total_amount += subtotal
            
            order_items_data.append({
                "menu_item_id": menu_item.id,
                "menu_item_name": menu_item.name,
                "menu_item_price": float(menu_item.price),
                "quantity": item_req.quantity,
                "subtotal": subtotal,
                "special_instructions": item_req.special_instructions
            })
        
        # 创建订单
        db_order = Orders(
            order_number=generate_order_number(),
            store_id=first_store.id,
            table_id=order.table_id,
            total_amount=total_amount,
            discount_amount=0,
            final_amount=total_amount,
            payment_method=order.payment_method,
            payment_status="paid",
            order_status="pending"
        )
        
        db.add(db_order)
        db.flush()
        
        # 创建订单项
        for item_data in order_items_data:
            order_item = OrderItems(
                order_id=db_order.id,
                status="pending",
                **item_data
            )
            db.add(order_item)
        
        # 更新菜品库存
        for item_req in order.items:
            menu_item = db.query(MenuItems).filter(MenuItems.id == item_req.menu_item_id).first()
            menu_item.stock -= item_req.quantity
        
        db.commit()
        db.refresh(db_order)
        
        # 获取桌号
        table_number = table.table_number
        
        # 构建订单项
        order_items = []
        for oi in db_order.order_items:
            order_items.append(OrderItemResponse(
                id=oi.id,
                menu_item_id=oi.menu_item_id,
                menu_item_name=oi.menu_item_name,
                price=float(oi.menu_item_price),
                quantity=oi.quantity,
                subtotal=float(oi.subtotal),
                special_instructions=oi.special_instructions,
                item_status=oi.status
            ))
        
        return OrderResponse(
            id=db_order.id,
            store_id=db_order.store_id,
            table_id=db_order.table_id,
            table_number=table_number,
            total_amount=float(db_order.total_amount),
            payment_method=db_order.payment_method,
            status=db_order.order_status,
            created_at=db_order.created_at.isoformat(),
            items=order_items
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建订单失败: {str(e)}")
    finally:
        db.close()


@app.get("/api/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    """获取订单详情"""
    db = get_session()
    try:
        order = db.query(Orders).filter(Orders.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        # 获取桌号
        table = db.query(Tables).filter(Tables.id == order.table_id).first()
        table_number = table.table_number if table else ""
        
        # 构建订单项
        order_items = []
        for oi in order.order_items:
            order_items.append(OrderItemResponse(
                id=oi.id,
                menu_item_id=oi.menu_item_id,
                menu_item_name=oi.menu_item_name,
                price=float(oi.menu_item_price),
                quantity=oi.quantity,
                subtotal=float(oi.subtotal),
                special_instructions=oi.special_instructions,
                item_status=oi.status
            ))
        
        return OrderResponse(
            id=order.id,
            store_id=order.store_id,
            table_id=order.table_id,
            table_number=table_number,
            total_amount=float(order.total_amount),
            payment_method=order.payment_method,
            status=order.order_status,
            created_at=order.created_at.isoformat() if order.created_at else "",
            items=order_items
        )
    finally:
        db.close()


@app.patch("/api/orders/{order_id}/status")
def update_order_status(order_id: int, req: UpdateOrderStatusRequest):
    """更新订单状态"""
    db = get_session()
    try:
        order = db.query(Orders).filter(Orders.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        # 验证状态流转是否合法
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['preparing', 'cancelled'],
            'preparing': ['ready'],
            'ready': ['serving'],
            'serving': ['completed'],
            'completed': [],
            'cancelled': []
        }
        
        current_status = order.order_status
        new_status = req.status
        
        if new_status not in valid_transitions.get(current_status, []):
            raise HTTPException(
                status_code=400, 
                detail=f"不能从状态 {current_status} 转换到 {new_status}"
            )
        
        order.order_status = new_status
        db.commit()
        
        return {"message": "订单状态更新成功", "status": new_status}
    finally:
        db.close()


@app.patch("/api/orders/{order_id}/items/{item_id}/status")
def update_order_item_status(order_id: int, item_id: int, req: UpdateItemStatusRequest):
    """更新订单项状态"""
    db = get_session()
    try:
        order_item = db.query(OrderItems).filter(
            OrderItems.id == item_id,
            OrderItems.order_id == order_id
        ).first()
        
        if not order_item:
            raise HTTPException(status_code=404, detail="订单项不存在")
        
        # 验证状态流转是否合法
        valid_transitions = {
            'pending': ['preparing'],
            'preparing': ['ready'],
            'ready': ['served'],
            'served': []
        }
        
        current_status = order_item.status or 'pending'
        new_status = req.item_status
        
        if new_status not in valid_transitions.get(current_status, []):
            raise HTTPException(
                status_code=400, 
                detail=f"不能从状态 {current_status} 转换到 {new_status}"
            )
        
        order_item.status = new_status
        db.commit()
        
        return {"message": "菜品状态更新成功", "item_status": new_status}
    finally:
        db.close()


from src.api.workflow_api import router as workflow_router
from src.api.order_flow_api import router as order_flow_router

# 注册工作流程配置路由
app.include_router(workflow_router)

# 注册订单流程配置路由
app.include_router(order_flow_router)


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok", "message": "餐饮系统API服务运行正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
