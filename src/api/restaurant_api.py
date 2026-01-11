"""
餐饮系统完整 API 服务
整合顾客端、管理端、厨房端、传菜端等所有接口
"""
from fastapi import FastAPI, HTTPException, Query, Body, Form, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import random
import string
import json
import logging

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from storage.database.db import get_session
from storage.database.shared.model import (
    Companies, Users, Stores, MenuCategories, MenuItems,
    Tables, Orders, OrderItems, MemberLevelRules
)

logger = logging.getLogger(__name__)

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

# 包含诊断路由
try:
    from diagnostic import router as diagnostic_router
    app.include_router(diagnostic_router)
    logger.info("✓ Diagnostic routes included")
except ImportError as e:
    logger.warning(f"Could not include diagnostic routes: {e}")


# ============ 应用启动事件 ============

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    logger.info("=" * 60)
    logger.info("Starting Restaurant API...")
    logger.info("=" * 60)

    # 初始化数据库表结构
    from storage.database.init_db import init_database, ensure_test_data

    if init_database():
        logger.info("✓ Database schema initialized")
    else:
        logger.warning("⚠ Failed to initialize database schema")

    # 初始化测试数据
    if ensure_test_data():
        logger.info("✓ Test data ensured")
    else:
        logger.warning("⚠ Failed to ensure test data")

    logger.info("=" * 60)
    logger.info("Restaurant API started successfully!")
    logger.info("=" * 60)


# ============ WebSocket 连接管理 ============

class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # store_id -> {connection_id: WebSocket}
        self.store_connections: Dict[int, Dict[str, WebSocket]] = {}
        # order_id -> {connection_id: WebSocket} 顾客订阅订单
        self.order_connections: Dict[int, Dict[str, WebSocket]] = {}
        # table_id -> {connection_id: WebSocket} 桌号连接（顾客端）
        self.table_connections: Dict[int, Dict[str, WebSocket]] = {}
    
    async def connect_to_store(self, websocket: WebSocket, store_id: int, connection_id: str):
        """连接到店铺（用于店员端）"""
        await websocket.accept()
        if store_id not in self.store_connections:
            self.store_connections[store_id] = {}
        self.store_connections[store_id][connection_id] = websocket
        logger.info(f"WebSocket连接到店铺: store_id={store_id}, connection_id={connection_id}")
        
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "message": "连接成功",
            "store_id": store_id,
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat()
        })
    
    async def connect_to_order(self, websocket: WebSocket, order_id: int, connection_id: str):
        """连接到订单（用于顾客端）"""
        await websocket.accept()
        if order_id not in self.order_connections:
            self.order_connections[order_id] = {}
        self.order_connections[order_id][connection_id] = websocket
        logger.info(f"WebSocket连接到订单: order_id={order_id}, connection_id={connection_id}")
        
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "message": "连接成功",
            "order_id": order_id,
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat()
        })
    
    async def connect_to_table(self, websocket: WebSocket, table_id: int, connection_id: str):
        """连接到桌号（用于顾客端）"""
        await websocket.accept()
        if table_id not in self.table_connections:
            self.table_connections[table_id] = {}
        self.table_connections[table_id][connection_id] = websocket
        logger.info(f"WebSocket连接到桌号: table_id={table_id}, connection_id={connection_id}")
        
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "message": "连接成功",
            "table_id": table_id,
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect(self, store_id: int = None, order_id: int = None, table_id: int = None, connection_id: str = None):
        """断开连接"""
        if store_id and store_id in self.store_connections:
            if connection_id and connection_id in self.store_connections[store_id]:
                del self.store_connections[store_id][connection_id]
                logger.info(f"断开店铺连接: store_id={store_id}, connection_id={connection_id}")
        
        if order_id and order_id in self.order_connections:
            if connection_id and connection_id in self.order_connections[order_id]:
                del self.order_connections[order_id][connection_id]
                logger.info(f"断开订单连接: order_id={order_id}, connection_id={connection_id}")
        
        if table_id and table_id in self.table_connections:
            if connection_id and connection_id in self.table_connections[table_id]:
                del self.table_connections[table_id][connection_id]
                logger.info(f"断开桌号连接: table_id={table_id}, connection_id={connection_id}")
    
    async def broadcast_to_store(self, store_id: int, message: dict):
        """向店铺的所有连接广播消息"""
        if store_id not in self.store_connections:
            return
        
        disconnected = []
        for connection_id, websocket in self.store_connections[store_id].items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败: store_id={store_id}, connection_id={connection_id}, error={str(e)}")
                disconnected.append(connection_id)
        
        # 清理断开的连接
        for connection_id in disconnected:
            del self.store_connections[store_id][connection_id]
    
    async def broadcast_to_order(self, order_id: int, message: dict):
        """向订单的所有连接广播消息（顾客端）"""
        if order_id not in self.order_connections:
            return
        
        disconnected = []
        for connection_id, websocket in self.order_connections[order_id].items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败: order_id={order_id}, connection_id={connection_id}, error={str(e)}")
                disconnected.append(connection_id)
        
        # 清理断开的连接
        for connection_id in disconnected:
            del self.order_connections[order_id][connection_id]
    
    async def broadcast_to_table(self, table_id: int, message: dict):
        """向桌号的所有连接广播消息（顾客端）"""
        if table_id not in self.table_connections:
            return
        
        disconnected = []
        for connection_id, websocket in self.table_connections[table_id].items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败: table_id={table_id}, connection_id={connection_id}, error={str(e)}")
                disconnected.append(connection_id)
        
        # 清理断开的连接
        for connection_id in disconnected:
            del self.table_connections[table_id][connection_id]
    
    async def broadcast_order_status(self, order_id: int, order_data: dict):
        """
        广播订单状态更新
        同时推送到店铺（店员端）和订单（顾客端）
        """
        message = {
            "type": "order_status_update",
            "order": order_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # 推送到店铺
        if "store_id" in order_data:
            await self.broadcast_to_store(order_data["store_id"], message)
        
        # 推送到订单
        await self.broadcast_to_order(order_id, message)
    
    async def broadcast_new_order(self, order_data: dict):
        """广播新订单到店铺"""
        message = {
            "type": "new_order",
            "order": order_data,
            "timestamp": datetime.now().isoformat()
        }
        
        if "store_id" in order_data:
            await self.broadcast_to_store(order_data["store_id"], message)
    
    async def broadcast_payment_status(self, order_id: int, payment_data: dict):
        """广播支付状态更新"""
        message = {
            "type": "payment_status_update",
            "payment": payment_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # 推送到店铺
        if "store_id" in payment_data:
            await self.broadcast_to_store(payment_data["store_id"], message)
        
        # 推送到订单
        await self.broadcast_to_order(order_id, message)


# 全局连接管理器
manager = ConnectionManager()


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
    """创建订单请求（第一步：确认下单）"""
    table_id: int
    items: List[OrderItemRequest]
    # payment_method 将在第二步支付时设置，这里不需要


class ConfirmPaymentRequest(BaseModel):
    """确认支付请求（第二步：确认支付）"""
    payment_method: str = Field(..., description="支付方式：immediate(马上支付) 或 counter(柜台支付)")

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
    order_number: str  # 添加订单号字段
    store_id: int
    table_id: int
    table_number: str
    total_amount: float
    payment_method: str
    payment_status: str  # 添加支付状态字段
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
async def create_order(order: CreateOrderRequest):
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
        
        # 创建订单（第一步：确认下单，不处理支付）
        db_order = Orders(
            order_number=generate_order_number(),
            store_id=first_store.id,
            table_id=order.table_id,
            total_amount=total_amount,
            discount_amount=0,
            final_amount=total_amount,
            payment_method="",  # 支付方式将在第二步设置
            payment_status="unpaid",  # 初始状态为未支付
            order_status="pending"  # 厨师可以开始制作
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
        
        # 广播新订单到店员端（WebSocket通知）
        try:
            order_data = {
                "id": db_order.id,
                "order_number": db_order.order_number,
                "store_id": db_order.store_id,
                "table_id": db_order.table_id,
                "table_number": table.table_number,
                "total_amount": float(db_order.total_amount),
                "payment_method": db_order.payment_method,
                "payment_status": db_order.payment_status,
                "status": db_order.order_status,
                "created_at": db_order.created_at.isoformat() if db_order.created_at else "",
                "items": order_items_data
            }
            # 直接使用await调用异步方法
            await manager.broadcast_new_order(order_data)
        except Exception as ws_error:
            logger.error(f"WebSocket通知失败: {str(ws_error)}")
            # WebSocket失败不影响订单创建，只记录错误

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
            order_number=db_order.order_number,
            store_id=db_order.store_id,
            table_id=db_order.table_id,
            table_number=table_number,
            total_amount=float(db_order.total_amount),
            payment_method=db_order.payment_method,
            payment_status=db_order.payment_status,
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


@app.post("/api/orders/{order_id}/confirm-payment")
async def confirm_payment(order_id: int, req: ConfirmPaymentRequest):
    """
    确认支付（第二步）
    顾客选择支付方式后调用此接口
    """
    db = get_session()
    try:
        order = db.query(Orders).filter(Orders.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        # 检查订单是否已支付
        if order.payment_status == "paid":
            raise HTTPException(status_code=400, detail="订单已支付")
        
        # 更新支付方式
        order.payment_method = req.payment_method
        
        # 根据支付方式设置支付状态
        if req.payment_method == "immediate":
            # 马上支付：标记为已支付
            order.payment_status = "paid"
            payment_time = datetime.now()
            # 如果订单还没有开始制作，可以保持pending状态
            # 如果订单已经在制作中，不影响
        elif req.payment_method == "counter":
            # 柜台支付：保持未支付状态，餐后到收银台支付
            order.payment_status = "unpaid"
        else:
            raise HTTPException(status_code=400, detail=f"不支持的支付方式: {req.payment_method}")
        
        db.commit()
        
        # 广播支付状态更新（WebSocket通知）
        try:
            order_data = {
                "id": order.id,
                "order_number": order.order_number,
                "store_id": order.store_id,
                "table_id": order.table_id,
                "total_amount": float(order.total_amount),
                "payment_method": order.payment_method,
                "payment_status": order.payment_status,
                "status": order.order_status,
                "created_at": order.created_at.isoformat() if order.created_at else ""
            }
            # 广播支付状态更新
            await manager.broadcast_payment_status(order_id, order_data)
        except Exception as ws_error:
            logger.error(f"WebSocket通知失败: {str(ws_error)}")
        
        return {
            "message": "支付确认成功",
            "order_id": order.id,
            "payment_method": order.payment_method,
            "payment_status": order.payment_status
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"确认支付失败: {str(e)}")
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
            order_number=order.order_number,
            store_id=order.store_id,
            table_id=order.table_id,
            table_number=table_number,
            total_amount=float(order.total_amount),
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            status=order.order_status,
            created_at=order.created_at.isoformat() if order.created_at else "",
            items=order_items
        )
    finally:
        db.close()


@app.patch("/api/orders/{order_id}/status")
async def update_order_status(order_id: int, req: UpdateOrderStatusRequest):
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
        
        # 广播订单状态更新（WebSocket通知）
        try:
            # 获取完整的订单数据
            order_data = {
                "id": order.id,
                "order_number": order.order_number,
                "store_id": order.store_id,
                "table_id": order.table_id,
                "total_amount": float(order.total_amount),
                "payment_method": order.payment_method,
                "status": order.order_status,
                "created_at": order.created_at.isoformat() if order.created_at else ""
            }
            # 直接使用await调用异步方法
            await manager.broadcast_order_status(order_id, order_data)
        except Exception as ws_error:
            logger.error(f"WebSocket通知失败: {str(ws_error)}")
        
        return {"message": "订单状态更新成功", "status": new_status}
    finally:
        db.close()


@app.patch("/api/orders/{order_id}/items/{item_id}/status")
async def update_order_item_status(order_id: int, item_id: int, req: UpdateItemStatusRequest):
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
        
        # 广播订单项状态更新（WebSocket通知）
        try:
            import asyncio
            # 获取订单信息
            order = db.query(Orders).filter(Orders.id == order_id).first()
            if order:
                order_data = {
                    "id": order.id,
                    "order_number": order.order_number,
                    "store_id": order.store_id,
                    "table_id": order.table_id,
                    "total_amount": float(order.total_amount),
                    "payment_method": order.payment_method,
                    "status": order.order_status,
                    "created_at": order.created_at.isoformat() if order.created_at else ""
                }
                # 直接使用await调用异步方法
                await manager.broadcast_order_status(order_id, order_data)
        except Exception as ws_error:
            logger.error(f"WebSocket通知失败: {str(ws_error)}")
        
        return {"message": "菜品状态更新成功", "item_status": new_status}
    finally:
        db.close()


# 订单流程配置路由
try:
    from api.order_flow_api import router as order_flow_router
    # 注册订单流程配置路由
    app.include_router(order_flow_router)
except ImportError:
    # 如果没有order_flow_api模块，跳过
    pass



# ============ 二维码生成 API ============

@app.post("/api/generate-styled-qrcode")
def generate_styled_qrcode(
    table_id: int = Form(...),
    base_url: str = Form(default="https://order.example.com"),
    foreground_color: str = Form(default="black"),
    background_color: str = Form(default="white"),
    logo_ratio: float = Form(default=0.2),
    logo: Optional[UploadFile] = None
):
    """
    生成带样式的二维码
    支持自定义颜色和添加logo
    """
    import io
    import qrcode
    from qrcode.constants import ERROR_CORRECT_H
    from PIL import Image, ImageDraw
    from storage.s3.s3_storage import S3SyncStorage
    import os

    db = get_session()
    try:
        # 验证桌号是否存在
        table = db.query(Tables).filter(Tables.id == table_id).first()
        if not table:
            raise HTTPException(status_code=404, detail=f"桌号ID {table_id} 不存在")

        # 读取logo数据
        logo_data = None
        if logo:
            logo_data = logo.file.read()

        # 生成二维码内容（前端期望的格式）
        qrcode_content = f"{base_url}/customer_order_v2.html?table={table.table_number}"

        # 生成二维码图片
        qr = qrcode.QRCode(
            version=1,
            error_correction=ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qrcode_content)
        qr.make(fit=True)

        # 转换为图片，使用自定义颜色
        img = qr.make_image(fill_color=foreground_color, back_color=background_color)
        img = img.convert('RGB')

        # 如果有logo，添加到二维码中间
        if logo_data:
            try:
                # 加载logo图片
                logo_img = Image.open(io.BytesIO(logo_data))

                # 计算logo尺寸
                qr_width, qr_height = img.size
                logo_size = int(min(qr_width, qr_height) * logo_ratio)

                # 调整logo大小
                logo_img.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)

                # 转换为RGBA模式以支持透明度
                if logo_img.mode != 'RGBA':
                    logo_img = logo_img.convert('RGBA')

                # 计算logo位置（居中）
                logo_position = (
                    (qr_width - logo_size) // 2,
                    (qr_height - logo_size) // 2
                )

                # 将logo粘贴到二维码上
                img.paste(logo_img, logo_position, logo_img)
            except Exception as e:
                print(f"添加logo失败: {str(e)}")

        # 将图片转换为字节流
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()

        # 上传到S3
        storage = S3SyncStorage(
            endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
            access_key="",
            secret_key="",
            bucket_name=os.getenv("COZE_BUCKET_NAME"),
            region="cn-beijing",
        )

        # 生成文件名
        color_fg = foreground_color.replace('#', '')
        color_bg = background_color.replace('#', '')
        file_name = f"qrcode_table{table.table_number}_{color_fg}_{color_bg}.png"

        qrcode_key = storage.upload_file(
            file_content=img_bytes,
            file_name=file_name,
            content_type="image/png"
        )

        # 生成签名URL
        qrcode_url = storage.generate_presigned_url(
            key=qrcode_key,
            expire_time=3600
        )

        return {
            "qrcode_url": qrcode_url,
            "qrcode_content": qrcode_content,
            "table_id": table.id,
            "table_number": table.table_number
        }
    finally:
        db.close()


@app.get("/health")
def health_check():
    """健康检查"""
    # Check database connection
    db_status = {"connected": False, "error": None}
    try:
        from storage.database.db import get_engine
        from storage.database.check_tables import check_tables_exist
        
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status["connected"] = True
            db_status["message"] = "数据库连接成功"
            
            # Check tables
            table_status = check_tables_exist(engine)
            db_status["tables"] = table_status
            
    except Exception as e:
        db_status["error"] = str(e)
        db_status["message"] = f"数据库连接失败: {str(e)}"
        import traceback
        db_status["traceback"] = traceback.format_exc()
    
    # Check environment variables
    env_status = {
        "PGDATABASE_URL": "✓ 已设置" if os.getenv("PGDATABASE_URL") else "✗ 未设置",
    }
    
    # Check installed packages
    packages_status = {}
    for pkg_name in ["pg8000", "psycopg2", "psycopg"]:
        try:
            __import__(pkg_name)
            packages_status[pkg_name] = "✓ 已安装"
        except ImportError:
            packages_status[pkg_name] = "✗ 未安装"
    
    return {
        "status": "ok" if db_status["connected"] else "error",
        "message": "餐饮系统API服务运行正常",
        "database": db_status,
        "environment": env_status,
        "packages": packages_status
    }


# ============ 诊断端点 ============

@app.get("/diagnostic/env")
def check_env():
    """检查环境变量"""
    return {
        "PGDATABASE_URL": "✓ 已设置" if os.getenv("PGDATABASE_URL") else "✗ 未设置",
        "PORT": os.getenv("PORT", "8000"),
        "PYTHON_VERSION": os.getenv("PYTHON_VERSION", "未设置"),
    }


@app.get("/diagnostic/database")
def check_db():
    """检查数据库连接"""
    result = {
        "connection_successful": False,
        "error": None
    }

    try:
        from storage.database.db import get_engine
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            result["connection_successful"] = True
            result["message"] = "数据库连接成功"
    except Exception as e:
        result["error"] = str(e)
        result["message"] = f"数据库连接失败: {str(e)}"
        import traceback
        result["traceback"] = traceback.format_exc()

    return result


@app.get("/diagnostic/health")
def full_health_check():
    """完整健康检查"""
    db_status = check_db()

    return {
        "status": "healthy" if db_status["connection_successful"] else "unhealthy",
        "database": db_status,
        "environment": check_env()
    }


# ============ WebSocket 接口 ============

@app.websocket("/ws/store/{store_id}")
async def websocket_store(
    websocket: WebSocket,
    store_id: int,
    connection_id: str = Query(default=None)
):
    """
    店铺WebSocket连接
    店员端使用，接收新订单和订单状态更新
    """
    if not connection_id:
        connection_id = f"store_{store_id}_{datetime.now().timestamp()}"
    
    await manager.connect_to_store(websocket, store_id, connection_id)
    
    try:
        while True:
            # 接收客户端消息（心跳等）
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理心跳
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
    except WebSocketDisconnect:
        manager.disconnect(store_id=store_id, connection_id=connection_id)
    except Exception as e:
        logger.error(f"店铺WebSocket错误: {str(e)}")
        manager.disconnect(store_id=store_id, connection_id=connection_id)


@app.websocket("/ws/order/{order_id}")
async def websocket_order(
    websocket: WebSocket,
    order_id: int,
    connection_id: str = Query(default=None)
):
    """
    订单WebSocket连接
    顾客端使用，接收订单状态和支付状态更新
    """
    if not connection_id:
        connection_id = f"order_{order_id}_{datetime.now().timestamp()}"
    
    await manager.connect_to_order(websocket, order_id, connection_id)
    
    try:
        while True:
            # 接收客户端消息（心跳等）
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理心跳
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
    except WebSocketDisconnect:
        manager.disconnect(order_id=order_id, connection_id=connection_id)
    except Exception as e:
        logger.error(f"订单WebSocket错误: {str(e)}")
        manager.disconnect(order_id=order_id, connection_id=connection_id)


@app.websocket("/ws/table/{table_id}")
async def websocket_table(
    websocket: WebSocket,
    table_id: int,
    connection_id: str = Query(default=None)
):
    """
    桌号WebSocket连接
    顾客端使用，接收该桌号的订单状态更新
    """
    if not connection_id:
        connection_id = f"table_{table_id}_{datetime.now().timestamp()}"
    
    await manager.connect_to_table(websocket, table_id, connection_id)
    
    try:
        while True:
            # 接收客户端消息（心跳等）
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理心跳
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
    except WebSocketDisconnect:
        manager.disconnect(table_id=table_id, connection_id=connection_id)
    except Exception as e:
        logger.error(f"桌号WebSocket错误: {str(e)}")
        manager.disconnect(table_id=table_id, connection_id=connection_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
