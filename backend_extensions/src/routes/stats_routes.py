from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from storage.database.db_config import get_db
from storage.database.models import Order, OrderItem, MenuItem
from typing import Optional
from datetime import datetime, timedelta
from routes.auth_routes import get_current_active_user

router = APIRouter(prefix="/api/stats", tags=["数据统计"])

class DailyStats(BaseModel):
    date: str
    orders_count: int
    total_revenue: float

class OrderStatusStats(BaseModel):
    status: str
    count: int

@router.get("/overview")
def get_overview_stats(
    store_id: int = 1,
    days: int = Query(7, description="统计最近几天的数据"),
    db: Session = Depends(get_db)
):
    """获取概览统计数据"""
    
    # 计算时间范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 今日数据
    today = datetime.now().date()
    
    # 今日订单数
    today_orders = db.query(Order).filter(
        Order.store_id == store_id,
        func.date(Order.created_at) == today
    ).count()
    
    # 今日营收
    today_revenue = db.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(
        Order.store_id == store_id,
        func.date(Order.created_at) == today,
        Order.payment_status == 'paid'
    ).scalar()
    
    # 待处理订单
    pending_orders = db.query(Order).filter(
        Order.store_id == store_id,
        Order.status.in_(['pending', 'confirmed'])
    ).count()
    
    # 菜品总数
    total_menu_items = db.query(MenuItem).filter(
        MenuItem.store_id == store_id
    ).count()
    
    # 订单状态统计
    status_stats = db.query(
        Order.status,
        func.count(Order.id)
    ).filter(
        Order.store_id == store_id
    ).group_by(Order.status).all()
    
    status_distribution = {status: count for status, count in status_stats}
    
    # 每日统计
    daily_stats = db.query(
        func.date(Order.created_at).label('date'),
        func.count(Order.id).label('orders_count'),
        func.coalesce(func.sum(Order.total_amount), 0).label('total_revenue')
    ).filter(
        Order.store_id == store_id,
        func.date(Order.created_at) >= start_date.date(),
        func.date(Order.created_at) <= end_date.date(),
        Order.payment_status == 'paid'
    ).group_by(func.date(Order.created_at)).all()
    
    daily_chart = [
        DailyStats(date=str(row.date), orders_count=row.orders_count, total_revenue=row.total_revenue)
        for row in daily_stats
    ]
    
    return {
        "today_orders": today_orders,
        "today_revenue": float(today_revenue),
        "pending_orders": pending_orders,
        "total_menu_items": total_menu_items,
        "status_distribution": status_distribution,
        "daily_chart": daily_chart
    }

@router.get("/top-items")
def get_top_items(
    store_id: int = 1,
    limit: int = Query(10, description="返回前几名"),
    db: Session = Depends(get_db)
):
    """获取最受欢迎的菜品"""
    
    results = db.query(
        OrderItem.menu_item_id,
        MenuItem.name,
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.sum(OrderItem.subtotal).label('total_revenue')
    ).join(
        Order, OrderItem.order_id == Order.id
    ).join(
        MenuItem, OrderItem.menu_item_id == MenuItem.id
    ).filter(
        Order.store_id == store_id
    ).group_by(
        OrderItem.menu_item_id,
        MenuItem.name
    ).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(limit).all()
    
    return [
        {
            "menu_item_id": row.menu_item_id,
            "name": row.name,
            "total_quantity": row.total_quantity,
            "total_revenue": float(row.total_revenue)
        }
        for row in results
    ]

@router.get("/revenue-trend")
def get_revenue_trend(
    store_id: int = 1,
    days: int = Query(30, description="统计最近几天的数据"),
    db: Session = Depends(get_db)
):
    """获取营收趋势"""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    results = db.query(
        func.date(Order.created_at).label('date'),
        func.count(Order.id).label('orders_count'),
        func.coalesce(func.sum(Order.total_amount), 0).label('total_revenue')
    ).filter(
        Order.store_id == store_id,
        func.date(Order.created_at) >= start_date.date(),
        func.date(Order.created_at) <= end_date.date(),
        Order.payment_status == 'paid'
    ).group_by(
        func.date(Order.created_at)
    ).order_by(
        func.date(Order.created_at)
    ).all()
    
    return [
        {
            "date": str(row.date),
            "orders_count": row.orders_count,
            "revenue": float(row.total_revenue)
        }
        for row in results
    ]
