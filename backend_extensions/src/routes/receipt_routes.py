from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from storage.database.db_config import get_db
from storage.database.models import Order, OrderItem
from datetime import datetime
from routes.auth_routes import get_current_active_user

router = APIRouter(prefix="/api/receipt", tags=["小票打印"])

class ReceiptData(BaseModel):
    order_id: int
    print_kitchen: bool = False  # 是否打印厨房联
    print_customer: bool = True  # 是否打印顾客联

def generate_receipt_text(order: dict, receipt_type: str = "customer") -> str:
    """生成小票文本"""
    
    lines = []
    
    if receipt_type == "customer":
        # 顾客联
        lines.append("=" * 32)
        lines.append("      餐厅小票".center(28))
        lines.append("=" * 32)
        lines.append("")
        lines.append(f"订单号: {order['order_number']}")
        lines.append(f"桌号:   {order['table_id']} 号桌")
        lines.append(f"时间:   {order['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("-" * 32)
        lines.append("商品         数量    金额")
        lines.append("-" * 32)
        
        for item in order['items']:
            name = item['name'][:12] if len(item['name']) > 12 else item['name']
            lines.append(f"{name:<12}  {item['quantity']:>2}    ¥{item['subtotal']:>6.2f}")
        
        lines.append("-" * 32)
        lines.append(f"总计:                     ¥{order['total_amount']:>6.2f}")
        lines.append(f"支付: {'已支付' if order['payment_status'] == 'paid' else '未支付'}")
        lines.append("")
        lines.append("谢谢惠顾！")
        lines.append("=" * 32)
    
    elif receipt_type == "kitchen":
        # 厨房联
        lines.append("=" * 32)
        lines.append("      厨房订单".center(28))
        lines.append("=" * 32)
        lines.append("")
        lines.append(f"订单号: {order['order_number']}")
        lines.append(f"桌号:   {order['table_id']} 号桌")
        lines.append(f"时间:   {order['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"状态:   {order['status']}")
        lines.append("")
        lines.append("-" * 32)
        lines.append("商品         数量    备注")
        lines.append("-" * 32)
        
        for item in order['items']:
            name = item['name'][:12] if len(item['name']) > 12 else item['name']
            note = item['special_instructions'][:8] if item.get('special_instructions') else ""
            lines.append(f"{name:<12}  {item['quantity']:>2}    {note}")
        
        lines.append("")
        if order.get('special_requirements'):
            lines.append(f"特殊要求: {order['special_requirements']}")
        
        lines.append("")
        lines.append("=" * 32)
    
    return "\n".join(lines)

@router.post("/print")
async def print_receipt(
    data: ReceiptData,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """打印小票（模拟）"""
    
    # 获取订单详情
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    
    # 构造订单数据
    order_data = {
        "id": order.id,
        "order_number": order.order_number,
        "table_id": order.table_id,
        "total_amount": order.total_amount,
        "payment_status": order.payment_status,
        "status": order.status,
        "created_at": order.created_at,
        "special_requirements": order.special_requirements,
        "items": [
            {
                "name": f"菜品{item.menu_item_id}",  # 实际应查询菜品名称
                "quantity": item.quantity,
                "subtotal": item.subtotal,
                "special_instructions": item.special_instructions
            }
            for item in order_items
        ]
    }
    
    result = {
        "order_id": order.id,
        "order_number": order.order_number,
        "timestamp": datetime.now().isoformat()
    }
    
    # 生成小票文本
    if data.print_customer:
        result["customer_receipt"] = generate_receipt_text(order_data, "customer")
    
    if data.print_kitchen:
        result["kitchen_receipt"] = generate_receipt_text(order_data, "kitchen")
    
    # 在实际应用中，这里会调用打印机驱动
    # 例如：使用 escpos 库打印到 USB 打印机
    # 或者发送到网络打印机
    
    return {
        "success": True,
        "message": "小票打印成功（模拟）",
        "data": result
    }

@router.get("/{order_id}/preview")
def preview_receipt(
    order_id: int,
    receipt_type: str = "customer",
    db: Session = Depends(get_db)
):
    """预览小票"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    
    order_data = {
        "order_number": order.order_number,
        "table_id": order.table_id,
        "total_amount": order.total_amount,
        "payment_status": order.payment_status,
        "status": order.status,
        "created_at": order.created_at,
        "special_requirements": order.special_requirements,
        "items": [
            {
                "name": f"菜品{item.menu_item_id}",
                "quantity": item.quantity,
                "subtotal": item.subtotal,
                "special_instructions": item.special_instructions
            }
            for item in order_items
        ]
    }
    
    receipt_text = generate_receipt_text(order_data, receipt_type)
    
    return {
        "order_id": order.id,
        "receipt_type": receipt_type,
        "receipt_text": receipt_text,
        "html": receipt_text.replace("\n", "<br>")
    }

@router.post("/batch-print")
async def batch_print_receipts(
    order_ids: list[int],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """批量打印小票"""
    
    results = []
    
    for order_id in order_ids:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
            
            order_data = {
                "order_number": order.order_number,
                "table_id": order.table_id,
                "total_amount": order.total_amount,
                "payment_status": order.payment_status,
                "status": order.status,
                "created_at": order.created_at,
                "special_requirements": order.special_requirements,
                "items": [
                    {
                        "name": f"菜品{item.menu_item_id}",
                        "quantity": item.quantity,
                        "subtotal": item.subtotal
                    }
                    for item in order_items
                ]
            }
            
            receipt_text = generate_receipt_text(order_data, "customer")
            results.append({
                "order_id": order.id,
                "success": True,
                "receipt": receipt_text
            })
        else:
            results.append({
                "order_id": order_id,
                "success": False,
                "error": "订单不存在"
            })
    
    return {
        "success": True,
        "message": f"批量打印完成，共 {len(results)} 张小票",
        "results": results
    }
