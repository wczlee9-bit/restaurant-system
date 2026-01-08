"""
支付功能 API
支持微信支付、支付宝等多种支付方式
"""
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import random
import string
from storage.database.db import get_session
from storage.database.shared.model import Orders, Payments, Members, PointLogs
import asyncio
import logging

# 创建 FastAPI 应用
app = FastAPI(title="扫码点餐系统 - 支付API", version="1.0.0")

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

class CreatePaymentRequest(BaseModel):
    """创建支付请求"""
    order_id: int
    payment_method: str = Field(..., description="支付方式: wechat, alipay, cash, credit_card")
    customer_phone: Optional[str] = None  # 手机号，用于会员识别


class PaymentResponse(BaseModel):
    """支付响应"""
    payment_id: int
    order_id: int
    order_number: str
    amount: float
    payment_method: str
    payment_url: Optional[str] = None  # 支付URL（用于扫码支付）
    qr_code: Optional[str] = None  # 支付二维码内容
    status: str


class PaymentStatusResponse(BaseModel):
    """支付状态响应"""
    payment_id: int
    order_id: int
    order_number: str
    amount: float
    payment_method: str
    status: str
    transaction_id: Optional[str] = None
    paid_at: Optional[datetime] = None


class PaymentCallbackRequest(BaseModel):
    """支付回调请求（模拟）"""
    payment_id: int
    transaction_id: Optional[str] = None
    success: bool = True


# ============ 工具函数 ============

def generate_transaction_id() -> str:
    """生成交易号"""
    now = datetime.now()
    random_str = ''.join(random.choices(string.digits, k=8))
    return f"TXN{now.strftime('%Y%m%d%H%M%S')}{random_str}"


async def process_payment_success(payment_id: int, db: Session):
    """
    处理支付成功
    - 更新订单支付状态
    - 增加会员积分
    """
    try:
        # 获取支付记录
        payment = db.query(Payments).filter(Payments.id == payment_id).first()
        if not payment:
            logger.error(f"支付记录不存在: {payment_id}")
            return
        
        # 更新支付状态
        payment.status = "success"
        payment.transaction_id = payment.transaction_id or generate_transaction_id()
        payment.payment_time = datetime.now()
        
        # 更新订单支付状态
        order = db.query(Orders).filter(Orders.id == payment.order_id).first()
        if order:
            order.payment_status = "paid"
            order.payment_method = payment.payment_method
            order.payment_time = payment.payment_time
        
        db.commit()
        
        # 增加会员积分（如果顾客是会员）
        if order and order.customer_phone:
            member = db.query(Members).filter(Members.phone == order.customer_phone).first()
            if member:
                # 积分规则：消费1元 = 1积分
                points = int(order.final_amount)
                
                # 增加积分
                member.points += points
                member.total_spent += order.final_amount
                member.total_orders += 1
                
                # 记录积分日志
                point_log = PointLogs(
                    member_id=member.id,
                    order_id=order.id,
                    points=points,
                    reason=f"订单消费: {order.order_number}"
                )
                db.add(point_log)
                db.commit()
                
                logger.info(f"会员 {member.name} 积分增加 {points}，当前积分: {member.points}")
        
        logger.info(f"支付成功处理完成: 支付ID={payment_id}, 订单ID={payment.order_id}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"处理支付成功失败: {str(e)}")


# ============ API 接口 ============

@app.get("/")
def root():
    """根路径"""
    return {
        "message": "扫码点餐系统 - 支付API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/payment/create": "创建支付",
            "GET /api/payment/{payment_id}/status": "查询支付状态",
            "POST /api/payment/callback": "支付回调",
            "POST /api/payment/{payment_id}/cancel": "取消支付"
        }
    }


@app.post("/api/payment/create", response_model=PaymentResponse)
def create_payment(request: CreatePaymentRequest, background_tasks: BackgroundTasks):
    """
    创建支付订单
    """
    db = get_session()
    try:
        # 获取订单
        order = db.query(Orders).filter(Orders.id == request.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        # 检查订单支付状态
        if order.payment_status == "paid":
            raise HTTPException(status_code=400, detail="订单已支付")
        
        # 创建支付记录
        payment = Payments(
            order_id=order.id,
            payment_method=request.payment_method,
            amount=order.final_amount,
            refund_amount=0.0,  # 退款金额默认为0
            status="pending"
        )
        db.add(payment)
        db.flush()
        
        # 根据支付方式生成支付信息
        payment_url = None
        qr_code = None
        
        if request.payment_method in ["wechat", "alipay"]:
            # 模拟生成支付二维码
            qr_code = f"pay://fake.{request.payment_method}.com?payment_id={payment.id}&amount={order.final_amount}"
            payment_url = f"http://localhost:8000/api/payment/qr/{payment.id}"
        elif request.payment_method == "credit_card":
            # 信用卡支付需要跳转到收银台
            payment_url = f"http://localhost:8000/api/payment/card/{payment.id}"
        # 现金支付不需要支付链接
        
        db.commit()
        db.refresh(payment)
        
        response = PaymentResponse(
            payment_id=payment.id,
            order_id=order.id,
            order_number=order.order_number,
            amount=payment.amount,
            payment_method=payment.payment_method,
            payment_url=payment_url,
            qr_code=qr_code,
            status=payment.status
        )
        
        logger.info(f"创建支付订单成功: 支付ID={payment.id}, 订单号={order.order_number}, 金额={order.final_amount}")
        return response
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建支付订单失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建支付订单失败: {str(e)}")
    finally:
        db.close()


@app.get("/api/payment/{payment_id}/status", response_model=PaymentStatusResponse)
def get_payment_status(payment_id: int):
    """
    查询支付状态
    """
    db = get_session()
    try:
        payment = db.query(Payments).filter(Payments.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="支付记录不存在")
        
        order = db.query(Orders).filter(Orders.id == payment.order_id).first()
        
        return PaymentStatusResponse(
            payment_id=payment.id,
            order_id=payment.order_id,
            order_number=order.order_number if order else "",
            amount=payment.amount,
            payment_method=payment.payment_method,
            status=payment.status,
            transaction_id=payment.transaction_id,
            paid_at=payment.payment_time
        )
        
    finally:
        db.close()


@app.post("/api/payment/callback")
def payment_callback(request: PaymentCallbackRequest, background_tasks: BackgroundTasks):
    """
    支付回调（模拟）
    实际使用时，这里会是微信支付/支付宝的回调接口
    """
    db = get_session()
    try:
        # 获取支付记录
        payment = db.query(Payments).filter(Payments.id == request.payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="支付记录不存在")
        
        # 检查支付状态
        if payment.status == "success":
            logger.warning(f"支付回调重复: 支付ID={request.payment_id}")
            return {"message": "支付已成功", "payment_id": payment.id}
        
        if payment.status == "failed":
            raise HTTPException(status_code=400, detail="支付已失败")
        
        # 更新支付状态
        if request.success:
            payment.status = "processing"  # 先设为处理中
            
            # 异步处理支付成功
            background_tasks.add_task(process_payment_success, request.payment_id, db)
            
            logger.info(f"支付回调成功: 支付ID={request.payment_id}")
            return {
                "message": "支付成功",
                "payment_id": payment.id,
                "status": "processing"
            }
        else:
            payment.status = "failed"
            db.commit()
            logger.error(f"支付回调失败: 支付ID={request.payment_id}")
            raise HTTPException(status_code=400, detail="支付失败")
            
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"处理支付回调失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理支付回调失败: {str(e)}")
    finally:
        db.close()


@app.post("/api/payment/{payment_id}/cancel")
def cancel_payment(payment_id: int):
    """
    取消支付
    """
    db = get_session()
    try:
        payment = db.query(Payments).filter(Payments.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="支付记录不存在")
        
        # 检查支付状态
        if payment.status == "success":
            raise HTTPException(status_code=400, detail="支付已成功，无法取消")
        
        if payment.status == "failed":
            raise HTTPException(status_code=400, detail="支付已失败")
        
        # 更新支付状态
        payment.status = "cancelled"
        db.commit()
        
        logger.info(f"支付已取消: 支付ID={payment_id}")
        return {
            "message": "支付已取消",
            "payment_id": payment_id
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"取消支付失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"取消支付失败: {str(e)}")
    finally:
        db.close()


@app.get("/api/payment/methods")
def get_payment_methods():
    """
    获取支持的支付方式
    """
    return {
        "methods": [
            {
                "id": "wechat",
                "name": "微信支付",
                "description": "使用微信扫码支付",
                "icon": "wechat-pay"
            },
            {
                "id": "alipay",
                "name": "支付宝",
                "description": "使用支付宝扫码支付",
                "icon": "alipay"
            },
            {
                "id": "cash",
                "name": "现金支付",
                "description": "现金支付，由店员确认",
                "icon": "cash"
            },
            {
                "id": "credit_card",
                "name": "信用卡",
                "description": "刷卡支付",
                "icon": "credit-card"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
