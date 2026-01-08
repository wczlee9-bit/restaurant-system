"""
权限管理 API
实现系统角色权限管理，支持管理员、总公司、店铺、店员四种角色
"""
from fastapi import FastAPI, HTTPException, Depends, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from storage.database.db import get_session
from storage.database.shared.model import Users, Roles, UserRoles, Stores, Companies

# 创建 FastAPI 应用
app = FastAPI(title="扫码点餐系统 - 权限管理API", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 权限定义 ============

# 角色权限定义
ROLE_PERMISSIONS = {
    "admin": {
        "name": "管理员",
        "description": "系统超级管理员，拥有所有权限",
        "permissions": [
            "all:access",  # 全部权限
            "company:create", "company:read", "company:update", "company:delete",
            "store:create", "store:read", "store:update", "store:delete",
            "menu:create", "menu:read", "menu:update", "menu:delete",
            "order:create", "order:read", "order:update", "order:delete",
            "payment:create", "payment:read", "payment:update", "payment:delete",
            "member:create", "member:read", "member:update", "member:delete",
            "staff:create", "staff:read", "staff:update", "staff:delete",
            "inventory:create", "inventory:read", "inventory:update", "inventory:delete",
            "report:read", "report:export",
            "role:manage", "user:manage",
            "receipt:print", "receipt:config"
        ]
    },
    "company": {
        "name": "总公司",
        "description": "总公司角色，可以管理旗下所有店铺",
        "permissions": [
            "store:create", "store:read", "store:update",
            "menu:create", "menu:read", "menu:update",
            "order:read", "order:update",
            "payment:read", "payment:update",
            "member:read", "member:update",
            "staff:create", "staff:read", "staff:update", "staff:delete",
            "inventory:read", "inventory:update",
            "report:read", "report:export",
            "receipt:print", "receipt:config"
        ]
    },
    "store_manager": {
        "name": "店长",
        "description": "店铺管理员，管理本店的所有业务",
        "permissions": [
            "store:read", "store:update",
            "menu:read", "menu:update",
            "order:create", "order:read", "order:update",
            "payment:read", "payment:update",
            "member:read", "member:update",
            "staff:read", "staff:update",
            "inventory:read", "inventory:update",
            "report:read",
            "receipt:print", "receipt:config"
        ]
    },
    "staff": {
        "name": "店员",
        "description": "普通店员，处理订单和基本业务",
        "permissions": [
            "order:create", "order:read", "order:update",
            "payment:read",
            "member:read",
            "inventory:read",
            "receipt:print"
        ]
    }
}


# ============ 数据模型 ============

class RoleCreateRequest(BaseModel):
    """创建角色请求"""
    name: str = Field(..., description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")
    permissions: List[str] = Field(..., description="权限列表")


class RoleResponse(BaseModel):
    """角色响应"""
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[str]
    created_at: datetime


class UserRoleCreateRequest(BaseModel):
    """用户角色关联请求"""
    user_id: int
    role_id: int
    store_id: Optional[int] = Field(None, description="店铺ID（店员角色必填）")


class UserRoleResponse(BaseModel):
    """用户角色响应"""
    id: int
    user_id: int
    user_name: str
    role_id: int
    role_name: str
    store_id: Optional[int] = None
    created_at: datetime


class PermissionCheckRequest(BaseModel):
    """权限检查请求"""
    user_id: int
    permission: str = Field(..., description="要检查的权限")
    store_id: Optional[int] = Field(None, description="店铺ID（可选）")


# ============ 工具函数 ============

def initialize_roles(db: Session):
    """初始化系统角色"""
    initialized_count = 0
    
    for role_key, role_data in ROLE_PERMISSIONS.items():
        # 检查角色是否已存在
        existing_role = db.query(Roles).filter(Roles.name == role_data["name"]).first()
        
        if not existing_role:
            # 创建新角色
            role = Roles(
                name=role_data["name"],
                description=role_data["description"],
                permissions={"permissions": role_data["permissions"]}
            )
            db.add(role)
            initialized_count += 1
        else:
            # 更新现有角色的权限
            if existing_role.permissions != role_data["permissions"]:
                existing_role.permissions = {"permissions": role_data["permissions"]}
                existing_role.description = role_data["description"]
    
    db.commit()
    return initialized_count


def check_user_permission(db: Session, user_id: int, permission: str, store_id: Optional[int] = None) -> bool:
    """
    检查用户是否有指定权限
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        permission: 要检查的权限
        store_id: 店铺ID（用于店铺级权限检查）
    
    Returns:
        bool: 是否有权限
    """
    # 获取用户的所有角色
    user_roles = db.query(UserRoles).filter(UserRoles.user_id == user_id).all()
    
    if not user_roles:
        return False
    
    for user_role in user_roles:
        role = db.query(Roles).filter(Roles.id == user_role.role_id).first()
        if not role:
            continue
        
        # 获取角色权限
        permissions = role.permissions.get("permissions", []) if role.permissions else []
        
        # 检查是否拥有全部权限
        if "all:access" in permissions:
            return True
        
        # 检查具体权限
        if permission in permissions:
            # 如果是店铺级权限，检查店铺ID
            if store_id and user_role.store_id:
                if user_role.store_id != store_id:
                    continue
            return True
    
    return False


def get_user_stores(db: Session, user_id: int) -> List[int]:
    """
    获取用户有权限的店铺ID列表
    
    Args:
        db: 数据库会话
        user_id: 用户ID
    
    Returns:
        店铺ID列表
    """
    # 获取用户的所有角色
    user_roles = db.query(UserRoles).filter(UserRoles.user_id == user_id).all()
    
    store_ids = []
    
    for user_role in user_roles:
        role = db.query(Roles).filter(Roles.id == user_role.role_id).first()
        if not role:
            continue
        
        permissions = role.permissions.get("permissions", []) if role.permissions else []
        
        # 管理员可以访问所有店铺
        if "all:access" in permissions:
            stores = db.query(Stores).filter(Stores.is_active == True).all()
            store_ids.extend([s.id for s in stores])
            continue
        
        # 总公司可以访问所有店铺
        if "store:create" in permissions and "store:update" in permissions:
            stores = db.query(Stores).filter(Stores.is_active == True).all()
            store_ids.extend([s.id for s in stores])
            continue
        
        # 店长和店员通过Staff表获取店铺ID
        from storage.database.shared.model import Staff
        staff = db.query(Staff).filter(Staff.user_id == user_id).first()
        if staff and staff.is_active:
            store_ids.append(staff.store_id)
    
    # 去重
    return list(set(store_ids))


# ============ API 接口 ============

@app.get("/")
def root():
    """根路径"""
    return {
        "message": "扫码点餐系统 - 权限管理API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/permission/init-roles": "初始化系统角色",
            "GET /api/permission/roles": "获取所有角色",
            "POST /api/permission/role": "创建角色",
            "POST /api/permission/user-role": "分配用户角色",
            "GET /api/permission/user/{user_id}/roles": "获取用户的所有角色",
            "DELETE /api/permission/user-role/{user_role_id}": "移除用户角色",
            "POST /api/permission/check": "检查用户权限",
            "GET /api/permission/user/{user_id}/stores": "获取用户有权限的店铺列表"
        }
    }


@app.post("/api/permission/init-roles")
def init_roles():
    """
    初始化系统角色
    如果角色已存在则更新权限，不存在则创建
    """
    db = get_session()
    try:
        count = initialize_roles(db)
        return {
            "message": f"成功初始化/更新 {count} 个角色",
            "roles": list(ROLE_PERMISSIONS.keys())
        }
    finally:
        db.close()


@app.get("/api/permission/roles", response_model=List[RoleResponse])
def get_roles():
    """
    获取所有角色
    """
    db = get_session()
    try:
        roles = db.query(Roles).all()
        return [
            RoleResponse(
                id=role.id,
                name=role.name,
                description=role.description,
                permissions=role.permissions.get("permissions", []) if role.permissions else [],
                created_at=role.created_at
            )
            for role in roles
        ]
    finally:
        db.close()


@app.post("/api/permission/role", response_model=RoleResponse)
def create_role(request: RoleCreateRequest):
    """
    创建角色
    """
    db = get_session()
    try:
        # 检查角色名称是否已存在
        existing_role = db.query(Roles).filter(Roles.name == request.name).first()
        if existing_role:
            raise HTTPException(status_code=400, detail="角色名称已存在")
        
        role = Roles(
            name=request.name,
            description=request.description,
            permissions={"permissions": request.permissions}
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        
        return RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=role.permissions.get("permissions", []),
            created_at=role.created_at
        )
    finally:
        db.close()


@app.post("/api/permission/user-role", response_model=UserRoleResponse)
def assign_user_role(request: UserRoleCreateRequest):
    """
    分配用户角色
    """
    db = get_session()
    try:
        # 检查用户是否存在
        user = db.query(Users).filter(Users.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 检查角色是否存在
        role = db.query(Roles).filter(Roles.id == request.role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        # 检查是否已经分配过该角色
        existing = db.query(UserRoles).filter(
            UserRoles.user_id == request.user_id,
            UserRoles.role_id == request.role_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户已分配该角色")
        
        # 店员角色必须有店铺ID，需要创建Staff记录
        if role.name == "店员":
            if not request.store_id:
                raise HTTPException(status_code=400, detail="店员角色必须指定店铺ID")
            
            # 检查店铺是否存在
            store = db.query(Stores).filter(Stores.id == request.store_id).first()
            if not store:
                raise HTTPException(status_code=404, detail="店铺不存在")
            
            # 检查是否已有Staff记录
            from storage.database.shared.model import Staff
            existing_staff = db.query(Staff).filter(
                Staff.user_id == request.user_id,
                Staff.store_id == request.store_id
            ).first()
            
            if not existing_staff:
                # 创建Staff记录
                staff = Staff(
                    user_id=request.user_id,
                    store_id=request.store_id,
                    position="店员",
                    is_active=True
                )
                db.add(staff)
        
        user_role = UserRoles(
            user_id=request.user_id,
            role_id=request.role_id
        )
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        
        # 获取店铺ID
        store_id = request.store_id
        if not store_id:
            from storage.database.shared.model import Staff
            staff = db.query(Staff).filter(Staff.user_id == request.user_id).first()
            if staff:
                store_id = staff.store_id
        
        return UserRoleResponse(
            id=user_role.id,
            user_id=user_role.user_id,
            user_name=user.name,
            role_id=user_role.role_id,
            role_name=role.name,
            store_id=store_id,
            created_at=user_role.created_at
        )
    finally:
        db.close()


@app.get("/api/permission/user/{user_id}/roles", response_model=List[UserRoleResponse])
def get_user_roles(user_id: int):
    """
    获取用户的所有角色
    """
    db = get_session()
    try:
        # 检查用户是否存在
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        user_roles = db.query(UserRoles).filter(UserRoles.user_id == user_id).all()
        
        result = []
        for ur in user_roles:
            role = db.query(Roles).filter(Roles.id == ur.role_id).first()
            if role:
                # 查找关联的店铺ID（通过Staff表）
                store_id = None
                from storage.database.shared.model import Staff
                staff = db.query(Staff).filter(Staff.user_id == ur.user_id).first()
                if staff:
                    store_id = staff.store_id
                
                result.append(UserRoleResponse(
                    id=ur.id,
                    user_id=ur.user_id,
                    user_name=user.name,
                    role_id=ur.role_id,
                    role_name=role.name,
                    store_id=store_id,
                    created_at=ur.created_at
                ))
        
        return result
    finally:
        db.close()


@app.delete("/api/permission/user-role/{user_role_id}")
def remove_user_role(user_role_id: int):
    """
    移除用户角色
    """
    db = get_session()
    try:
        user_role = db.query(UserRoles).filter(UserRoles.id == user_role_id).first()
        if not user_role:
            raise HTTPException(status_code=404, detail="用户角色关联不存在")
        
        db.delete(user_role)
        db.commit()
        
        return {"message": "成功移除用户角色"}
    finally:
        db.close()


@app.post("/api/permission/check")
def check_permission(request: PermissionCheckRequest):
    """
    检查用户是否有指定权限
    """
    db = get_session()
    try:
        has_permission = check_user_permission(
            db,
            request.user_id,
            request.permission,
            request.store_id
        )
        
        return {
            "has_permission": has_permission,
            "user_id": request.user_id,
            "permission": request.permission
        }
    finally:
        db.close()


@app.get("/api/permission/user/{user_id}/stores")
def get_user_accessible_stores(user_id: int):
    """
    获取用户有权限的店铺列表
    """
    db = get_session()
    try:
        # 检查用户是否存在
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        store_ids = get_user_stores(db, user_id)
        
        # 获取店铺详细信息
        stores = db.query(Stores).filter(Stores.id.in_(store_ids)).all()
        
        return [
            {
                "id": store.id,
                "name": store.name,
                "address": store.address,
                "is_active": store.is_active
            }
            for store in stores
        ]
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
