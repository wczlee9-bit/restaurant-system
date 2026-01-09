"""
餐饮系统增强 API
提供菜品图片上传、会员二维码、优惠系统等增强功能
"""
from fastapi import FastAPI, HTTPException, Query, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import io
import logging

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from storage.database.db import get_session
from storage.database.shared.model import (
    Companies, Stores, MenuItems, Members, MemberQRCodes,
    DiscountConfig, MemberLevelRules, Orders
)
from coze_coding_dev_sdk.s3 import S3SyncStorage

logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(title="多店铺扫码点餐系统 - 增强API", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 数据模型 ============

class MenuItemImageUpload(BaseModel):
    """菜品图片上传响应"""
    menu_item_id: int
    image_url: str
    message: str


class MemberQRCodeResponse(BaseModel):
    """会员二维码响应"""
    member_id: int
    member_name: str
    qr_code_url: str
    valid_until: Optional[str] = None


class MemberVerificationRequest(BaseModel):
    """会员验证请求"""
    identifier: str = Field(..., description="会员标识：手机号或二维码内容")


class MemberVerificationResponse(BaseModel):
    """会员验证响应"""
    member_id: int
    phone: str
    name: Optional[str] = None
    level: int
    level_name: str
    points: int
    discount: float
    avatar_url: Optional[str] = None


class DiscountConfigCreate(BaseModel):
    """创建优惠配置"""
    discount_type: str = Field(..., description="优惠类型: percentage, fixed, points")
    discount_value: float = Field(..., gt=0)
    min_amount: Optional[float] = None
    max_discount: Optional[float] = None
    member_level: Optional[int] = None
    points_required: Optional[int] = None
    description: Optional[str] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    is_active: bool = True


class DiscountConfigUpdate(BaseModel):
    """更新优惠配置"""
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    min_amount: Optional[float] = None
    max_discount: Optional[float] = None
    member_level: Optional[int] = None
    points_required: Optional[int] = None
    description: Optional[str] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    is_active: Optional[bool] = None


class DiscountConfigResponse(BaseModel):
    """优惠配置响应"""
    id: int
    store_id: Optional[int] = None
    company_id: Optional[int] = None
    discount_type: str
    discount_value: float
    min_amount: Optional[float] = None
    max_discount: Optional[float] = None
    member_level: Optional[int] = None
    points_required: Optional[int] = None
    description: Optional[str] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    is_active: bool
    created_at: str


class ApplyDiscountRequest(BaseModel):
    """应用优惠请求"""
    member_id: Optional[int] = None
    order_amount: float = Field(..., gt=0)
    member_points: Optional[int] = None
    discount_config_id: Optional[int] = None


class ApplyDiscountResponse(BaseModel):
    """应用优惠响应"""
    original_amount: float
    discount_amount: float
    final_amount: float
    discount_info: dict
    member_info: Optional[dict] = None


# ============ 工具函数 ============

def get_storage():
    """获取S3存储客户端"""
    return S3SyncStorage(
        endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
        access_key="",
        secret_key="",
        bucket_name=os.getenv("COZE_BUCKET_NAME"),
        region="cn-beijing",
    )


def get_member_level_info(level: int) -> dict:
    """获取会员等级信息"""
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
        return {
            "level": level,
            "level_name": "普通会员",
            "min_points": 0,
            "discount": 1.0
        }
    finally:
        db.close()


# ============ 菜品图片上传 ============

@app.post("/api/menu-items/{item_id}/upload-image", response_model=MenuItemImageUpload)
async def upload_menu_item_image(
    item_id: int,
    image: UploadFile = Form(...)
):
    """
    上传菜品图片
    """
    db = get_session()
    try:
        # 验证菜品是否存在
        menu_item = db.query(MenuItems).filter(MenuItems.id == item_id).first()
        if not menu_item:
            raise HTTPException(status_code=404, detail="菜品不存在")
        
        # 验证文件类型
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif"]
        if image.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="只支持JPEG、PNG、GIF格式的图片")
        
        # 读取图片数据
        image_data = await image.read()
        
        # 上传到S3
        storage = get_storage()
        
        # 生成文件名
        file_extension = os.path.splitext(image.filename)[1]
        file_name = f"menu_item_{menu_item.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"
        
        qrcode_key = storage.upload_file(
            file_content=image_data,
            file_name=file_name,
            content_type=image.content_type
        )
        
        # 生成签名URL
        image_url = storage.generate_presigned_url(
            key=qrcode_key,
            expire_time=31536000  # 1年有效期
        )
        
        # 更新菜品图片URL
        menu_item.image_url = image_url
        db.commit()
        
        logger.info(f"菜品图片上传成功: menu_item_id={menu_item.id}, url={image_url}")
        
        return MenuItemImageUpload(
            menu_item_id=menu_item.id,
            image_url=image_url,
            message="菜品图片上传成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"上传菜品图片失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传菜品图片失败: {str(e)}")
    finally:
        db.close()


# ============ 会员二维码 ============

@app.get("/api/member/{member_id}/qrcode", response_model=MemberQRCodeResponse)
def get_member_qrcode(member_id: int, days_valid: int = Query(default=30, ge=1, le=365)):
    """
    获取会员二维码
    如果不存在则自动生成
    """
    import qrcode
    from qrcode.constants import ERROR_CORRECT_H
    from PIL import Image
    
    db = get_session()
    try:
        # 验证会员是否存在
        member = db.query(Members).filter(Members.id == member_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="会员不存在")
        
        # 查找有效的二维码
        now = datetime.now()
        valid_until = now + timedelta(days=days_valid)
        
        qrcode = db.query(MemberQRCodes).filter(
            MemberQRCodes.member_id == member_id,
            MemberQRCodes.is_active == True,
            MemberQRCodes.valid_until > now
        ).first()
        
        # 如果不存在或已过期，生成新的
        if not qrcode:
            # 删除旧的二维码
            db.query(MemberQRCodes).filter(MemberQRCodes.member_id == member_id).delete()
            
            # 生成二维码内容（包含会员ID和加密验证）
            qr_content = f"MEMBER:{member.id}:{now.strftime('%Y%m%d%H%M%S')}"
            
            # 生成二维码图片
            qr = qrcode.QRCode(
                version=1,
                error_correction=ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            
            # 转换为图片
            img = qr.make_image(fill_color="black", back_color="white")
            img = img.convert('RGB')
            
            # 将图片转换为字节流
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # 上传到S3
            storage = get_storage()
            file_name = f"member_qrcode_{member.id}_{now.strftime('%Y%m%d%H%M%S')}.png"
            qrcode_key = storage.upload_file(
                file_content=img_bytes,
                file_name=file_name,
                content_type="image/png"
            )
            
            # 生成签名URL
            qrcode_url = storage.generate_presigned_url(
                key=qrcode_key,
                expire_time=31536000  # 1年有效期
            )
            
            # 创建二维码记录
            qrcode = MemberQRCodes(
                member_id=member.id,
                qr_code_url=qrcode_url,
                qr_code_key=qrcode_key,
                valid_from=now,
                valid_until=valid_until,
                is_active=True
            )
            db.add(qrcode)
            db.commit()
        else:
            qrcode_url = qrcode.qr_code_url
            valid_until = qrcode.valid_until
        
        # 获取等级信息
        level_info = get_member_level_info(member.level)
        
        return MemberQRCodeResponse(
            member_id=member.id,
            member_name=member.name or "会员",
            qr_code_url=qrcode_url,
            valid_until=valid_until.isoformat() if valid_until else None
        )
    except Exception as e:
        db.rollback()
        logger.error(f"获取会员二维码失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取会员二维码失败: {str(e)}")
    finally:
        db.close()


# ============ 会员验证 ============

@app.post("/api/member/verify", response_model=MemberVerificationResponse)
def verify_member(request: MemberVerificationRequest):
    """
    验证会员信息
    支持通过手机号或二维码内容验证
    """
    db = get_session()
    try:
        member = None
        
        # 判断是通过手机号还是二维码验证
        if request.identifier.startswith("MEMBER:"):
            # 通过二维码验证
            parts = request.identifier.split(":")
            if len(parts) >= 2:
                try:
                    member_id = int(parts[1])
                    member = db.query(Members).filter(Members.id == member_id).first()
                except ValueError:
                    pass
        else:
            # 通过手机号验证
            member = db.query(Members).filter(
                Members.phone == request.identifier
            ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="会员不存在")
        
        # 更新二维码扫描次数（如果是二维码验证）
        if request.identifier.startswith("MEMBER:"):
            qrcode = db.query(MemberQRCodes).filter(
                MemberQRCodes.member_id == member.id,
                MemberQRCodes.is_active == True
            ).first()
            if qrcode:
                qrcode.scan_count += 1
                qrcode.last_scan_time = datetime.now()
                db.commit()
        
        # 获取等级信息
        level_info = get_member_level_info(member.level)
        
        return MemberVerificationResponse(
            member_id=member.id,
            phone=member.phone,
            name=member.name,
            level=member.level,
            level_name=level_info["level_name"],
            points=member.points,
            discount=level_info["discount"],
            avatar_url=member.avatar_url
        )
    finally:
        db.close()


# ============ 优惠配置 ============

@app.post("/api/discount-config", response_model=DiscountConfigResponse)
def create_discount_config(
    config: DiscountConfigCreate,
    store_id: Optional[int] = None,
    company_id: Optional[int] = None
):
    """
    创建优惠配置
    必须指定 store_id 或 company_id 其中一个
    """
    db = get_session()
    try:
        if not store_id and not company_id:
            raise HTTPException(status_code=400, detail="必须指定店铺ID或公司ID")
        
        if store_id and company_id:
            raise HTTPException(status_code=400, detail="店铺ID和公司ID只能指定一个")
        
        # 验证店铺或公司是否存在
        if store_id:
            store = db.query(Stores).filter(Stores.id == store_id).first()
            if not store:
                raise HTTPException(status_code=404, detail="店铺不存在")
        
        if company_id:
            company = db.query(Companies).filter(Companies.id == company_id).first()
            if not company:
                raise HTTPException(status_code=404, detail="公司不存在")
        
        # 转换日期字符串
        valid_from_date = None
        valid_until_date = None
        if config.valid_from:
            valid_from_date = datetime.fromisoformat(config.valid_from)
        if config.valid_until:
            valid_until_date = datetime.fromisoformat(config.valid_until)
        
        db_config = DiscountConfig(
            store_id=store_id,
            company_id=company_id,
            discount_type=config.discount_type,
            discount_value=config.discount_value,
            min_amount=config.min_amount,
            max_discount=config.max_discount,
            member_level=config.member_level,
            points_required=config.points_required,
            description=config.description,
            valid_from=valid_from_date,
            valid_until=valid_until_date,
            is_active=config.is_active
        )
        
        db.add(db_config)
        db.commit()
        db.refresh(db_config)
        
        logger.info(f"优惠配置创建成功: config_id={db_config.id}")
        
        return DiscountConfigResponse(
            id=db_config.id,
            store_id=db_config.store_id,
            company_id=db_config.company_id,
            discount_type=db_config.discount_type,
            discount_value=float(db_config.discount_value),
            min_amount=float(db_config.min_amount) if db_config.min_amount else None,
            max_discount=float(db_config.max_discount) if db_config.max_discount else None,
            member_level=db_config.member_level,
            points_required=db_config.points_required,
            description=db_config.description,
            valid_from=db_config.valid_from.isoformat() if db_config.valid_from else None,
            valid_until=db_config.valid_until.isoformat() if db_config.valid_until else None,
            is_active=db_config.is_active,
            created_at=db_config.created_at.isoformat()
        )
    except Exception as e:
        db.rollback()
        logger.error(f"创建优惠配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建优惠配置失败: {str(e)}")
    finally:
        db.close()


@app.get("/api/discount-config", response_model=List[DiscountConfigResponse])
def get_discount_configs(
    store_id: Optional[int] = None,
    company_id: Optional[int] = None,
    is_active: Optional[bool] = None
):
    """
    获取优惠配置列表
    """
    db = get_session()
    try:
        query = db.query(DiscountConfig)
        
        if store_id:
            query = query.filter(DiscountConfig.store_id == store_id)
        
        if company_id:
            query = query.filter(DiscountConfig.company_id == company_id)
        
        if is_active is not None:
            query = query.filter(DiscountConfig.is_active == is_active)
        
        configs = query.order_by(DiscountConfig.created_at.desc()).all()
        
        result = []
        for config in configs:
            result.append(DiscountConfigResponse(
                id=config.id,
                store_id=config.store_id,
                company_id=config.company_id,
                discount_type=config.discount_type,
                discount_value=float(config.discount_value),
                min_amount=float(config.min_amount) if config.min_amount else None,
                max_discount=float(config.max_discount) if config.max_discount else None,
                member_level=config.member_level,
                points_required=config.points_required,
                description=config.description,
                valid_from=config.valid_from.isoformat() if config.valid_from else None,
                valid_until=config.valid_until.isoformat() if config.valid_until else None,
                is_active=config.is_active,
                created_at=config.created_at.isoformat()
            ))
        
        return result
    finally:
        db.close()


@app.patch("/api/discount-config/{config_id}", response_model=DiscountConfigResponse)
def update_discount_config(config_id: int, config: DiscountConfigUpdate):
    """更新优惠配置"""
    db = get_session()
    try:
        db_config = db.query(DiscountConfig).filter(DiscountConfig.id == config_id).first()
        if not db_config:
            raise HTTPException(status_code=404, detail="优惠配置不存在")
        
        update_data = config.dict(exclude_unset=True)
        
        # 转换日期字符串
        if "valid_from" in update_data and update_data["valid_from"]:
            update_data["valid_from"] = datetime.fromisoformat(update_data["valid_from"])
        if "valid_until" in update_data and update_data["valid_until"]:
            update_data["valid_until"] = datetime.fromisoformat(update_data["valid_until"])
        
        for key, value in update_data.items():
            setattr(db_config, key, value)
        
        db.commit()
        db.refresh(db_config)
        
        logger.info(f"优惠配置更新成功: config_id={db_config.id}")
        
        return DiscountConfigResponse(
            id=db_config.id,
            store_id=db_config.store_id,
            company_id=db_config.company_id,
            discount_type=db_config.discount_type,
            discount_value=float(db_config.discount_value),
            min_amount=float(db_config.min_amount) if db_config.min_amount else None,
            max_discount=float(db_config.max_discount) if db_config.max_discount else None,
            member_level=db_config.member_level,
            points_required=db_config.points_required,
            description=db_config.description,
            valid_from=db_config.valid_from.isoformat() if db_config.valid_from else None,
            valid_until=db_config.valid_until.isoformat() if db_config.valid_until else None,
            is_active=db_config.is_active,
            created_at=db_config.created_at.isoformat()
        )
    except Exception as e:
        db.rollback()
        logger.error(f"更新优惠配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新优惠配置失败: {str(e)}")
    finally:
        db.close()


@app.delete("/api/discount-config/{config_id}")
def delete_discount_config(config_id: int):
    """删除优惠配置"""
    db = get_session()
    try:
        db_config = db.query(DiscountConfig).filter(DiscountConfig.id == config_id).first()
        if not db_config:
            raise HTTPException(status_code=404, detail="优惠配置不存在")
        
        db.delete(db_config)
        db.commit()
        
        logger.info(f"优惠配置删除成功: config_id={config_id}")
        
        return {"message": "优惠配置删除成功"}
    finally:
        db.close()


# ============ 应用优惠 ============

@app.post("/api/discount/apply", response_model=ApplyDiscountResponse)
def apply_discount(request: ApplyDiscountRequest, store_id: Optional[int] = None):
    """
    应用优惠
    计算订单的最优优惠
    """
    db = get_session()
    try:
        original_amount = request.order_amount
        total_discount = 0.0
        discount_info = {
            "applied_discounts": [],
            "member_discount": None,
            "points_discount": None,
            "custom_discount": None
        }
        member_info = None
        
        # 1. 会员等级折扣
        if request.member_id:
            member = db.query(Members).filter(Members.id == request.member_id).first()
            if member:
                level_info = get_member_level_info(member.level)
                member_discount_rate = level_info["discount"]
                member_discount = original_amount * (1 - member_discount_rate)
                
                if member_discount > 0:
                    discount_info["member_discount"] = {
                        "type": "member_level",
                        "level": member.level,
                        "level_name": level_info["level_name"],
                        "discount_rate": member_discount_rate,
                        "discount_amount": round(member_discount, 2)
                    }
                    total_discount += member_discount
                    discount_info["applied_discounts"].append("会员等级折扣")
                
                member_info = {
                    "member_id": member.id,
                    "level": member.level,
                    "level_name": level_info["level_name"],
                    "points": member.points
                }
        
        # 2. 积分抵扣（1积分 = 0.01元）
        if request.member_points and request.member_points > 0:
            points_discount = request.member_points * 0.01
            # 限制：积分抵扣不超过订单金额的50%
            max_points_discount = original_amount * 0.5
            if points_discount > max_points_discount:
                points_discount = max_points_discount
            
            if points_discount > 0:
                discount_info["points_discount"] = {
                    "type": "points",
                    "points_used": int(request.member_points),
                    "discount_amount": round(points_discount, 2)
                }
                total_discount += points_discount
                discount_info["applied_discounts"].append("积分抵扣")
        
        # 3. 自定义优惠配置
        if request.discount_config_id:
            discount_config = db.query(DiscountConfig).filter(
                DiscountConfig.id == request.discount_config_id,
                DiscountConfig.is_active == True
            ).first()
            
            if discount_config:
                now = datetime.now()
                
                # 检查日期有效性
                if discount_config.valid_from and now < discount_config.valid_from:
                    pass
                elif discount_config.valid_until and now > discount_config.valid_until:
                    pass
                elif discount_config.member_level and member_info and member_info["level"] < discount_config.member_level:
                    pass
                elif discount_config.points_required and (not member_info or member_info["points"] < discount_config.points_required):
                    pass
                else:
                    # 应用优惠
                    config_discount = 0.0
                    if discount_config.discount_type == "percentage":
                        config_discount = original_amount * (discount_config.discount_value / 100)
                    elif discount_config.discount_type == "fixed":
                        config_discount = discount_config.discount_value
                    elif discount_config.discount_type == "points" and request.member_points:
                        # 积分兑换优惠
                        config_discount = min(request.member_points, discount_config.points_required) * (discount_config.discount_value / 100)
                    
                    # 应用最大优惠限制
                    if discount_config.max_discount and config_discount > discount_config.max_discount:
                        config_discount = discount_config.max_discount
                    
                    if config_discount > 0:
                        discount_info["custom_discount"] = {
                            "type": discount_config.discount_type,
                            "config_id": discount_config.id,
                            "discount_value": float(discount_config.discount_value),
                            "discount_amount": round(config_discount, 2)
                        }
                        total_discount += config_discount
                        discount_info["applied_discounts"].append("自定义优惠")
        
        # 4. 查找所有有效的优惠配置（未指定特定配置时）
        if not request.discount_config_id:
            query = db.query(DiscountConfig).filter(DiscountConfig.is_active == True)
            
            if store_id:
                query = query.filter(DiscountConfig.store_id == store_id)
            
            # 获取第一个公司的ID（用于公司级别的优惠）
            first_company = db.query(Companies).first()
            if first_company:
                query = query.filter(
                    (DiscountConfig.store_id == store_id) | (DiscountConfig.company_id == first_company.id)
                )
            
            configs = query.all()
            
            for config in configs:
                now = datetime.now()
                
                # 检查日期有效性
                if config.valid_from and now < config.valid_from:
                    continue
                if config.valid_until and now > config.valid_until:
                    continue
                
                # 检查会员等级
                if config.member_level and member_info and member_info["level"] < config.member_level:
                    continue
                
                # 检查所需积分
                if config.points_required and (not member_info or member_info["points"] < config.points_required):
                    continue
                
                # 检查最低消费
                if config.min_amount and original_amount < config.min_amount:
                    continue
                
                # 应用优惠
                config_discount = 0.0
                if config.discount_type == "percentage":
                    config_discount = original_amount * (config.discount_value / 100)
                elif config.discount_type == "fixed":
                    config_discount = config.discount_value
                
                # 应用最大优惠限制
                if config.max_discount and config_discount > config.max_discount:
                    config_discount = config.max_discount
                
                if config_discount > 0:
                    discount_info["custom_discount"] = {
                        "type": config.discount_type,
                        "config_id": config.id,
                        "discount_value": float(config.discount_value),
                        "discount_amount": round(config_discount, 2)
                    }
                    total_discount += config_discount
                    discount_info["applied_discounts"].append("自动应用优惠")
                    break  # 只应用一个最优优惠
        
        # 计算最终金额
        final_amount = original_amount - total_discount
        if final_amount < 0:
            final_amount = 0
            total_discount = original_amount
        
        return ApplyDiscountResponse(
            original_amount=round(original_amount, 2),
            discount_amount=round(total_discount, 2),
            final_amount=round(final_amount, 2),
            discount_info=discount_info,
            member_info=member_info
        )
    finally:
        db.close()


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok", "message": "餐饮系统增强API服务运行正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
