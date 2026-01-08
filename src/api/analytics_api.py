"""
营收分析报表 API
支持日/周/月营收、菜品销量、订单统计等分析
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from storage.database.db import get_session
from storage.database.shared.model import Orders, OrderItems, MenuItems, Stores, Payments
import logging

# 创建 FastAPI 应用
app = FastAPI(title="扫码点餐系统 - 营收分析API", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)


# ============ 数据模型 ============

class RevenueSummary(BaseModel):
    """营收汇总"""
    period: str  # today, week, month, custom
    start_date: str
    end_date: str
    total_orders: int
    total_amount: float
    total_discount: float
    net_revenue: float
    average_order_amount: float


class PaymentMethodSummary(BaseModel):
    """支付方式统计"""
    payment_method: str
    count: int
    amount: float
    percentage: float


class MenuItemSales(BaseModel):
    """菜品销量"""
    menu_item_id: int
    menu_item_name: str
    quantity: int
    revenue: float
    category_name: Optional[str] = None


class HourlySales(BaseModel):
    """每小时销量"""
    hour: int
    order_count: int
    revenue: float


class OrderStatusSummary(BaseModel):
    """订单状态统计"""
    order_status: str
    count: int
    amount: float


class DailyRevenue(BaseModel):
    """每日营收"""
    date: str
    order_count: int
    revenue: float


# ============ 工具函数 ============

def get_date_range(period: str, custom_start: Optional[str] = None, custom_end: Optional[str] = None):
    """
    根据时间范围获取日期范围
    """
    end_date = datetime.now().date()
    
    if period == "today":
        start_date = end_date
    elif period == "yesterday":
        start_date = end_date - timedelta(days=1)
        end_date = start_date
    elif period == "week":
        start_date = end_date - timedelta(days=end_date.weekday())
    elif period == "month":
        start_date = end_date.replace(day=1)
    elif period == "last_month":
        start_date = (end_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        end_date = end_date.replace(day=1) - timedelta(days=1)
    elif period == "custom" and custom_start and custom_end:
        start_date = datetime.strptime(custom_start, "%Y-%m-%d").date()
        end_date = datetime.strptime(custom_end, "%Y-%m-%d").date()
    else:
        start_date = end_date - timedelta(days=7)  # 默认最近7天
    
    return start_date, end_date


# ============ API 接口 ============

@app.get("/")
def root():
    """根路径"""
    return {
        "message": "扫码点餐系统 - 营收分析API",
        "version": "1.0.0",
        "endpoints": {
            "GET /api/analytics/revenue-summary": "营收汇总",
            "GET /api/analytics/payment-methods": "支付方式统计",
            "GET /api/analytics/menu-item-sales": "菜品销量统计",
            "GET /api/analytics/hourly-sales": "每小时销量统计",
            "GET /api/analytics/order-status": "订单状态统计",
            "GET /api/analytics/daily-revenue": "每日营收趋势",
            "GET /api/analytics/top-orders": "订单排行榜"
        }
    }


@app.get("/api/analytics/revenue-summary", response_model=RevenueSummary)
def get_revenue_summary(
    store_id: int = Query(..., description="店铺ID"),
    period: str = Query("today", description="时间范围: today, yesterday, week, month, last_month, custom"),
    custom_start: Optional[str] = Query(None, description="自定义开始日期 (YYYY-MM-DD)"),
    custom_end: Optional[str] = Query(None, description="自定义结束日期 (YYYY-MM-DD)")
):
    """
    营收汇总
    """
    db = get_session()
    try:
        # 获取日期范围
        start_date, end_date = get_date_range(period, custom_start, custom_end)
        
        # 查询订单数据
        query = db.query(Orders).filter(
            Orders.store_id == store_id,
            func.date(Orders.created_at) >= start_date,
            func.date(Orders.created_at) <= end_date,
            Orders.order_status != 'cancelled'
        )
        
        orders = query.all()
        
        # 计算汇总数据
        total_orders = len(orders)
        total_amount = sum(order.total_amount for order in orders)
        total_discount = sum(order.discount_amount for order in orders)
        net_revenue = sum(order.final_amount for order in orders)
        average_order_amount = net_revenue / total_orders if total_orders > 0 else 0
        
        return RevenueSummary(
            period=period,
            start_date=str(start_date),
            end_date=str(end_date),
            total_orders=total_orders,
            total_amount=round(total_amount, 2),
            total_discount=round(total_discount, 2),
            net_revenue=round(net_revenue, 2),
            average_order_amount=round(average_order_amount, 2)
        )
        
    finally:
        db.close()


@app.get("/api/analytics/payment-methods", response_model=List[PaymentMethodSummary])
def get_payment_methods_summary(
    store_id: int = Query(..., description="店铺ID"),
    period: str = Query("today", description="时间范围: today, week, month, custom"),
    custom_start: Optional[str] = Query(None),
    custom_end: Optional[str] = Query(None)
):
    """
    支付方式统计
    """
    db = get_session()
    try:
        # 获取日期范围
        start_date, end_date = get_date_range(period, custom_start, custom_end)
        
        # 查询支付数据
        payments = db.query(Payments).join(Orders).filter(
            Orders.store_id == store_id,
            func.date(Payments.created_at) >= start_date,
            func.date(Payments.created_at) <= end_date,
            Payments.status == 'success'
        ).all()
        
        # 按支付方式分组统计
        payment_stats = {}
        total_amount = 0
        
        for payment in payments:
            method = payment.payment_method
            if method not in payment_stats:
                payment_stats[method] = {"count": 0, "amount": 0}
            payment_stats[method]["count"] += 1
            payment_stats[method]["amount"] += payment.amount
            total_amount += payment.amount
        
        # 转换为响应格式
        result = []
        for method, stats in payment_stats.items():
            result.append(PaymentMethodSummary(
                payment_method=method,
                count=stats["count"],
                amount=round(stats["amount"], 2),
                percentage=round((stats["amount"] / total_amount * 100), 2) if total_amount > 0 else 0
            ))
        
        # 按金额排序
        result.sort(key=lambda x: x.amount, reverse=True)
        
        return result
        
    finally:
        db.close()


@app.get("/api/analytics/menu-item-sales", response_model=List[MenuItemSales])
def get_menu_item_sales(
    store_id: int = Query(..., description="店铺ID"),
    period: str = Query("today", description="时间范围: today, week, month, custom"),
    custom_start: Optional[str] = Query(None),
    custom_end: Optional[str] = Query(None),
    limit: int = Query(20, description="返回数量限制", ge=1, le=100)
):
    """
    菜品销量统计
    """
    db = get_session()
    try:
        # 获取日期范围
        start_date, end_date = get_date_range(period, custom_start, custom_end)
        
        # 查询订单项数据
        order_items = db.query(OrderItems).join(Orders).filter(
            Orders.store_id == store_id,
            func.date(Orders.created_at) >= start_date,
            func.date(Orders.created_at) <= end_date,
            Orders.order_status != 'cancelled'
        ).all()
        
        # 按菜品分组统计
        item_stats = {}
        
        for item in order_items:
            menu_item_id = item.menu_item_id or 0
            key = (menu_item_id, item.menu_item_name)
            
            if key not in item_stats:
                item_stats[key] = {"quantity": 0, "revenue": 0}
            
            item_stats[key]["quantity"] += item.quantity
            item_stats[key]["revenue"] += item.subtotal
        
        # 转换为响应格式
        result = []
        for (menu_item_id, menu_item_name), stats in item_stats.items():
            result.append(MenuItemSales(
                menu_item_id=menu_item_id,
                menu_item_name=menu_item_name,
                quantity=stats["quantity"],
                revenue=round(stats["revenue"], 2)
            ))
        
        # 按销量排序
        result.sort(key=lambda x: x.quantity, reverse=True)
        
        return result[:limit]
        
    finally:
        db.close()


@app.get("/api/analytics/hourly-sales", response_model=List[HourlySales])
def get_hourly_sales(
    store_id: int = Query(..., description="店铺ID"),
    period: str = Query("today", description="时间范围: today, yesterday"),
    custom_date: Optional[str] = Query(None, description="自定义日期 (YYYY-MM-DD)")
):
    """
    每小时销量统计
    """
    db = get_session()
    try:
        # 获取日期
        if custom_date:
            target_date = datetime.strptime(custom_date, "%Y-%m-%d").date()
        elif period == "yesterday":
            target_date = datetime.now().date() - timedelta(days=1)
        else:
            target_date = datetime.now().date()
        
        # 查询订单数据
        orders = db.query(Orders).filter(
            Orders.store_id == store_id,
            func.date(Orders.created_at) == target_date,
            Orders.order_status != 'cancelled'
        ).all()
        
        # 按小时分组统计
        hourly_stats = {hour: {"count": 0, "revenue": 0} for hour in range(24)}
        
        for order in orders:
            hour = order.created_at.hour
            hourly_stats[hour]["count"] += 1
            hourly_stats[hour]["revenue"] += order.final_amount
        
        # 转换为响应格式
        result = []
        for hour in range(24):
            result.append(HourlySales(
                hour=hour,
                order_count=hourly_stats[hour]["count"],
                revenue=round(hourly_stats[hour]["revenue"], 2)
            ))
        
        return result
        
    finally:
        db.close()


@app.get("/api/analytics/order-status", response_model=List[OrderStatusSummary])
def get_order_status_summary(
    store_id: int = Query(..., description="店铺ID"),
    period: str = Query("today", description="时间范围: today, week, month, custom"),
    custom_start: Optional[str] = Query(None),
    custom_end: Optional[str] = Query(None)
):
    """
    订单状态统计
    """
    db = get_session()
    try:
        # 获取日期范围
        start_date, end_date = get_date_range(period, custom_start, custom_end)
        
        # 查询订单数据
        orders = db.query(Orders).filter(
            Orders.store_id == store_id,
            func.date(Orders.created_at) >= start_date,
            func.date(Orders.created_at) <= end_date
        ).all()
        
        # 按状态分组统计
        status_stats = {}
        
        for order in orders:
            status = order.order_status
            if status not in status_stats:
                status_stats[status] = {"count": 0, "amount": 0}
            
            status_stats[status]["count"] += 1
            status_stats[status]["amount"] += order.final_amount
        
        # 转换为响应格式
        result = []
        for status, stats in status_stats.items():
            result.append(OrderStatusSummary(
                order_status=status,
                count=stats["count"],
                amount=round(stats["amount"], 2)
            ))
        
        return result
        
    finally:
        db.close()


@app.get("/api/analytics/daily-revenue", response_model=List[DailyRevenue])
def get_daily_revenue(
    store_id: int = Query(..., description="店铺ID"),
    days: int = Query(7, description="查询天数", ge=1, le=365)
):
    """
    每日营收趋势
    """
    db = get_session()
    try:
        result = []
        
        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)
            
            # 查询当日订单
            orders = db.query(Orders).filter(
                Orders.store_id == store_id,
                func.date(Orders.created_at) == date,
                Orders.order_status != 'cancelled'
            ).all()
            
            order_count = len(orders)
            revenue = sum(order.final_amount for order in orders)
            
            result.append(DailyRevenue(
                date=str(date),
                order_count=order_count,
                revenue=round(revenue, 2)
            ))
        
        # 按日期升序排列
        result.reverse()
        
        return result
        
    finally:
        db.close()


@app.get("/api/analytics/top-orders")
def get_top_orders(
    store_id: int = Query(..., description="店铺ID"),
    period: str = Query("today", description="时间范围: today, week, month"),
    limit: int = Query(10, description="返回数量限制", ge=1, le=50)
):
    """
    订单排行榜（按金额）
    """
    db = get_session()
    try:
        # 获取日期范围
        start_date, end_date = get_date_range(period)
        
        # 查询订单并排序
        orders = db.query(Orders).filter(
            Orders.store_id == store_id,
            func.date(Orders.created_at) >= start_date,
            func.date(Orders.created_at) <= end_date,
            Orders.order_status != 'cancelled'
        ).order_by(Orders.final_amount.desc()).limit(limit).all()
        
        result = []
        for order in orders:
            result.append({
                "order_id": order.id,
                "order_number": order.order_number,
                "table_id": order.table_id,
                "final_amount": order.final_amount,
                "order_status": order.order_status,
                "created_at": order.created_at.isoformat(),
                "items_count": len(order.order_items)
            })
        
        return result
        
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
