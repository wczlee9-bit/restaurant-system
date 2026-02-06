from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from storage.database.db_config import get_db
from storage.database.models import User, Order
from typing import Optional
from datetime import datetime
from routes.auth_routes import get_current_active_user

router = APIRouter(prefix="/api/members", tags=["会员管理"])

class MemberInfo(BaseModel):
    id: int
    username: str
    real_name: Optional[str]
    phone: Optional[str]
    points: int
    level: str
    total_orders: int
    total_spent: float
    
    class Config:
        from_attributes = True

class PointsResponse(BaseModel):
    points: int
    change: int
    reason: str
    created_at: datetime

@router.get("/me", response_model=MemberInfo)
def get_my_member_info(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的会员信息"""
    
    # 获取总订单数和总消费
    user_orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    total_orders = len(user_orders)
    total_spent = sum(o.total_amount for o in user_orders if o.payment_status == 'paid')
    
    # 获取积分（从用户表）
    points = getattr(current_user, 'points', 0)
    
    # 计算会员等级
    level = "普通会员"
    if points >= 1000:
        level = "黄金会员"
    elif points >= 500:
        level = "白银会员"
    elif points >= 100:
        level = "青铜会员"
    
    return MemberInfo(
        id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        phone=current_user.phone,
        points=points,
        level=level,
        total_orders=total_orders,
        total_spent=float(total_spent)
    )

@router.get("/{user_id}", response_model=MemberInfo)
def get_member_info(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取指定用户的会员信息"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取总订单数和总消费
    user_orders = db.query(Order).filter(Order.user_id == user_id).all()
    total_orders = len(user_orders)
    total_spent = sum(o.total_amount for o in user_orders if o.payment_status == 'paid')
    
    # 获取积分
    points = getattr(user, 'points', 0)
    
    # 计算会员等级
    level = "普通会员"
    if points >= 1000:
        level = "黄金会员"
    elif points >= 500:
        level = "白银会员"
    elif points >= 100:
        level = "青铜会员"
    
    return MemberInfo(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        phone=user.phone,
        points=points,
        level=level,
        total_orders=total_orders,
        total_spent=float(total_spent)
    )

@router.post("/{user_id}/points/add")
def add_points(
    user_id: int,
    points: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """给用户添加积分"""
    
    if points <= 0:
        raise HTTPException(status_code=400, detail="积分必须大于0")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    current_points = getattr(user, 'points', 0)
    user.points = current_points + points
    
    db.commit()
    
    return {
        "message": "积分添加成功",
        "old_points": current_points,
        "new_points": user.points,
        "added": points,
        "reason": reason
    }

@router.post("/{user_id}/points/deduct")
def deduct_points(
    user_id: int,
    points: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """扣除用户积分"""
    
    if points <= 0:
        raise HTTPException(status_code=400, detail="积分必须大于0")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    current_points = getattr(user, 'points', 0)
    
    if current_points < points:
        raise HTTPException(status_code=400, detail="积分不足")
    
    user.points = current_points - points
    
    db.commit()
    
    return {
        "message": "积分扣除成功",
        "old_points": current_points,
        "new_points": user.points,
        "deducted": points,
        "reason": reason
    }

@router.get("/list")
def get_members_list(
    store_id: int = 1,
    min_points: Optional[int] = None,
    level: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取会员列表"""
    
    query = db.query(User)
    
    if min_points is not None:
        if hasattr(User, 'points'):
            query = query.filter(User.points >= min_points)
    
    users = query.limit(limit).all()
    
    members = []
    for user in users:
        # 计算等级
        points = getattr(user, 'points', 0)
        user_level = "普通会员"
        if points >= 1000:
            user_level = "黄金会员"
        elif points >= 500:
            user_level = "白银会员"
        elif points >= 100:
            user_level = "青铜会员"
        
        if level and user_level != level:
            continue
        
        members.append({
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "phone": user.phone,
            "points": points,
            "level": user_level
        })
    
    return members

@router.get("/rankings")
def get_member_rankings(
    store_id: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """获取会员排行榜"""
    
    users = db.query(User).order_by(
        getattr(User, 'points', 0).desc()
    ).limit(limit).all()
    
    return [
        {
            "rank": idx + 1,
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "phone": user.phone,
            "points": getattr(user, 'points', 0)
        }
        for idx, user in enumerate(users)
    ]
