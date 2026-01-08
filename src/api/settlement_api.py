"""
跨店铺结算与第三方积分互通 API
支持跨店铺积分结算、第三方积分兑换、积分协议管理等功能
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

from src.storage.database.db import get_session
from src.storage.database.shared.model import (
    StorePointSettlements, ThirdPartyPointAgreements, PointExchangeLogs,
    Stores, Members, PointLogs, Orders
)
import logging

# 创建 FastAPI 应用
app = FastAPI(title="扫码点餐系统 - 跨店铺结算API", version="1.0.0")

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

class StoreSettlementRequest(BaseModel):
    """跨店铺结算请求"""
    source_store_id: int = Field(..., description="积分来源店铺ID")
    target_store_id: int = Field(..., description="积分目标店铺ID")
    member_id: int = Field(..., description="会员ID")
    points: int = Field(..., gt=0, description="积分数量")
    order_id: Optional[int] = Field(None, description="关联订单ID")
    settlement_rate: float = Field(1.0, ge=0, description="结算汇率")
    remarks: Optional[str] = Field(None, description="备注")


class StoreSettlementResponse(BaseModel):
    """跨店铺结算响应"""
    id: int
    source_store_id: int
    target_store_id: int
    member_id: int
    points: int
    settlement_date: datetime
    status: str
    settlement_amount: Optional[float] = None
    source_store_name: str
    target_store_name: str
    member_name: Optional[str] = None
    member_phone: Optional[str] = None


class ThirdPartyAgreementRequest(BaseModel):
    """第三方积分协议请求"""
    store_id: int = Field(..., description="本店铺ID")
    third_party_name: str = Field(..., description="第三方公司名称")
    agreement_type: str = Field(..., description="协议类型: bidirectional(双向), inbound(只进), outbound(只出)")
    exchange_rate: float = Field(1.0, gt=0, description="积分兑换比例: 1第三方积分 = 本方积分")
    max_points_per_day: Optional[int] = Field(None, description="每日最大兑换积分数")
    max_points_per_order: Optional[int] = Field(None, description="单笔订单最大兑换积分数")
    settlement_cycle: str = Field("daily", description="结算周期: daily, weekly, monthly")
    valid_from: Optional[date] = Field(None, description="生效日期")
    valid_until: Optional[date] = Field(None, description="到期日期")
    contact_person: Optional[str] = Field(None, description="联系人")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    remarks: Optional[str] = Field(None, description="备注")


class PointExchangeRequest(BaseModel):
    """积分兑换请求"""
    member_id: int = Field(..., description="会员ID")
    store_id: int = Field(..., description="店铺ID")
    agreement_id: int = Field(..., description="第三方协议ID")
    exchange_type: str = Field(..., description="兑换类型: inbound(第三方->本方), outbound(本方->第三方)")
    points: int = Field(..., gt=0, description="积分数量")
    order_id: Optional[int] = Field(None, description="关联订单ID")
    third_party_order_no: Optional[str] = Field(None, description="第三方订单号")
    remarks: Optional[str] = Field(None, description="备注")


class PointExchangeResponse(BaseModel):
    """积分兑换响应"""
    id: int
    member_id: int
    store_id: int
    agreement_id: int
    exchange_type: str
    source_points: int
    target_points: int
    exchange_rate: float
    status: str
    created_at: datetime
    member_name: Optional[str] = None
    store_name: str
    agreement_name: str


# ============ 工具函数 ============

def calculate_settlement_amount(points: int, rate: float) -> float:
    """
    计算结算金额（假设1积分=1元，可根据汇率调整）
    """
    return round(points * rate, 2)


def validate_store_settlement(
    db: Session,
    source_store_id: int,
    target_store_id: int,
    member_id: int,
    points: int
) -> tuple[bool, str]:
    """
    验证跨店铺结算请求
    """
    # 检查店铺是否存在
    source_store = db.query(Stores).filter(Stores.id == source_store_id).first()
    if not source_store:
        return False, "积分来源店铺不存在"
    
    target_store = db.query(Stores).filter(Stores.id == target_store_id).first()
    if not target_store:
        return False, "积分目标店铺不存在"
    
    if source_store_id == target_store_id:
        return False, "来源店铺和目标店铺不能相同"
    
    # 检查会员是否存在
    member = db.query(Members).filter(Members.id == member_id).first()
    if not member:
        return False, "会员不存在"
    
    # 检查会员积分是否足够（从来源店铺）
    # 这里假设会员积分是全局的，不区分店铺
    # 如果需要区分店铺积分，需要扩展 Members 模型
    if member.points < points:
        return False, f"会员积分不足（当前积分：{member.points}，需要：{points}）"
    
    return True, ""


def validate_point_exchange(
    db: Session,
    agreement_id: int,
    points: int,
    member_id: int
) -> tuple[bool, str, Optional[ThirdPartyPointAgreements]]:
    """
    验证积分兑换请求
    """
    # 检查协议是否存在且有效
    agreement = db.query(ThirdPartyPointAgreements).filter(
        ThirdPartyPointAgreements.id == agreement_id
    ).first()
    
    if not agreement:
        return False, "积分协议不存在", None
    
    if agreement.status != "active":
        return False, f"协议状态不活跃（当前状态：{agreement.status}）", None
    
    # 检查有效期
    now = datetime.now().date()
    if agreement.valid_from and now < agreement.valid_from:
        return False, "协议尚未生效", agreement
    
    if agreement.valid_until and now > agreement.valid_until:
        return False, "协议已过期", agreement
    
    # 检查每日限额
    if agreement.max_points_per_day:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_exchange = db.query(PointExchangeLogs).filter(
            PointExchangeLogs.agreement_id == agreement_id,
            PointExchangeLogs.created_at >= today_start,
            PointExchangeLogs.status == "success"
        ).count()
        
        if today_exchange + points > agreement.max_points_per_day:
            return False, f"超过每日最大兑换限额（已使用：{today_exchange}，限额：{agreement.max_points_per_day}）", agreement
    
    # 检查单笔订单限额
    if agreement.max_points_per_order and points > agreement.max_points_per_order:
        return False, f"超过单笔订单最大兑换限额（{agreement.max_points_per_order}）", agreement
    
    # 检查会员积分是否足够（如果是出库兑换）
    if member_id:
        member = db.query(Members).filter(Members.id == member_id).first()
        if not member:
            return False, "会员不存在", agreement
        
        if member.points < points:
            return False, f"会员积分不足（当前积分：{member.points}，需要：{points}）", agreement
    
    return True, "", agreement


# ============ API 接口 ============

@app.get("/")
def root():
    """根路径"""
    return {
        "message": "扫码点餐系统 - 跨店铺结算API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/settlement/store": "创建跨店铺结算",
            "GET /api/settlement/store/{settlement_id}": "获取结算详情",
            "GET /api/settlement/store/list": "获取结算列表",
            "POST /api/settlement/third-party-agreements": "创建第三方积分协议",
            "GET /api/settlement/third-party-agreements": "获取协议列表",
            "GET /api/settlement/third-party-agreements/{agreement_id}": "获取协议详情",
            "POST /api/settlement/exchange-points": "积分兑换",
            "GET /api/settlement/exchange-logs": "获取兑换日志",
            "GET /api/settlement/statistics": "获取结算统计",
        }
    }


# ============ 跨店铺结算接口 ============

@app.post("/api/settlement/store", response_model=StoreSettlementResponse)
def create_store_settlement(request: StoreSettlementRequest):
    """
    创建跨店铺结算
    
    功能：记录会员在一个店铺消费时使用另一个店铺的积分
    """
    db = get_session()
    try:
        # 验证请求
        is_valid, error_msg = validate_store_settlement(
            db,
            request.source_store_id,
            request.target_store_id,
            request.member_id,
            request.points
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # 计算结算金额
        settlement_amount = calculate_settlement_amount(request.points, request.settlement_rate)
        
        # 创建结算记录
        settlement = StorePointSettlements(
            source_store_id=request.source_store_id,
            target_store_id=request.target_store_id,
            member_id=request.member_id,
            points=request.points,
            settlement_date=datetime.now(),
            status="pending",
            order_id=request.order_id,
            settlement_rate=request.settlement_rate,
            settlement_amount=settlement_amount,
            remarks=request.remarks
        )
        
        db.add(settlement)
        db.commit()
        db.refresh(settlement)
        
        # 获取关联数据
        source_store = db.query(Stores).filter(Stores.id == request.source_store_id).first()
        target_store = db.query(Stores).filter(Stores.id == request.target_store_id).first()
        member = db.query(Members).filter(Members.id == request.member_id).first()
        
        # 扣除会员积分（从来源店铺）
        member.points -= request.points
        db.commit()
        
        # 记录积分日志
        point_log = PointLogs(
            member_id=request.member_id,
            points=-request.points,
            reason=f"跨店铺结算：店铺{source_store.name} -> 店铺{target_store.name}",
            order_id=request.order_id
        )
        db.add(point_log)
        db.commit()
        
        logger.info(f"创建跨店铺结算：会员 {member.phone} 在 {target_store.name} 消费，使用 {source_store.name} 积分 {request.points}")
        
        return StoreSettlementResponse(
            id=settlement.id,
            source_store_id=settlement.source_store_id,
            target_store_id=settlement.target_store_id,
            member_id=settlement.member_id,
            points=settlement.points,
            settlement_date=settlement.settlement_date,
            status=settlement.status,
            settlement_amount=settlement.settlement_amount,
            source_store_name=source_store.name,
            target_store_name=target_store.name,
            member_name=member.name,
            member_phone=member.phone
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建跨店铺结算失败：{str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建结算失败：{str(e)}")
    finally:
        db.close()


@app.get("/api/settlement/store/{settlement_id}", response_model=StoreSettlementResponse)
def get_store_settlement(settlement_id: int):
    """
    获取结算详情
    """
    db = get_session()
    try:
        settlement = db.query(StorePointSettlements).filter(
            StorePointSettlements.id == settlement_id
        ).first()
        
        if not settlement:
            raise HTTPException(status_code=404, detail="结算记录不存在")
        
        # 获取关联数据
        source_store = db.query(Stores).filter(Stores.id == settlement.source_store_id).first()
        target_store = db.query(Stores).filter(Stores.id == settlement.target_store_id).first()
        member = db.query(Members).filter(Members.id == settlement.member_id).first()
        
        return StoreSettlementResponse(
            id=settlement.id,
            source_store_id=settlement.source_store_id,
            target_store_id=settlement.target_store_id,
            member_id=settlement.member_id,
            points=settlement.points,
            settlement_date=settlement.settlement_date,
            status=settlement.status,
            settlement_amount=settlement.settlement_amount,
            source_store_name=source_store.name,
            target_store_name=target_store.name,
            member_name=member.name,
            member_phone=member.phone
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取结算详情失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"获取结算详情失败：{str(e)}")
    finally:
        db.close()


@app.get("/api/settlement/store/list")
def get_store_settlement_list(
    source_store_id: Optional[int] = Query(None, description="来源店铺ID"),
    target_store_id: Optional[int] = Query(None, description="目标店铺ID"),
    member_id: Optional[int] = Query(None, description="会员ID"),
    status: Optional[str] = Query(None, description="结算状态"),
    date_from: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量")
):
    """
    获取结算列表（分页）
    """
    db = get_session()
    try:
        query = db.query(StorePointSettlements)
        
        # 筛选条件
        if source_store_id:
            query = query.filter(StorePointSettlements.source_store_id == source_store_id)
        if target_store_id:
            query = query.filter(StorePointSettlements.target_store_id == target_store_id)
        if member_id:
            query = query.filter(StorePointSettlements.member_id == member_id)
        if status:
            query = query.filter(StorePointSettlements.status == status)
        if date_from:
            query = query.filter(StorePointSettlements.settlement_date >= datetime.strptime(date_from, "%Y-%m-%d"))
        if date_to:
            query = query.filter(StorePointSettlements.settlement_date <= datetime.strptime(date_to, "%Y-%m-%d"))
        
        # 总数
        total = query.count()
        
        # 分页
        settlements = query.order_by(
            StorePointSettlements.settlement_date.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        # 转换为响应格式
        result = []
        for settlement in settlements:
            source_store = db.query(Stores).filter(Stores.id == settlement.source_store_id).first()
            target_store = db.query(Stores).filter(Stores.id == settlement.target_store_id).first()
            member = db.query(Members).filter(Members.id == settlement.member_id).first()
            
            result.append({
                "id": settlement.id,
                "source_store_id": settlement.source_store_id,
                "target_store_id": settlement.target_store_id,
                "member_id": settlement.member_id,
                "points": settlement.points,
                "settlement_date": settlement.settlement_date,
                "status": settlement.status,
                "settlement_amount": settlement.settlement_amount,
                "source_store_name": source_store.name if source_store else "未知",
                "target_store_name": target_store.name if target_store else "未知",
                "member_name": member.name if member else "未知",
                "member_phone": member.phone if member else "未知"
            })
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"获取结算列表失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"获取结算列表失败：{str(e)}")
    finally:
        db.close()


# ============ 第三方积分协议接口 ============

@app.post("/api/settlement/third-party-agreements")
def create_third_party_agreement(request: ThirdPartyAgreementRequest):
    """
    创建第三方积分协议
    """
    db = get_session()
    try:
        # 检查店铺是否存在
        store = db.query(Stores).filter(Stores.id == request.store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail="店铺不存在")
        
        # 创建协议
        agreement = ThirdPartyPointAgreements(
            store_id=request.store_id,
            third_party_name=request.third_party_name,
            agreement_type=request.agreement_type,
            exchange_rate=request.exchange_rate,
            max_points_per_day=request.max_points_per_day,
            max_points_per_order=request.max_points_per_order,
            settlement_cycle=request.settlement_cycle,
            valid_from=request.valid_from,
            valid_until=request.valid_until,
            contact_person=request.contact_person,
            contact_phone=request.contact_phone,
            remarks=request.remarks,
            status="active"
        )
        
        db.add(agreement)
        db.commit()
        db.refresh(agreement)
        
        logger.info(f"创建第三方积分协议：{request.third_party_name} <-> {store.name}")
        
        return {
            "message": "第三方积分协议创建成功",
            "agreement_id": agreement.id,
            "agreement": {
                "id": agreement.id,
                "store_id": agreement.store_id,
                "store_name": store.name,
                "third_party_name": agreement.third_party_name,
                "agreement_type": agreement.agreement_type,
                "exchange_rate": agreement.exchange_rate,
                "status": agreement.status,
                "created_at": agreement.created_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建第三方积分协议失败：{str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建协议失败：{str(e)}")
    finally:
        db.close()


@app.get("/api/settlement/third-party-agreements")
def get_third_party_agreements(
    store_id: Optional[int] = Query(None, description="店铺ID"),
    status: Optional[str] = Query(None, description="状态"),
    agreement_type: Optional[str] = Query(None, description="协议类型")
):
    """
    获取第三方积分协议列表
    """
    db = get_session()
    try:
        query = db.query(ThirdPartyPointAgreements)
        
        if store_id:
            query = query.filter(ThirdPartyPointAgreements.store_id == store_id)
        if status:
            query = query.filter(ThirdPartyPointAgreements.status == status)
        if agreement_type:
            query = query.filter(ThirdPartyPointAgreements.agreement_type == agreement_type)
        
        agreements = query.order_by(ThirdPartyPointAgreements.created_at.desc()).all()
        
        result = []
        for agreement in agreements:
            store = db.query(Stores).filter(Stores.id == agreement.store_id).first()
            
            result.append({
                "id": agreement.id,
                "store_id": agreement.store_id,
                "store_name": store.name if store else "未知",
                "third_party_name": agreement.third_party_name,
                "agreement_type": agreement.agreement_type,
                "exchange_rate": agreement.exchange_rate,
                "max_points_per_day": agreement.max_points_per_day,
                "max_points_per_order": agreement.max_points_per_order,
                "settlement_cycle": agreement.settlement_cycle,
                "status": agreement.status,
                "valid_from": agreement.valid_from,
                "valid_until": agreement.valid_until,
                "settlement_balance": agreement.settlement_balance,
                "last_settlement_date": agreement.last_settlement_date,
                "contact_person": agreement.contact_person,
                "contact_phone": agreement.contact_phone,
                "created_at": agreement.created_at
            })
        
        return {
            "total": len(result),
            "data": result
        }
        
    except Exception as e:
        logger.error(f"获取协议列表失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"获取协议列表失败：{str(e)}")
    finally:
        db.close()


@app.get("/api/settlement/third-party-agreements/{agreement_id}")
def get_third_party_agreement_detail(agreement_id: int):
    """
    获取第三方积分协议详情
    """
    db = get_session()
    try:
        agreement = db.query(ThirdPartyPointAgreements).filter(
            ThirdPartyPointAgreements.id == agreement_id
        ).first()
        
        if not agreement:
            raise HTTPException(status_code=404, detail="协议不存在")
        
        store = db.query(Stores).filter(Stores.id == agreement.store_id).first()
        
        # 获取该协议的兑换统计
        total_exchanges = db.query(PointExchangeLogs).filter(
            PointExchangeLogs.agreement_id == agreement_id
        ).count()
        
        success_exchanges = db.query(PointExchangeLogs).filter(
            PointExchangeLogs.agreement_id == agreement_id,
            PointExchangeLogs.status == "success"
        ).count()
        
        return {
            "id": agreement.id,
            "store_id": agreement.store_id,
            "store_name": store.name if store else "未知",
            "third_party_name": agreement.third_party_name,
            "third_party_store_id": agreement.third_party_store_id,
            "agreement_type": agreement.agreement_type,
            "exchange_rate": agreement.exchange_rate,
            "max_points_per_day": agreement.max_points_per_day,
            "max_points_per_order": agreement.max_points_per_order,
            "settlement_cycle": agreement.settlement_cycle,
            "status": agreement.status,
            "valid_from": agreement.valid_from,
            "valid_until": agreement.valid_until,
            "settlement_balance": agreement.settlement_balance,
            "last_settlement_date": agreement.last_settlement_date,
            "api_endpoint": agreement.api_endpoint,
            "contact_person": agreement.contact_person,
            "contact_phone": agreement.contact_phone,
            "remarks": agreement.remarks,
            "created_at": agreement.created_at,
            "updated_at": agreement.updated_at,
            "statistics": {
                "total_exchanges": total_exchanges,
                "success_exchanges": success_exchanges,
                "failed_exchanges": total_exchanges - success_exchanges
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取协议详情失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"获取协议详情失败：{str(e)}")
    finally:
        db.close()


# ============ 积分兑换接口 ============

@app.post("/api/settlement/exchange-points", response_model=PointExchangeResponse)
def exchange_points(request: PointExchangeRequest):
    """
    积分兑换
    
    功能：执行第三方积分兑换
    - inbound: 第三方积分 -> 本方积分（增加会员积分）
    - outbound: 本方积分 -> 第三方积分（扣除会员积分）
    """
    db = get_session()
    try:
        # 验证兑换请求
        is_valid, error_msg, agreement = validate_point_exchange(
            db,
            request.agreement_id,
            request.points,
            request.member_id
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # 计算目标积分
        if request.exchange_type == "inbound":
            # 第三方 -> 本方
            target_points = int(request.points * agreement.exchange_rate)
            source_points = request.points
        else:
            # 本方 -> 第三方
            target_points = int(request.points / agreement.exchange_rate)
            source_points = request.points
        
        # 创建兑换日志
        exchange_log = PointExchangeLogs(
            member_id=request.member_id,
            store_id=request.store_id,
            agreement_id=request.agreement_id,
            exchange_type=request.exchange_type,
            source_points=source_points,
            target_points=target_points,
            exchange_rate=agreement.exchange_rate,
            order_id=request.order_id,
            third_party_order_no=request.third_party_order_no,
            status="pending",
            remarks=request.remarks
        )
        
        db.add(exchange_log)
        db.commit()
        db.refresh(exchange_log)
        
        # 获取会员和店铺信息
        member = db.query(Members).filter(Members.id == request.member_id).first()
        store = db.query(Stores).filter(Stores.id == request.store_id).first()
        
        # 执行积分操作
        if request.exchange_type == "inbound":
            # 增加会员积分
            member.points += target_points
            member.total_spent += target_points  # 假设积分也算消费（可选）
            
            # 记录积分日志
            point_log = PointLogs(
                member_id=request.member_id,
                points=target_points,
                reason=f"第三方积分兑换：{agreement.third_party_name}",
                order_id=request.order_id
            )
            db.add(point_log)
        else:
            # 扣除会员积分
            member.points -= source_points
            
            # 记录积分日志
            point_log = PointLogs(
                member_id=request.member_id,
                points=-source_points,
                reason=f"兑换第三方积分：{agreement.third_party_name}",
                order_id=request.order_id
            )
            db.add(point_log)
        
        # 更新兑换状态为成功
        exchange_log.status = "success"
        exchange_log.completed_at = datetime.now()
        
        # 更新协议结算余额
        if request.exchange_type == "inbound":
            agreement.settlement_balance -= target_points
        else:
            agreement.settlement_balance += source_points
        
        db.commit()
        
        logger.info(f"积分兑换成功：会员 {member.phone} {request.exchange_type} {source_points} 积分 <-> {agreement.third_party_name}")
        
        return PointExchangeResponse(
            id=exchange_log.id,
            member_id=exchange_log.member_id,
            store_id=exchange_log.store_id,
            agreement_id=exchange_log.agreement_id,
            exchange_type=exchange_log.exchange_type,
            source_points=exchange_log.source_points,
            target_points=exchange_log.target_points,
            exchange_rate=exchange_log.exchange_rate,
            status=exchange_log.status,
            created_at=exchange_log.created_at,
            member_name=member.name,
            store_name=store.name,
            agreement_name=agreement.third_party_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"积分兑换失败：{str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"积分兑换失败：{str(e)}")
    finally:
        db.close()


@app.get("/api/settlement/exchange-logs")
def get_exchange_logs(
    agreement_id: Optional[int] = Query(None, description="协议ID"),
    member_id: Optional[int] = Query(None, description="会员ID"),
    store_id: Optional[int] = Query(None, description="店铺ID"),
    exchange_type: Optional[str] = Query(None, description="兑换类型"),
    status: Optional[str] = Query(None, description="状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量")
):
    """
    获取积分兑换日志（分页）
    """
    db = get_session()
    try:
        query = db.query(PointExchangeLogs)
        
        # 筛选条件
        if agreement_id:
            query = query.filter(PointExchangeLogs.agreement_id == agreement_id)
        if member_id:
            query = query.filter(PointExchangeLogs.member_id == member_id)
        if store_id:
            query = query.filter(PointExchangeLogs.store_id == store_id)
        if exchange_type:
            query = query.filter(PointExchangeLogs.exchange_type == exchange_type)
        if status:
            query = query.filter(PointExchangeLogs.status == status)
        
        # 总数
        total = query.count()
        
        # 分页
        logs = query.order_by(
            PointExchangeLogs.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        # 转换为响应格式
        result = []
        for log in logs:
            member = db.query(Members).filter(Members.id == log.member_id).first()
            store = db.query(Stores).filter(Stores.id == log.store_id).first()
            agreement = db.query(ThirdPartyPointAgreements).filter(
                ThirdPartyPointAgreements.id == log.agreement_id
            ).first()
            
            result.append({
                "id": log.id,
                "member_id": log.member_id,
                "member_name": member.name if member else "未知",
                "member_phone": member.phone if member else "未知",
                "store_id": log.store_id,
                "store_name": store.name if store else "未知",
                "agreement_id": log.agreement_id,
                "agreement_name": agreement.third_party_name if agreement else "未知",
                "exchange_type": log.exchange_type,
                "source_points": log.source_points,
                "target_points": log.target_points,
                "exchange_rate": log.exchange_rate,
                "order_id": log.order_id,
                "third_party_order_no": log.third_party_order_no,
                "status": log.status,
                "error_message": log.error_message,
                "created_at": log.created_at,
                "completed_at": log.completed_at,
                "remarks": log.remarks
            })
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"获取兑换日志失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"获取兑换日志失败：{str(e)}")
    finally:
        db.close()


# ============ 统计接口 ============

@app.get("/api/settlement/statistics")
def get_settlement_statistics(
    store_id: Optional[int] = Query(None, description="店铺ID"),
    date_from: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)")
):
    """
    获取结算统计信息
    """
    db = get_session()
    try:
        # 跨店铺结算统计
        settlement_query = db.query(StorePointSettlements)
        
        if store_id:
            settlement_query = settlement_query.filter(
                (StorePointSettlements.source_store_id == store_id) |
                (StorePointSettlements.target_store_id == store_id)
            )
        if date_from:
            settlement_query = settlement_query.filter(
                StorePointSettlements.settlement_date >= datetime.strptime(date_from, "%Y-%m-%d")
            )
        if date_to:
            settlement_query = settlement_query.filter(
                StorePointSettlements.settlement_date <= datetime.strptime(date_to, "%Y-%m-%d")
            )
        
        settlements = settlement_query.all()
        
        total_settlements = len(settlements)
        pending_settlements = len([s for s in settlements if s.status == "pending"])
        completed_settlements = len([s for s in settlements if s.status == "completed"])
        total_points = sum(s.points for s in settlements)
        total_amount = sum(s.settlement_amount or 0 for s in settlements)
        
        # 第三方积分兑换统计
        exchange_query = db.query(PointExchangeLogs)
        
        if store_id:
            exchange_query = exchange_query.filter(PointExchangeLogs.store_id == store_id)
        if date_from:
            exchange_query = exchange_query.filter(
                PointExchangeLogs.created_at >= datetime.strptime(date_from, "%Y-%m-%d")
            )
        if date_to:
            exchange_query = exchange_query.filter(
                PointExchangeLogs.created_at <= datetime.strptime(date_to, "%Y-%m-%d")
            )
        
        exchanges = exchange_query.all()
        
        total_exchanges = len(exchanges)
        success_exchanges = len([e for e in exchanges if e.status == "success"])
        failed_exchanges = len([e for e in exchanges if e.status == "failed"])
        total_inbound_points = sum(e.target_points for e in exchanges if e.exchange_type == "inbound" and e.status == "success")
        total_outbound_points = sum(e.source_points for e in exchanges if e.exchange_type == "outbound" and e.status == "success")
        
        # 第三方协议统计
        agreement_query = db.query(ThirdPartyPointAgreements)
        if store_id:
            agreement_query = agreement_query.filter(ThirdPartyPointAgreements.store_id == store_id)
        
        agreements = agreement_query.all()
        
        total_agreements = len(agreements)
        active_agreements = len([a for a in agreements if a.status == "active"])
        
        return {
            "cross_store_settlements": {
                "total_settlements": total_settlements,
                "pending_settlements": pending_settlements,
                "completed_settlements": completed_settlements,
                "total_points": total_points,
                "total_amount": round(total_amount, 2)
            },
            "third_party_exchanges": {
                "total_exchanges": total_exchanges,
                "success_exchanges": success_exchanges,
                "failed_exchanges": failed_exchanges,
                "total_inbound_points": total_inbound_points,
                "total_outbound_points": total_outbound_points,
                "net_points": total_inbound_points - total_outbound_points
            },
            "agreements": {
                "total_agreements": total_agreements,
                "active_agreements": active_agreements
            },
            "summary": {
                "store_id": store_id,
                "date_from": date_from,
                "date_to": date_to
            }
        }
        
    except Exception as e:
        logger.error(f"获取结算统计失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"获取结算统计失败：{str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
