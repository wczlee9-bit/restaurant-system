"""
店员端 API 接口
用于店员接收订单、确认订单、更新订单状态等
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from storage.database.db import get_session
from storage.database.shared.model import Stores, Tables, Orders, OrderItems, OrderStatusLogs, Users

# 创建 FastAPI 应用
app = FastAPI(title="扫码点餐系统 - 店员端 API", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 数据模型 ============

class OrderUpdateRequest(BaseModel):
    """更新订单请求"""
    order_id: int
    order_status: str = Field(..., description="订单状态: pending, confirmed, preparing, ready, serving, completed, cancelled")
    notes: Optional[str] = None
    operator_id: int  # 操作人ID


class OrderItemUpdateRequest(BaseModel):
    """更新订单项请求"""
    order_item_id: int
    status: str = Field(..., description="状态: pending, preparing, ready, serving, completed")


class OrderListResponse(BaseModel):
    """订单列表响应"""
    id: int
    order_number: str
    table_id: int
    table_number: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    total_amount: float
    final_amount: float
    payment_status: str
    order_status: str
    created_at: datetime
    items_count: int


class OrderDetailResponse(BaseModel):
    """订单详情响应"""
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
    items: List[dict]
    status_logs: List[dict]


# ============ 工具函数 ============

ORDER_STATUS_FLOW = {
    'pending': ['confirmed', 'cancelled'],  # 待确认 -> 已确认/已取消
    'confirmed': ['preparing'],  # 已确认 -> 准备中
    'preparing': ['ready'],  # 准备中 -> 已完成
    'ready': ['serving'],  # 已完成 -> 上菜中
    'serving': ['completed'],  # 上菜中 -> 已完成
    'completed': [],  # 已完成 -> 终态
    'cancelled': []  # 已取消 -> 终态
}


def validate_status_transition(from_status: str, to_status: str) -> bool:
    """验证状态流转是否合法"""
    if from_status not in ORDER_STATUS_FLOW:
        return False
    return to_status in ORDER_STATUS_FLOW[from_status]


# ============ API 接口 ============

@app.get("/")
def root():
    """根路径"""
    return {
        "message": "扫码点餐系统 - 店员端 API",
        "version": "1.0.0",
        "endpoints": {
            "GET /api/staff/orders": "获取订单列表",
            "GET /api/staff/order/{order_id}": "获取订单详情",
            "PUT /api/staff/order/status": "更新订单状态",
            "PUT /api/staff/order-item/status": "更新订单项状态",
            "GET /api/staff/store/{store_id}/tables": "获取店铺桌号列表"
        }
    }


@app.get("/api/staff/orders", response_model=List[OrderListResponse])
def get_orders(
    store_id: int = Query(..., description="店铺ID"),
    status: Optional[str] = Query(None, description="订单状态筛选"),
    limit: int = Query(50, description="返回数量限制", ge=1, le=100)
):
    """
    获取订单列表
    """
    db = get_session()
    try:
        query = db.query(Orders).filter(Orders.store_id == store_id)
        
        if status:
            query = query.filter(Orders.order_status == status)
        
        orders = query.order_by(Orders.created_at.desc()).limit(limit).all()
        
        result = []
        for order in orders:
            # 获取桌号信息
            table = db.query(Tables).filter(Tables.id == order.table_id).first()
            table_number = table.table_number if table else ""
            
            result.append(OrderListResponse(
                id=order.id,
                order_number=order.order_number,
                table_id=order.table_id,
                table_number=table_number,
                customer_name=order.customer_name,
                customer_phone=order.customer_phone,
                total_amount=order.total_amount,
                final_amount=order.final_amount,
                payment_status=order.payment_status,
                order_status=order.order_status,
                created_at=order.created_at,
                items_count=len(order.order_items)
            ))
        
        return result
        
    finally:
        db.close()


@app.get("/api/staff/order/{order_id}", response_model=OrderDetailResponse)
def get_order_detail(order_id: int):
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
        items = []
        for oi in order.order_items:
            items.append({
                "id": oi.id,
                "menu_item_name": oi.menu_item_name,
                "menu_item_price": oi.menu_item_price,
                "quantity": oi.quantity,
                "subtotal": oi.subtotal,
                "special_instructions": oi.special_instructions,
                "status": oi.status
            })
        
        # 构建状态日志
        logs = []
        for log in order.order_status_logs:
            operator = db.query(Users).filter(Users.id == log.operator_id).first()
            logs.append({
                "id": log.id,
                "from_status": log.from_status,
                "to_status": log.to_status,
                "created_at": log.created_at,
                "operator_name": operator.name if operator else log.operator_name,
                "notes": log.notes
            })
        
        return OrderDetailResponse(
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
            items=items,
            status_logs=logs
        )
        
    finally:
        db.close()


@app.put("/api/staff/order/status")
def update_order_status(request: OrderUpdateRequest):
    """
    更新订单状态
    """
    db = get_session()
    try:
        # 获取订单
        order = db.query(Orders).filter(Orders.id == request.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        # 验证状态流转
        if not validate_status_transition(order.order_status, request.order_status):
            raise HTTPException(
                status_code=400,
                detail=f"状态流转不合法，从 {order.order_status} 不能直接转到 {request.order_status}"
            )
        
        # 获取操作人信息
        operator = db.query(Users).filter(Users.id == request.operator_id).first()
        if not operator:
            raise HTTPException(status_code=404, detail="操作人不存在")
        
        # 创建状态日志
        status_log = OrderStatusLogs(
            order_id=order.id,
            from_status=order.order_status,
            to_status=request.order_status,
            operator_id=request.operator_id,
            operator_name=operator.name,
            notes=request.notes
        )
        db.add(status_log)
        
        # 更新订单状态
        order.order_status = request.order_status
        
        # 如果取消订单，需要恢复库存
        if request.order_status == 'cancelled':
            for item in order.order_items:
                if item.menu_item:
                    item.menu_item.stock += item.quantity
        
        db.commit()
        
        return {
            "message": "订单状态更新成功",
            "order_id": order.id,
            "from_status": status_log.from_status,
            "to_status": status_log.to_status
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新订单状态失败: {str(e)}")
    finally:
        db.close()


@app.put("/api/staff/order-item/status")
def update_order_item_status(request: OrderItemUpdateRequest):
    """
    更新订单项状态
    """
    db = get_session()
    try:
        # 获取订单项
        order_item = db.query(OrderItems).filter(OrderItems.id == request.order_item_id).first()
        if not order_item:
            raise HTTPException(status_code=404, detail="订单项不存在")
        
        # 更新状态
        order_item.status = request.status
        
        db.commit()
        
        return {
            "message": "订单项状态更新成功",
            "order_item_id": order_item.id,
            "status": order_item.status
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新订单项状态失败: {str(e)}")
    finally:
        db.close()


@app.get("/api/staff/store/{store_id}/tables")
def get_store_tables(store_id: int):
    """
    获取店铺的桌号列表
    """
    db = get_session()
    try:
        tables = db.query(Tables).filter(
            Tables.store_id == store_id
        ).order_by(Tables.table_number).all()
        
        result = []
        for table in tables:
            # 获取该桌号的最新订单
            latest_order = db.query(Orders).filter(
                Orders.table_id == table.id
            ).order_by(Orders.created_at.desc()).first()
            
            result.append({
                "id": table.id,
                "table_number": table.table_number,
                "table_name": table.table_name,
                "seats": table.seats,
                "is_active": table.is_active,
                "current_order_id": latest_order.id if latest_order and latest_order.order_status in ['pending', 'confirmed', 'preparing', 'ready', 'serving'] else None,
                "current_order_status": latest_order.order_status if latest_order and latest_order.order_status in ['pending', 'confirmed', 'preparing', 'ready', 'serving'] else None
            })
        
        return result
        
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
