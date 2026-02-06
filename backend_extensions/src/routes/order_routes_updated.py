from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload
from storage.database.db_config import get_db
from storage.database.models import Order, OrderItem, MenuItem, Table, Store
from typing import Optional, List
from datetime import datetime
from routes.auth_routes import get_current_active_user
from routes.websocket_routes import notify_order_update, notify_new_order
import random
import string

router = APIRouter(prefix="/api/orders", tags=["订单管理"])

def generate_order_number():
    return "ORD" + datetime.now().strftime("%Y%m%d%H%M%S") + ''.join(random.choices(string.digits, k=4))

class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int
    special_instructions: Optional[str] = None

class OrderCreate(BaseModel):
    table_id: int
    store_id: int
    items: List[OrderItemCreate]
    special_requirements: Optional[str] = None
    user_id: Optional[int] = None

class OrderResponse(BaseModel):
    id: int
    order_number: str
    store_id: int
    table_id: int
    total_amount: float
    status: str
    payment_status: str
    special_requirements: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    price: float
    subtotal: float
    special_instructions: Optional[str]
    
    class Config:
        from_attributes = True

class OrderDetailResponse(BaseModel):
    id: int
    order_number: str
    store_id: int
    table_id: int
    total_amount: float
    status: str
    payment_status: str
    special_requirements: Optional[str]
    created_at: datetime
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[OrderResponse])
def get_orders(
    store_id: Optional[int] = None,
    table_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Order)
    if store_id:
        query = query.filter(Order.store_id == store_id)
    if table_id:
        query = query.filter(Order.table_id == table_id)
    if status:
        query = query.filter(Order.status == status)
    orders = query.order_by(Order.created_at.desc()).all()
    return [
        OrderResponse(
            id=o.id, order_number=o.order_number, store_id=o.store_id,
            table_id=o.table_id, total_amount=o.total_amount, status=o.status,
            payment_status=o.payment_status, special_requirements=o.special_requirements,
            created_at=o.created_at
        ) for o in orders
    ]

@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).options(selectinload(Order.order_items)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    items = [
        OrderItemResponse(
            id=item.id, menu_item_id=item.menu_item_id, quantity=item.quantity,
            price=item.price, subtotal=item.subtotal, special_instructions=item.special_instructions
        ) for item in order.order_items
    ]
    
    return OrderDetailResponse(
        id=order.id, order_number=order.order_number, store_id=order.store_id,
        table_id=order.table_id, total_amount=order.total_amount, status=order.status,
        payment_status=order.payment_status, special_requirements=order.special_requirements,
        created_at=order.created_at, items=items
    )

@router.post("/", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    table = db.query(Table).filter(Table.id == order_data.table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="桌台不存在")
    
    store = db.query(Store).filter(Store.id == order_data.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    order_number = generate_order_number()
    total_amount = 0.0
    
    new_order = Order(
        order_number=order_number,
        store_id=order_data.store_id,
        table_id=order_data.table_id,
        user_id=order_data.user_id,
        special_requirements=order_data.special_requirements,
        status="pending",
        payment_status="unpaid"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # 扣减库存
    for item_data in order_data.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.menu_item_id).first()
        if not menu_item:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"菜品 {item_data.menu_item_id} 不存在")
        
        if menu_item.stock < item_data.quantity:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"菜品 {menu_item.name} 库存不足")
        
        # 扣减库存
        menu_item.stock -= item_data.quantity
        
        subtotal = menu_item.price * item_data.quantity
        total_amount += subtotal
        
        order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=item_data.menu_item_id,
            quantity=item_data.quantity,
            price=menu_item.price,
            subtotal=subtotal,
            special_instructions=item_data.special_instructions
        )
        db.add(order_item)
    
    new_order.total_amount = total_amount
    db.commit()
    db.refresh(new_order)
    
    # WebSocket 通知新订单（异步执行）
    import asyncio
    asyncio.create_task(notify_new_order(
        order_data.store_id,
        {
            "id": new_order.id,
            "order_number": new_order.order_number,
            "table_id": new_order.table_id,
            "total_amount": new_order.total_amount,
            "status": new_order.status
        },
        order_data.table_id
    ))
    
    return OrderResponse(
        id=new_order.id, order_number=new_order.order_number, store_id=new_order.store_id,
        table_id=new_order.table_id, total_amount=new_order.total_amount, status=new_order.status,
        payment_status=new_order.payment_status, special_requirements=new_order.special_requirements,
        created_at=new_order.created_at
    )

@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'serving', 'completed', 'cancelled']
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"无效的状态，必须是: {', '.join(valid_statuses)}")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    old_status = order.status
    order.status = status
    
    if status == "completed":
        order.completed_at = datetime.now()
    elif status == "cancelled" and old_status != "cancelled":
        # 取消订单时恢复库存
        for item in order.order_items:
            menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
            if menu_item:
                menu_item.stock += item.quantity
    
    db.commit()
    
    # WebSocket 通知订单状态更新（异步执行）
    import asyncio
    asyncio.create_task(notify_order_update(order.store_id, order_id, status))
    
    return {"message": "状态更新成功", "status": status, "old_status": old_status}

@router.put("/{order_id}/payment")
def update_payment_status(
    order_id: int,
    payment_status: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    valid_statuses = ['unpaid', 'paid', 'refunded']
    if payment_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"无效的支付状态，必须是: {', '.join(valid_statuses)}")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    old_status = order.payment_status
    order.payment_status = payment_status
    
    # 如果支付完成，给用户添加积分（1元 = 1积分）
    if payment_status == "paid" and old_status != "paid":
        if order.user_id:
            user = db.query(Order.__table__.c.user_id).filter(Order.id == order_id).scalar()
            # TODO: 更新用户积分
    
    db.commit()
    return {"message": "支付状态更新成功", "payment_status": payment_status}
