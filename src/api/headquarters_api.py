"""
总公司管理后台 API
支持查看所有店铺的营收情况、人员情况、数据统计等
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from storage.database.db import get_session
from storage.database.shared.model import (
    Companies, Stores, Orders, DailyRevenue, Staff,
    Users, Roles, UserRoles, OrderItems, Members
)
import logging

# 创建 FastAPI 应用
app = FastAPI(title="扫码点餐系统 - 总公司管理API", version="1.0.0")

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

class StoreSummary(BaseModel):
    """店铺概要信息"""
    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    manager_name: Optional[str] = None
    is_active: bool
    created_at: datetime


class StoreRevenueStats(BaseModel):
    """店铺营收统计"""
    store_id: int
    store_name: str
    total_orders: int
    total_revenue: float
    average_order_value: float
    payment_methods: dict


class StoreStaffStats(BaseModel):
    """店铺人员统计"""
    store_id: int
    store_name: str
    total_staff: int
    active_staff: int
    staff_by_position: dict


class OverallStats(BaseModel):
    """总体统计"""
    total_stores: int
    active_stores: int
    total_orders: int
    total_revenue: float
    total_members: int
    total_staff: int


class RevenueTrend(BaseModel):
    """营收趋势"""
    date: str
    total_revenue: float
    total_orders: int
    store_count: int


class StaffInfo(BaseModel):
    """员工信息"""
    id: int
    user_id: int
    name: str
    phone: Optional[str] = None
    position: str
    store_name: str
    is_active: bool
    roles: List[str] = []


# ============ 工具函数 ============

def get_date_range(days: int = 30) -> tuple:
    """
    获取日期范围
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


# ============ API 接口 ============

@app.get("/")
def root():
    """根路径"""
    return {
        "message": "扫码点餐系统 - 总公司管理API",
        "version": "1.0.0",
        "endpoints": {
            "GET /api/headquarters/overall-stats": "获取总体统计",
            "GET /api/headquarters/stores": "获取店铺列表",
            "GET /api/headquarters/stores/{store_id}/revenue": "获取店铺营收统计",
            "GET /api/headquarters/stores/{store_id}/staff": "获取店铺人员统计",
            "GET /api/headquarters/stores/revenue-ranking": "获取店铺营收排名",
            "GET /api/headquarters/revenue-trend": "获取营收趋势",
            "GET /api/headquarters/staff": "获取所有员工信息",
            "GET /api/headquarters/members": "获取会员统计"
        }
    }


@app.get("/api/headquarters/overall-stats", response_model=OverallStats)
def get_overall_stats():
    """
    获取总体统计
    """
    db = get_session()
    try:
        # 店铺统计
        total_stores = db.query(func.count(Stores.id)).scalar()
        active_stores = db.query(func.count(Stores.id)).filter(
            Stores.is_active == True
        ).scalar()
        
        # 订单和营收统计
        total_orders = db.query(func.count(Orders.id)).scalar()
        total_revenue = db.query(func.sum(Orders.final_amount)).scalar() or 0
        
        # 会员统计
        total_members = db.query(func.count(Members.id)).scalar()
        
        # 员工统计
        total_staff = db.query(func.count(Staff.id)).scalar()
        
        return OverallStats(
            total_stores=total_stores,
            active_stores=active_stores,
            total_orders=total_orders,
            total_revenue=round(total_revenue, 2),
            total_members=total_members,
            total_staff=total_staff
        )
        
    finally:
        db.close()


@app.get("/api/headquarters/stores", response_model=List[StoreSummary])
def get_stores(
    is_active: Optional[bool] = Query(None, description="是否激活"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    获取店铺列表
    """
    db = get_session()
    try:
        query = db.query(Stores)
        
        if is_active is not None:
            query = query.filter(Stores.is_active == is_active)
        
        stores = query.order_by(Stores.created_at.desc()).offset(skip).limit(limit).all()
        
        result = []
        for store in stores:
            result.append(StoreSummary(
                id=store.id,
                name=store.name,
                address=store.address,
                phone=store.phone,
                manager_name=store.manager.name if store.manager else None,
                is_active=store.is_active,
                created_at=store.created_at
            ))
        
        return result
        
    finally:
        db.close()


@app.get("/api/headquarters/stores/{store_id}/revenue", response_model=StoreRevenueStats)
def get_store_revenue_stats(
    store_id: int,
    days: int = Query(30, ge=1, le=365, description="统计天数")
):
    """
    获取店铺营收统计
    """
    db = get_session()
    try:
        # 验证店铺存在
        store = db.query(Stores).filter(Stores.id == store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail="店铺不存在")
        
        # 获取日期范围
        start_date, end_date = get_date_range(days)
        
        # 查询订单统计
        orders = db.query(Orders).filter(
            and_(
                Orders.store_id == store_id,
                Orders.created_at >= start_date,
                Orders.created_at <= end_date,
                Orders.payment_status == 'paid'
            )
        ).all()
        
        total_orders = len(orders)
        total_revenue = sum(order.final_amount for order in orders)
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # 支付方式统计
        payment_methods = {}
        for order in orders:
            method = order.payment_method or 'unknown'
            if method not in payment_methods:
                payment_methods[method] = {'count': 0, 'amount': 0}
            payment_methods[method]['count'] += 1
            payment_methods[method]['amount'] += order.final_amount
        
        return StoreRevenueStats(
            store_id=store.id,
            store_name=store.name,
            total_orders=total_orders,
            total_revenue=round(total_revenue, 2),
            average_order_value=round(average_order_value, 2),
            payment_methods=payment_methods
        )
        
    finally:
        db.close()


@app.get("/api/headquarters/stores/{store_id}/staff", response_model=StoreStaffStats)
def get_store_staff_stats(store_id: int):
    """
    获取店铺人员统计
    """
    db = get_session()
    try:
        # 验证店铺存在
        store = db.query(Stores).filter(Stores.id == store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail="店铺不存在")
        
        # 查询员工
        staff_list = db.query(Staff).filter(Staff.store_id == store_id).all()
        
        total_staff = len(staff_list)
        active_staff = sum(1 for s in staff_list if s.is_active)
        
        # 按职位统计
        staff_by_position = {}
        for staff in staff_list:
            position = staff.position
            if position not in staff_by_position:
                staff_by_position[position] = {'total': 0, 'active': 0}
            staff_by_position[position]['total'] += 1
            if staff.is_active:
                staff_by_position[position]['active'] += 1
        
        return StoreStaffStats(
            store_id=store.id,
            store_name=store.name,
            total_staff=total_staff,
            active_staff=active_staff,
            staff_by_position=staff_by_position
        )
        
    finally:
        db.close()


@app.get("/api/headquarters/stores/revenue-ranking")
def get_revenue_ranking(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    top: int = Query(10, ge=1, le=50, description="返回前N名")
):
    """
    获取店铺营收排名
    """
    db = get_session()
    try:
        # 获取日期范围
        start_date, end_date = get_date_range(days)
        
        # 查询每个店铺的营收
        results = db.query(
            Stores.id,
            Stores.name,
            func.count(Orders.id).label('total_orders'),
            func.sum(Orders.final_amount).label('total_revenue')
        ).outerjoin(Orders, and_(
            Orders.store_id == Stores.id,
            Orders.created_at >= start_date,
            Orders.created_at <= end_date,
            Orders.payment_status == 'paid'
        )).group_by(Stores.id, Stores.name).order_by(
            desc('total_revenue')
        ).limit(top).all()
        
        ranking = []
        for idx, result in enumerate(results, 1):
            ranking.append({
                "rank": idx,
                "store_id": result.id,
                "store_name": result.name,
                "total_orders": result.total_orders or 0,
                "total_revenue": round(result.total_revenue or 0, 2)
            })
        
        return ranking
        
    finally:
        db.close()


@app.get("/api/headquarters/revenue-trend", response_model=List[RevenueTrend])
def get_revenue_trend(
    days: int = Query(30, ge=1, le=365, description="统计天数")
):
    """
    获取营收趋势
    """
    db = get_session()
    try:
        # 获取日期范围
        start_date, end_date = get_date_range(days)
        
        # 按天统计
        results = db.query(
            func.date(Orders.created_at).label('date'),
            func.count(Orders.id).label('total_orders'),
            func.sum(Orders.final_amount).label('total_revenue'),
            func.count(func.distinct(Orders.store_id)).label('store_count')
        ).filter(
            and_(
                Orders.created_at >= start_date,
                Orders.created_at <= end_date,
                Orders.payment_status == 'paid'
            )
        ).group_by(func.date(Orders.created_at)).order_by('date').all()
        
        trend = []
        for result in results:
            trend.append(RevenueTrend(
                date=result.date.strftime('%Y-%m-%d'),
                total_revenue=round(result.total_revenue or 0, 2),
                total_orders=result.total_orders,
                store_count=result.store_count
            ))
        
        return trend
        
    finally:
        db.close()


@app.get("/api/headquarters/staff", response_model=List[StaffInfo])
def get_all_staff(
    store_id: Optional[int] = Query(None, description="店铺ID筛选"),
    is_active: Optional[bool] = Query(None, description="是否在职"),
    position: Optional[str] = Query(None, description="职位筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """
    获取所有员工信息
    """
    db = get_session()
    try:
        query = db.query(Staff).join(Users).join(Stores)
        
        if store_id is not None:
            query = query.filter(Staff.store_id == store_id)
        
        if is_active is not None:
            query = query.filter(Staff.is_active == is_active)
        
        if position is not None:
            query = query.filter(Staff.position == position)
        
        staff_list = query.order_by(Staff.created_at.desc()).offset(skip).limit(limit).all()
        
        result = []
        for staff in staff_list:
            # 查询用户角色
            user_roles = db.query(Roles).join(UserRoles).filter(
                UserRoles.user_id == staff.user_id
            ).all()
            roles = [role.name for role in user_roles]
            
            result.append(StaffInfo(
                id=staff.id,
                user_id=staff.user_id,
                name=staff.user.name,
                phone=staff.user.phone,
                position=staff.position,
                store_name=staff.store.name if staff.store else "未知店铺",
                is_active=staff.is_active,
                roles=roles
            ))
        
        return result
        
    finally:
        db.close()


@app.get("/api/headquarters/members")
def get_members_stats(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    获取会员统计
    """
    db = get_session()
    try:
        # 获取日期范围
        start_date, end_date = get_date_range(days)
        
        # 查询新注册会员
        new_members = db.query(Members).filter(
            Members.created_at >= start_date,
            Members.created_at <= end_date
        ).order_by(Members.created_at.desc()).offset(skip).limit(limit).all()
        
        # 总体会员统计
        total_members = db.query(func.count(Members.id)).scalar()
        active_members = db.query(func.count(Members.id)).filter(
            Members.total_orders > 0
        ).scalar()
        
        # 会员等级分布
        level_distribution = db.query(
            Members.level,
            func.count(Members.id).label('count')
        ).group_by(Members.level).all()
        
        # 总积分和总消费
        total_points = db.query(func.sum(Members.points)).scalar() or 0
        total_spent = db.query(func.sum(Members.total_spent)).scalar() or 0
        
        members_list = []
        for member in new_members:
            members_list.append({
                "id": member.id,
                "phone": member.phone,
                "name": member.name,
                "level": member.level,
                "points": member.points,
                "total_spent": member.total_spent,
                "total_orders": member.total_orders,
                "created_at": member.created_at
            })
        
        return {
            "total_members": total_members,
            "active_members": active_members,
            "new_members_count": len(new_members),
            "total_points": total_points,
            "total_spent": round(total_spent, 2),
            "level_distribution": [
                {"level": item.level, "count": item.count}
                for item in level_distribution
            ],
            "new_members": members_list
        }
        
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
