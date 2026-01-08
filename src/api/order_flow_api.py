"""
订单流程配置 API
支持动态角色管理和灵活的功能分配
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.storage.database.shared.model import RoleConfig, OrderFlowConfig, Stores
from src.storage.database.db import get_session

def get_db():
    """获取数据库会话"""
    db = get_session()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/order-flow", tags=["订单流程配置"])


# ============ Pydantic 模型 ============

class RoleConfigCreate(BaseModel):
    """创建角色配置"""
    角色名称: str
    角色描述: Optional[str] = None
    是否启用: bool = True
    排序: int = 0


class RoleConfigUpdate(BaseModel):
    """更新角色配置"""
    角色名称: Optional[str] = None
    角色描述: Optional[str] = None
    是否启用: Optional[bool] = None
    排序: Optional[int] = None


class RoleConfigResponse(BaseModel):
    """角色配置响应"""
    id: int
    店铺ID: int
    角色名称: str
    角色描述: Optional[str]
    是否启用: bool
    排序: int
    创建时间: datetime
    更新时间: Optional[datetime]

    class Config:
        from_attributes = True


class OrderFlowConfigCreate(BaseModel):
    """创建订单流程配置"""
    角色名称: str
    订单状态: str
    操作方式: str = "逐项确认"
    是否启用: bool = True
    排序: int = 0


class OrderFlowConfigUpdate(BaseModel):
    """更新订单流程配置"""
    角色名称: Optional[str] = None
    订单状态: Optional[str] = None
    操作方式: Optional[str] = None
    是否启用: Optional[bool] = None
    排序: Optional[int] = None


class OrderFlowConfigResponse(BaseModel):
    """订单流程配置响应"""
    id: int
    店铺ID: int
    角色名称: str
    订单状态: str
    操作方式: str
    是否启用: bool
    排序: int
    创建时间: datetime
    更新时间: Optional[datetime]

    class Config:
        from_attributes = True


class StoreConfigResponse(BaseModel):
    """店铺完整配置响应"""
    店铺ID: int
    店铺名称: str
    角色列表: List[RoleConfigResponse]
    流程配置: List[OrderFlowConfigResponse]


# ============ 角色管理 API ============

@router.get("/stores/{store_id}/roles", response_model=List[RoleConfigResponse])
def get_roles(store_id: int, db: Session = Depends(get_db)):
    """获取店铺的所有角色配置"""
    # 验证店铺存在
    store = db.query(Stores).filter(Stores.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    roles = db.query(RoleConfig).filter(RoleConfig.店铺ID == store_id).order_by(RoleConfig.排序).all()
    return roles


@router.post("/stores/{store_id}/roles", response_model=RoleConfigResponse)
def create_role(store_id: int, role: RoleConfigCreate, db: Session = Depends(get_db)):
    """创建新角色"""
    # 验证店铺存在
    store = db.query(Stores).filter(Stores.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    # 检查角色名是否已存在
    existing = db.query(RoleConfig).filter(
        RoleConfig.店铺ID == store_id,
        RoleConfig.角色名称 == role.角色名称
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"角色 '{role.角色名称}' 已存在")
    
    db_role = RoleConfig(店铺ID=store_id, **role.model_dump())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


@router.put("/stores/{store_id}/roles/{role_id}", response_model=RoleConfigResponse)
def update_role(store_id: int, role_id: int, role: RoleConfigUpdate, db: Session = Depends(get_db)):
    """更新角色配置"""
    db_role = db.query(RoleConfig).filter(
        RoleConfig.id == role_id,
        RoleConfig.店铺ID == store_id
    ).first()
    
    if not db_role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 如果修改角色名，检查是否冲突
    if role.角色名称 and role.角色名称 != db_role.角色名称:
        existing = db.query(RoleConfig).filter(
            RoleConfig.店铺ID == store_id,
            RoleConfig.角色名称 == role.角色名称,
            RoleConfig.id != role_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"角色名称 '{role.角色名称}' 已存在")
    
    update_data = role.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_role, key, value)
    
    db_role.更新时间 = datetime.now()
    db.commit()
    db.refresh(db_role)
    return db_role


@router.delete("/stores/{store_id}/roles/{role_id}")
def delete_role(store_id: int, role_id: int, db: Session = Depends(get_db)):
    """删除角色"""
    db_role = db.query(RoleConfig).filter(
        RoleConfig.id == role_id,
        RoleConfig.店铺ID == store_id
    ).first()
    
    if not db_role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 删除角色相关的所有流程配置
    db.query(OrderFlowConfig).filter(
        OrderFlowConfig.店铺ID == store_id,
        OrderFlowConfig.角色名称 == db_role.角色名称
    ).delete()
    
    db.delete(db_role)
    db.commit()
    return {"message": "角色删除成功"}


# ============ 订单流程配置 API ============

@router.get("/stores/{store_id}/flow-configs", response_model=List[OrderFlowConfigResponse])
def get_flow_configs(
    store_id: int,
    角色名称: Optional[str] = None,
    订单状态: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取店铺的订单流程配置"""
    # 验证店铺存在
    store = db.query(Stores).filter(Stores.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    query = db.query(OrderFlowConfig).filter(OrderFlowConfig.店铺ID == store_id)
    
    if 角色名称:
        query = query.filter(OrderFlowConfig.角色名称 == 角色名称)
    
    if 订单状态:
        query = query.filter(OrderFlowConfig.订单状态 == 订单状态)
    
    configs = query.order_by(OrderFlowConfig.排序).all()
    return configs


@router.get("/stores/{store_id}/flow-configs/grouped")
def get_flow_configs_grouped(store_id: int, db: Session = Depends(get_db)):
    """按角色分组获取流程配置"""
    # 验证店铺存在
    store = db.query(Stores).filter(Stores.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    configs = db.query(OrderFlowConfig).filter(
        OrderFlowConfig.店铺ID == store_id
    ).order_by(OrderFlowConfig.角色名称, OrderFlowConfig.排序).all()
    
    # 按角色分组
    grouped = {}
    for config in configs:
        if config.角色名称 not in grouped:
            grouped[config.角色名称] = []
        grouped[config.角色名称].append(OrderFlowConfigResponse.model_validate(config))
    
    return grouped


@router.post("/stores/{store_id}/flow-configs", response_model=OrderFlowConfigResponse)
def create_flow_config(store_id: int, config: OrderFlowConfigCreate, db: Session = Depends(get_db)):
    """创建订单流程配置"""
    # 验证店铺存在
    store = db.query(Stores).filter(Stores.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    # 验证角色存在
    role = db.query(RoleConfig).filter(
        RoleConfig.店铺ID == store_id,
        RoleConfig.角色名称 == config.角色名称
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail=f"角色 '{config.角色名称}' 不存在")
    
    # 检查配置是否已存在
    existing = db.query(OrderFlowConfig).filter(
        OrderFlowConfig.店铺ID == store_id,
        OrderFlowConfig.角色名称 == config.角色名称,
        OrderFlowConfig.订单状态 == config.订单状态
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"该角色的 '{config.订单状态}' 配置已存在")
    
    db_config = OrderFlowConfig(店铺ID=store_id, **config.model_dump())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


@router.put("/stores/{store_id}/flow-configs/{config_id}", response_model=OrderFlowConfigResponse)
def update_flow_config(
    store_id: int,
    config_id: int,
    config: OrderFlowConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新订单流程配置"""
    db_config = db.query(OrderFlowConfig).filter(
        OrderFlowConfig.id == config_id,
        OrderFlowConfig.店铺ID == store_id
    ).first()
    
    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 如果修改角色名或状态，检查是否冲突
    if config.角色名称 or config.订单状态:
        new_role_name = config.角色名称 if config.角色名称 else db_config.角色名称
        new_status = config.订单状态 if config.订单状态 else db_config.订单状态
        
        existing = db.query(OrderFlowConfig).filter(
            OrderFlowConfig.店铺ID == store_id,
            OrderFlowConfig.角色名称 == new_role_name,
            OrderFlowConfig.订单状态 == new_status,
            OrderFlowConfig.id != config_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="该角色的该状态配置已存在")
    
    update_data = config.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_config, key, value)
    
    db_config.更新时间 = datetime.now()
    db.commit()
    db.refresh(db_config)
    return db_config


@router.delete("/stores/{store_id}/flow-configs/{config_id}")
def delete_flow_config(store_id: int, config_id: int, db: Session = Depends(get_db)):
    """删除订单流程配置"""
    db_config = db.query(OrderFlowConfig).filter(
        OrderFlowConfig.id == config_id,
        OrderFlowConfig.店铺ID == store_id
    ).first()
    
    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    db.delete(db_config)
    db.commit()
    return {"message": "配置删除成功"}


# ============ 批量操作 API ============

@router.post("/stores/{store_id}/flow-configs/batch")
def batch_update_flow_configs(
    store_id: int,
    configs: List[OrderFlowConfigUpdate],
    db: Session = Depends(get_db)
):
    """批量更新流程配置"""
    # 验证店铺存在
    store = db.query(Stores).filter(Stores.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    updated_count = 0
    for config_data in configs:
        if not config_data.id:
            continue
        
        db_config = db.query(OrderFlowConfig).filter(
            OrderFlowConfig.id == config_data.id,
            OrderFlowConfig.店铺ID == store_id
        ).first()
        
        if db_config:
            update_data = config_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_config, key, value)
            db_config.更新时间 = datetime.now()
            updated_count += 1
    
    db.commit()
    return {"message": f"成功更新 {updated_count} 个配置"}


@router.post("/stores/{store_id}/reset")
def reset_to_default(store_id: int, db: Session = Depends(get_db)):
    """重置店铺的流程配置为默认值"""
    # 验证店铺存在
    store = db.query(Stores).filter(Stores.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    # 删除现有配置
    db.query(OrderFlowConfig).filter(OrderFlowConfig.店铺ID == store_id).delete()
    
    # 重新创建默认配置
    default_configs = [
        {"角色名称": "厨师", "订单状态": "待确认", "操作方式": "逐项确认", "是否启用": True, "排序": 1},
        {"角色名称": "厨师", "订单状态": "制作中", "操作方式": "订单确认", "是否启用": True, "排序": 2},
        {"角色名称": "传菜员", "订单状态": "待传菜", "操作方式": "订单确认", "是否启用": True, "排序": 3},
        {"角色名称": "传菜员", "订单状态": "上菜中", "操作方式": "逐项确认", "是否启用": True, "排序": 4},
        {"角色名称": "收银员", "订单状态": "已完成", "操作方式": "订单确认", "是否启用": True, "排序": 5},
        {"角色名称": "店长", "订单状态": "待确认", "操作方式": "忽略不显示", "是否启用": True, "排序": 10},
        {"角色名称": "店长", "订单状态": "制作中", "操作方式": "忽略不显示", "是否启用": True, "排序": 11},
        {"角色名称": "店长", "订单状态": "待传菜", "操作方式": "忽略不显示", "是否启用": True, "排序": 12},
        {"角色名称": "店长", "订单状态": "上菜中", "操作方式": "忽略不显示", "是否启用": True, "排序": 13},
        {"角色名称": "店长", "订单状态": "已完成", "操作方式": "忽略不显示", "是否启用": True, "排序": 14},
    ]
    
    for config_data in default_configs:
        db_config = OrderFlowConfig(店铺ID=store_id, **config_data)
        db.add(db_config)
    
    db.commit()
    return {"message": "已重置为默认配置"}


@router.get("/stores/{store_id}/full-config", response_model=StoreConfigResponse)
def get_full_store_config(store_id: int, db: Session = Depends(get_db)):
    """获取店铺的完整配置（角色 + 流程配置）"""
    # 验证店铺存在
    store = db.query(Stores).filter(Stores.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    roles = db.query(RoleConfig).filter(
        RoleConfig.店铺ID == store_id
    ).order_by(RoleConfig.排序).all()
    
    flow_configs = db.query(OrderFlowConfig).filter(
        OrderFlowConfig.店铺ID == store_id
    ).order_by(OrderFlowConfig.排序).all()
    
    return StoreConfigResponse(
        店铺ID=store.id,
        店铺名称=store.名称,
        角色列表=[RoleConfigResponse.model_validate(r) for r in roles],
        流程配置=[OrderFlowConfigResponse.model_validate(c) for c in flow_configs]
    )


# ============ 获取角色对应的订单状态 API ============

@router.get("/stores/{store_id}/roles/{role_name}/statuses")
def get_role_order_statuses(store_id: int, role_name: str, db: Session = Depends(get_db)):
    """获取指定角色需要处理的所有订单状态"""
    # 验证店铺存在
    store = db.query(Stores).filter(Stores.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    configs = db.query(OrderFlowConfig).filter(
        OrderFlowConfig.店铺ID == store_id,
        OrderFlowConfig.角色名称 == role_name,
        OrderFlowConfig.是否启用 == True
    ).all()
    
    return {
        "角色名称": role_name,
        "订单状态列表": [
            {
                "订单状态": c.订单状态,
                "操作方式": c.操作方式
            }
            for c in configs
        ]
    }
