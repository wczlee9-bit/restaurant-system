from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from storage.database.db_config import get_db
from storage.database.models import MenuItem
from typing import Optional
from routes.auth_routes import get_current_active_user

router = APIRouter(prefix="/api/menu", tags=["库存管理"])

class StockUpdate(BaseModel):
    stock: int
    low_stock_threshold: Optional[int] = 10

class StockResponse(BaseModel):
    id: int
    name: str
    stock: int
    low_stock_threshold: int
    is_low_stock: bool
    status: str
    
    class Config:
        from_attributes = True

@router.get("/{item_id}/stock", response_model=StockResponse)
def get_item_stock(
    item_id: int,
    db: Session = Depends(get_db)
):
    """获取菜品库存信息"""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="菜品不存在")
    
    return StockResponse(
        id=item.id,
        name=item.name,
        stock=item.stock,
        low_stock_threshold=getattr(item, 'low_stock_threshold', 10),
        is_low_stock=item.stock <= getattr(item, 'low_stock_threshold', 10),
        status="低库存" if item.stock <= getattr(item, 'low_stock_threshold', 10) else "正常"
    )

@router.put("/{item_id}/stock")
def update_item_stock(
    item_id: int,
    data: StockUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """更新菜品库存"""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="菜品不存在")
    
    if data.stock < 0:
        raise HTTPException(status_code=400, detail="库存不能为负数")
    
    item.stock = data.stock
    
    # 如果有 low_stock_threshold 字段，也更新
    if hasattr(item, 'low_stock_threshold'):
        item.low_stock_threshold = data.low_stock_threshold
    
    db.commit()
    
    is_low = item.stock <= getattr(item, 'low_stock_threshold', 10)
    
    return {
        "message": "库存更新成功",
        "stock": item.stock,
        "is_low_stock": is_low
    }

@router.get("/low-stock")
def get_low_stock_items(
    store_id: int = 1,
    threshold: int = 10,
    db: Session = Depends(get_db)
):
    """获取库存不足的菜品列表"""
    items = db.query(MenuItem).filter(
        MenuItem.store_id == store_id,
        MenuItem.stock <= threshold
    ).order_by(MenuItem.stock.asc()).all()
    
    return [
        {
            "id": item.id,
            "name": item.name,
            "stock": item.stock,
            "price": item.price
        }
        for item in items
    ]

@router.post("/{item_id}/restock")
def restock_item(
    item_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """补货"""
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="补货数量必须大于0")
    
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="菜品不存在")
    
    old_stock = item.stock
    item.stock += quantity
    
    db.commit()
    
    return {
        "message": "补货成功",
        "old_stock": old_stock,
        "new_stock": item.stock,
        "added": quantity
    }

@router.get("/stock-summary")
def get_stock_summary(
    store_id: int = 1,
    db: Session = Depends(get_db)
):
    """获取库存汇总"""
    total_items = db.query(MenuItem).filter(MenuItem.store_id == store_id).count()
    low_stock_items = db.query(MenuItem).filter(
        MenuItem.store_id == store_id,
        MenuItem.stock <= 10
    ).count()
    out_of_stock = db.query(MenuItem).filter(
        MenuItem.store_id == store_id,
        MenuItem.stock == 0
    ).count()
    
    return {
        "total_items": total_items,
        "in_stock": total_items - out_of_stock,
        "low_stock": low_stock_items,
        "out_of_stock": out_of_stock
    }
