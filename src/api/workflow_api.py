"""
订单流程配置 API
用于管理店铺的工作流程配置
"""
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from storage.database.db import get_session
from storage.database.shared.model import Stores, WorkflowConfig

router = APIRouter(prefix="/api/workflow-config", tags=["订单流程配置"])


# ============ 数据模型 ============

class WorkflowConfigResponse(BaseModel):
    """工作流程配置响应"""
    id: int
    role: str
    status: str
    action_mode: str
    is_enabled: bool
    description: Optional[str] = None

class WorkflowConfigUpdate(BaseModel):
    """更新工作流程配置请求"""
    action_mode: Optional[str] = None
    is_enabled: Optional[bool] = None

class WorkflowConfigBulkUpdate(BaseModel):
    """批量更新配置"""
    configs: List[dict]  # [{"id": 1, "action_mode": "per_item", "is_enabled": True}, ...]


# ============ 工具函数 ============

ROLE_NAMES = {
    'kitchen': '厨师',
    'waiter': '传菜员',
    'cashier': '收银员',
    'manager': '店长'
}

STATUS_NAMES = {
    'pending': '待确认',
    'preparing': '制作中',
    'ready': '待传菜',
    'serving': '上菜中',
    'completed': '已完成'
}

ACTION_MODE_NAMES = {
    'per_item': '逐项确认',
    'per_order': '订单确认',
    'skip': '自动跳过',
    'ignore': '忽略不显示'
}

DEFAULT_CONFIGS = [
    {
        'role': 'kitchen',
        'status': 'pending',
        'action_mode': 'per_item',
        'is_enabled': True
    },
    {
        'role': 'kitchen',
        'status': 'preparing',
        'action_mode': 'per_item',
        'is_enabled': True
    },
    {
        'role': 'waiter',
        'status': 'ready',
        'action_mode': 'per_order',
        'is_enabled': True
    },
    {
        'role': 'waiter',
        'status': 'serving',
        'action_mode': 'per_order',
        'is_enabled': True
    },
    {
        'role': 'cashier',
        'status': 'completed',
        'action_mode': 'skip',
        'is_enabled': False
    },
    {
        'role': 'manager',
        'status': 'completed',
        'action_mode': 'skip',
        'is_enabled': True
    }
]


# ============ API 接口 ============

@router.get("/")
def get_workflow_configs(
    store_id: Optional[int] = Query(None, description="店铺ID"),
    role: Optional[str] = Query(None, description="角色")
):
    """
    获取工作流程配置列表
    """
    db = get_session()
    try:
        # 如果没有指定 store_id，获取第一个店铺
        if not store_id:
            first_store = db.query(Stores).first()
            if first_store:
                store_id = first_store.id

        query = db.query(WorkflowConfig).filter(WorkflowConfig.store_id == store_id)

        if role:
            query = query.filter(WorkflowConfig.role == role)

        configs = query.all()

        return [
            {
                "id": cfg.id,
                "role": cfg.role,
                "role_name": ROLE_NAMES.get(cfg.role, cfg.role),
                "status": cfg.status,
                "status_name": STATUS_NAMES.get(cfg.status, cfg.status),
                "action_mode": cfg.action_mode,
                "action_mode_name": ACTION_MODE_NAMES.get(cfg.action_mode, cfg.action_mode),
                "is_enabled": cfg.is_enabled,
                "created_at": cfg.created_at.isoformat() if cfg.created_at else None,
                "updated_at": cfg.updated_at.isoformat() if cfg.updated_at else None
            }
            for cfg in configs
        ]
    finally:
        db.close()


@router.get("/by-role/{role}")
def get_workflow_config_by_role(
    role: str,
    store_id: Optional[int] = Query(None, description="店铺ID")
):
    """
    获取指定角色的所有配置
    """
    db = get_session()
    try:
        # 如果没有指定 store_id，获取第一个店铺
        if not store_id:
            first_store = db.query(Stores).first()
            if first_store:
                store_id = first_store.id

        configs = db.query(WorkflowConfig).filter(
            WorkflowConfig.store_id == store_id,
            WorkflowConfig.role == role,
            WorkflowConfig.is_enabled == True
        ).all()

        return [
            {
                "id": cfg.id,
                "status": cfg.status,
                "action_mode": cfg.action_mode,
                "is_enabled": cfg.is_enabled
            }
            for cfg in configs
        ]
    finally:
        db.close()


@router.patch("/{config_id}")
def update_workflow_config(
    config_id: int,
    update_data: WorkflowConfigUpdate
):
    """
    更新单个工作流程配置
    """
    db = get_session()
    try:
        config = db.query(WorkflowConfig).filter(WorkflowConfig.id == config_id).first()
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")

        # 更新字段
        if update_data.action_mode is not None:
            config.action_mode = update_data.action_mode
        if update_data.is_enabled is not None:
            config.is_enabled = update_data.is_enabled

        config.updated_at = datetime.now()

        db.commit()
        db.refresh(config)

        return {
            "id": config.id,
            "role": config.role,
            "status": config.status,
            "action_mode": config.action_mode,
            "is_enabled": config.is_enabled
        }
    finally:
        db.close()


@router.post("/bulk-update")
def bulk_update_workflow_configs(bulk_data: WorkflowConfigBulkUpdate):
    """
    批量更新工作流程配置
    """
    db = get_session()
    try:
        updated_count = 0

        for item in bulk_data.configs:
            config_id = item.get('id')
            if not config_id:
                continue

            config = db.query(WorkflowConfig).filter(WorkflowConfig.id == config_id).first()
            if config:
                if 'action_mode' in item:
                    config.action_mode = item['action_mode']
                if 'is_enabled' in item:
                    config.is_enabled = item['is_enabled']

                config.updated_at = datetime.now()
                updated_count += 1

        db.commit()

        return {
            "message": f"成功更新 {updated_count} 条配置",
            "updated_count": updated_count
        }
    finally:
        db.close()


@router.post("/reset-defaults")
def reset_to_defaults(store_id: Optional[int] = Query(None, description="店铺ID")):
    """
    重置为默认配置
    """
    db = get_session()
    try:
        # 如果没有指定 store_id，获取第一个店铺
        if not store_id:
            first_store = db.query(Stores).first()
            if first_store:
                store_id = first_store.id

        # 删除现有配置
        db.query(WorkflowConfig).filter(WorkflowConfig.store_id == store_id).delete()

        # 创建默认配置
        for default_cfg in DEFAULT_CONFIGS:
            config = WorkflowConfig(
                store_id=store_id,
                **default_cfg
            )
            db.add(config)

        db.commit()

        return {
            "message": "已重置为默认配置",
            "store_id": store_id
        }
    finally:
        db.close()


@router.get("/action-mode/{role}/{status}")
def get_action_mode(
    role: str,
    status: str,
    store_id: Optional[int] = Query(None, description="店铺ID")
):
    """
    获取指定角色和状态的操作模式
    用于前端判断如何处理该状态
    """
    db = get_session()
    try:
        # 如果没有指定 store_id，获取第一个店铺
        if not store_id:
            first_store = db.query(Stores).first()
            if first_store:
                store_id = first_store.id

        config = db.query(WorkflowConfig).filter(
            WorkflowConfig.store_id == store_id,
            WorkflowConfig.role == role,
            WorkflowConfig.status == status
        ).first()

        if not config or not config.is_enabled:
            # 如果没有配置或未启用，返回默认行为
            return {
                "action_mode": "skip",  # 默认跳过
                "is_enabled": False
            }

        return {
            "action_mode": config.action_mode,
            "is_enabled": config.is_enabled
        }
    finally:
        db.close()
