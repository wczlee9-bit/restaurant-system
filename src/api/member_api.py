"""
会员管理 API
支持会员信息查询、积分兑换、等级管理等
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from storage.database.db import get_session
from storage.database.shared.model import Members, PointLogs, MemberLevelRules, Orders
import logging

# 创建 FastAPI 应用
app = FastAPI(title="扫码点餐系统 - 会员API", version="1.0.0")

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

@app.get("/")
def root():
    """根路径"""
    return {
        "message": "扫码点餐系统 - 会员API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/member/register": "注册会员",
            "GET /api/member/{member_id}": "获取会员信息",
            "GET /api/member/phone/{phone}": "通过手机号获取会员",
            "GET /api/member/{member_id}/points-logs": "获取积分日志",
            "POST /api/member/redeem": "积分兑换",
            "POST /api/member/apply-discount": "应用会员折扣",
            "GET /api/member/levels": "获取会员等级列表"
        }
    }


@app.post("/api/member/register", response_model=MemberInfo)
def register_member(request: RegisterMemberRequest):
    """
    注册会员
    """
    db = get_session()
    try:
        # 检查手机号是否已注册
        existing_member = db.query(Members).filter(Members.phone == request.phone).first()
        if existing_member:
            return MemberInfo(
                id=existing_member.id,
                phone=existing_member.phone,
                name=existing_member.name,
                level=existing_member.level,
                level_name=get_member_level_info(existing_member.level)["level_name"],
                points=existing_member.points,
                total_spent=existing_member.total_spent,
                total_orders=existing_member.total_orders,
                avatar_url=existing_member.avatar_url,
                discount=get_member_level_info(existing_member.level)["discount"]
            )
        
        # 创建新会员
        member = Members(
            phone=request.phone,
            name=request.name or "会员",
            level=1,  # 默认等级
            points=0,
            total_spent=0.0,
            total_orders=0
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        
        level_info = get_member_level_info(member.level)
        
        logger.info(f"会员注册成功: {member.phone}")
        
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
        
    except Exception as e:
        db.rollback()
        logger.error(f"注册会员失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"注册会员失败: {str(e)}")
    finally:
        db.close()


@app.get("/api/member/{member_id}", response_model=MemberInfoResponse)
def get_member_info(member_id: int):
    """
    获取会员信息
    """
    db = get_session()
    try:
        member = db.query(Members).filter(Members.id == member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="会员不存在")
        
        level_info = get_member_level_info(member.level)
        next_level = get_next_level(member.level)
        
        return MemberInfoResponse(
            member=MemberInfo(
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
            ),
            next_level=next_level
        )
        
    finally:
        db.close()


@app.get("/api/member/phone/{phone}", response_model=MemberInfoResponse)
def get_member_by_phone(phone: str):
    """
    通过手机号获取会员
    """
    db = get_session()
    try:
        member = db.query(Members).filter(Members.phone == phone).first()
        if not member:
            raise HTTPException(status_code=404, detail="会员不存在")
        
        level_info = get_member_level_info(member.level)
        next_level = get_next_level(member.level)
        
        return MemberInfoResponse(
            member=MemberInfo(
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
            ),
            next_level=next_level
        )
        
    finally:
        db.close()


@app.get("/api/member/{member_id}/points-logs", response_model=List[PointLogInfo])
def get_points_logs(
    member_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    获取积分日志
    """
    db = get_session()
    try:
        # 验证会员存在
        member = db.query(Members).filter(Members.id == member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="会员不存在")
        
        # 查询积分日志
        logs = db.query(PointLogs).filter(
            PointLogs.member_id == member_id
        ).order_by(PointLogs.created_at.desc()).offset(skip).limit(limit).all()
        
        result = []
        for log in logs:
            order = db.query(Orders).filter(Orders.id == log.order_id).first()
            result.append(PointLogInfo(
                id=log.id,
                points=log.points,
                reason=log.reason,
                created_at=log.created_at,
                order_number=order.order_number if order else None
            ))
        
        return result
        
    finally:
        db.close()


@app.post("/api/member/redeem")
def redeem_points(request: RedeemPointsRequest):
    """
    积分兑换
    """
    db = get_session()
    try:
        # 获取会员
        member = db.query(Members).filter(Members.id == request.member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="会员不存在")
        
        # 检查积分是否足够
        if member.points < request.points:
            raise HTTPException(status_code=400, detail="积分不足")
        
        # 扣减积分
        member.points -= request.points
        
        # 记录积分日志
        point_log = PointLogs(
            member_id=member.id,
            points=-request.points,
            reason=request.reason
        )
        db.add(point_log)
        db.commit()
        
        logger.info(f"会员 {member.name} 积分兑换: {request.points} 积分, 原因: {request.reason}")
        
        return {
            "message": "积分兑换成功",
            "member_id": member.id,
            "redeemed_points": request.points,
            "remaining_points": member.points
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"积分兑换失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"积分兑换失败: {str(e)}")
    finally:
        db.close()


@app.post("/api/member/apply-discount", response_model=DiscountResponse)
def apply_discount(request: ApplyDiscountRequest):
    """
    应用会员折扣
    """
    try:
        discount_info = calculate_discount(request.member_id, request.order_amount)
        return discount_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"应用折扣失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"应用折扣失败: {str(e)}")


@app.get("/api/member/levels")
def get_member_levels():
    """
    获取会员等级列表
    """
    db = get_session()
    try:
        levels = db.query(MemberLevelRules).order_by(MemberLevelRules.level).all()
        
        result = []
        for level in levels:
            result.append({
                "level": level.level,
                "level_name": level.level_name,
                "min_points": level.min_points,
                "discount": level.discount
            })
        
        return result
        
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
