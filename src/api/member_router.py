"""
会员管理 API Router
支持会员信息查询、积分兑换、等级管理等
"""
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from storage.database.db import get_session
from storage.database.shared.model import Members, PointLogs, MemberLevelRules, Orders, OrderItems, Stores
import logging

# 创建 API Router
router = APIRouter(prefix="/api/member", tags=["会员管理"])

logger = logging.getLogger(__name__)


# ============ 数据模型 ============

class MemberInfo(BaseModel):
    """会员信息"""
    id: int
    phone: str
    name: Optional[str] = None
    level: int
    level_name: str
    points: int
    total_spent: float
    total_orders: int
    avatar_url: Optional[str] = None
    discount: float  # 折扣比例


class MemberInfoResponse(BaseModel):
    """会员信息响应"""
    member: MemberInfo
    next_level: Optional[dict] = None  # 下一等级信息


class PointLogInfo(BaseModel):
    """积分日志"""
    id: int
    points: int
    reason: str
    created_at: datetime
    order_number: Optional[str] = None


class RedeemPointsRequest(BaseModel):
    """积分兑换请求"""
    member_id: int
    points: int = Field(..., gt=0, description="兑换积分数")
    reason: str = Field(..., description="兑换原因")


class RegisterMemberRequest(BaseModel):
    """注册会员请求"""
    phone: str = Field(..., min_length=11, max_length=11)
    name: Optional[str] = None


class ApplyDiscountRequest(BaseModel):
    """应用会员折扣请求"""
    member_id: int
    order_amount: float = Field(..., gt=0)


class DiscountResponse(BaseModel):
    """折扣响应"""
    member_id: int
    original_amount: float
    discount_amount: float
    final_amount: float
    discount_rate: float


class OrderItemInfo(BaseModel):
    """订单项信息"""
    item_name: str
    quantity: int
    price: float
    subtotal: float


class OrderInfo(BaseModel):
    """订单信息"""
    id: int
    order_number: str
    store_name: str
    table_number: Optional[str] = None
    total_amount: float
    discount_amount: float
    final_amount: float
    payment_method: Optional[str] = None
    payment_status: str
    order_status: str
    created_at: datetime
    payment_time: Optional[datetime] = None
    items: List[OrderItemInfo]


# ============ 工具函数 ============

def get_member_level_info(level: int) -> dict:
    """
    获取会员等级信息
    """
    db = get_session()
    try:
        level_rule = db.query(MemberLevelRules).filter(
            MemberLevelRules.level == level
        ).first()
        
        if level_rule:
            return {
                "level": level_rule.level,
                "level_name": level_rule.level_name,
                "min_points": level_rule.min_points,
                "discount": level_rule.discount
            }
        else:
            # 默认等级信息
            return {
                "level": level,
                "level_name": "普通会员",
                "min_points": 0,
                "discount": 1.0
            }
    finally:
        db.close()


def get_next_level(current_level: int) -> Optional[dict]:
    """
    获取下一等级信息
    """
    db = get_session()
    try:
        next_level = db.query(MemberLevelRules).filter(
            MemberLevelRules.level > current_level
        ).order_by(MemberLevelRules.level).first()
        
        if next_level:
            return {
                "level": next_level.level,
                "level_name": next_level.level_name,
                "min_points": next_level.min_points,
                "discount": next_level.discount
            }
        return None
    finally:
        db.close()


def calculate_discount(member_id: int, order_amount: float) -> dict:
    """
    计算会员折扣
    """
    db = get_session()
    try:
        member = db.query(Members).filter(Members.id == member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="会员不存在")
        
        # 获取等级信息
        level_info = get_member_level_info(member.level)
        discount_rate = level_info["discount"]
        
        # 计算折扣金额
        discount_amount = order_amount * (1 - discount_rate)
        final_amount = order_amount - discount_amount
        
        return {
            "member_id": member_id,
            "original_amount": order_amount,
            "discount_amount": round(discount_amount, 2),
            "final_amount": round(final_amount, 2),
            "discount_rate": discount_rate
        }
    finally:
        db.close()


# ============ API 接口 ============

@router.get("/levels")
def get_member_levels():
    """
    获取会员等级列表
    """
    db = get_session()
    try:
        levels = db.query(MemberLevelRules).order_by(MemberLevelRules.level).all()
        return [
            {
                "level": level.level,
                "level_name": level.level_name,
                "min_points": level.min_points,
                "discount": level.discount
            }
            for level in levels
        ]
    finally:
        db.close()


@router.post("/register", response_model=MemberInfo)
def register_member(req: RegisterMemberRequest):
    """
    注册会员
    """
    db = get_session()
    try:
        # 检查手机号是否已注册
        existing = db.query(Members).filter(Members.phone == req.phone).first()
        if existing:
            raise HTTPException(status_code=400, detail="该手机号已注册会员")
        
        # 创建新会员（默认等级为1）
        member = Members(
            phone=req.phone,
            name=req.name or "会员",
            level=1,
            points=0,
            total_spent=0.0,
            total_orders=0
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        
        # 获取等级信息
        level_info = get_member_level_info(member.level)
        
        return MemberInfo(
            id=member.id,
            phone=member.phone,
            name=member.name,
            level=member.level,
            level_name=level_info["level_name"],
            points=member.points,
            total_spent=member.total_spent,
            total_orders=member.total_orders,
            avatar_url=member.avatar_url,
            discount=level_info["discount"]
        )
    finally:
        db.close()


@router.get("/{member_id}", response_model=MemberInfoResponse)
def get_member_info(member_id: int):
    """
    获取会员信息
    """
    db = get_session()
    try:
        member = db.query(Members).filter(Members.id == member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="会员不存在")
        
        # 获取等级信息
        level_info = get_member_level_info(member.level)
        next_level_info = get_next_level(member.level)
        
        member_info = MemberInfo(
            id=member.id,
            phone=member.phone,
            name=member.name,
            level=member.level,
            level_name=level_info["level_name"],
            points=member.points,
            total_spent=member.total_spent,
            total_orders=member.total_orders,
            avatar_url=member.avatar_url,
            discount=level_info["discount"]
        )
        
        return MemberInfoResponse(
            member=member_info,
            next_level=next_level_info
        )
    finally:
        db.close()


@router.get("/phone/{phone}", response_model=MemberInfoResponse)
def get_member_by_phone(phone: str):
    """
    通过手机号获取会员信息
    """
    db = get_session()
    try:
        member = db.query(Members).filter(Members.phone == phone).first()
        if not member:
            raise HTTPException(status_code=404, detail="会员不存在")
        
        # 获取等级信息
        level_info = get_member_level_info(member.level)
        next_level_info = get_next_level(member.level)
        
        member_info = MemberInfo(
            id=member.id,
            phone=member.phone,
            name=member.name,
            level=member.level,
            level_name=level_info["level_name"],
            points=member.points,
            total_spent=member.total_spent,
            total_orders=member.total_orders,
            avatar_url=member.avatar_url,
            discount=level_info["discount"]
        )
        
        return MemberInfoResponse(
            member=member_info,
            next_level=next_level_info
        )
    finally:
        db.close()


@router.get("/{member_id}/points-logs", response_model=List[PointLogInfo])
def get_member_points_logs(member_id: int):
    """
    获取会员积分日志
    """
    db = get_session()
    try:
        member = db.query(Members).filter(Members.id == member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="会员不存在")
        
        logs = db.query(PointLogs).filter(
            PointLogs.member_id == member_id
        ).order_by(PointLogs.created_at.desc()).limit(50).all()
        
        return [
            PointLogInfo(
                id=log.id,
                points=log.points,
                reason=log.reason,
                created_at=log.created_at,
                order_number=log.order_number
            )
            for log in logs
        ]
    finally:
        db.close()


@router.post("/redeem")
def redeem_points(req: RedeemPointsRequest):
    """
    积分兑换
    """
    db = get_session()
    try:
        member = db.query(Members).filter(Members.id == req.member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="会员不存在")
        
        if member.points < req.points:
            raise HTTPException(status_code=400, detail="积分不足")
        
        # 扣除积分
        member.points -= req.points
        db.add(PointLogs(
            member_id=member.id,
            points=-req.points,
            reason=req.reason
        ))
        db.commit()
        
        return {"message": "积分兑换成功", "remaining_points": member.points}
    finally:
        db.close()


@router.post("/apply-discount", response_model=DiscountResponse)
def apply_discount(req: ApplyDiscountRequest):
    """
    应用会员折扣
    """
    discount_info = calculate_discount(req.member_id, req.order_amount)
    return DiscountResponse(**discount_info)


@router.get("/{member_id}/orders", response_model=List[OrderInfo])
def get_member_orders(member_id: int, limit: int = 10):
    """
    获取会员订单列表
    """
    db = get_session()
    try:
        member = db.query(Members).filter(Members.id == member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="会员不存在")
        
        orders = db.query(Orders).filter(
            Orders.member_id == member_id
        ).order_by(Orders.created_at.desc()).limit(limit).all()
        
        result = []
        for order in orders:
            order_items = db.query(OrderItems).filter(
                OrderItems.order_id == order.id
            ).all()
            
            items = [
                OrderItemInfo(
                    item_name=oi.menu_item_name or "",
                    quantity=oi.quantity,
                    price=float(oi.price),
                    subtotal=float(oi.subtotal)
                )
                for oi in order_items
            ]
            
            result.append(OrderInfo(
                id=order.id,
                order_number=order.order_number,
                store_name=order.store.name if order.store else "",
                table_number=order.table.table_number if order.table else None,
                total_amount=float(order.total_amount),
                discount_amount=float(order.discount_amount or 0),
                final_amount=float(order.total_amount - (order.discount_amount or 0)),
                payment_method=order.payment_method,
                payment_status=order.payment_status,
                order_status=order.order_status,
                created_at=order.created_at,
                payment_time=order.payment_time,
                items=items
            ))
        
        return result
    finally:
        db.close()


@router.get("/{member_id}/orders/{order_id}", response_model=OrderInfo)
def get_member_order_detail(member_id: int, order_id: int):
    """
    获取会员订单详情
    """
    db = get_session()
    try:
        order = db.query(Orders).filter(
            Orders.id == order_id,
            Orders.member_id == member_id
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        order_items = db.query(OrderItems).filter(
            OrderItems.order_id == order.id
        ).all()
        
        items = [
            OrderItemInfo(
                item_name=oi.menu_item_name or "",
                quantity=oi.quantity,
                price=float(oi.price),
                subtotal=float(oi.subtotal)
            )
            for oi in order_items
        ]
        
        return OrderInfo(
            id=order.id,
            order_number=order.order_number,
            store_name=order.store.name if order.store else "",
            table_number=order.table.table_number if order.table else None,
            total_amount=float(order.total_amount),
            discount_amount=float(order.discount_amount or 0),
            final_amount=float(order.total_amount - (order.discount_amount or 0)),
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            order_status=order.order_status,
            created_at=order.created_at,
            payment_time=order.payment_time,
            items=items
        )
    finally:
        db.close()
