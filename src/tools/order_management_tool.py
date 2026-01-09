"""
订单管理工具 - 支持订单查询、状态更新等操作
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from langchain.tools import tool
from storage.database.db import get_session
from storage.database.shared.model import Orders, OrderItems, OrderStatusLogs, Payments
from datetime import datetime, timedelta
from pydantic import BaseModel, Field


class OrderQueryParams(BaseModel):
    """订单查询参数"""
    store_id: Optional[int] = None
    table_id: Optional[int] = None
    order_status: Optional[str] = None
    payment_status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@tool
def query_orders(params: str, runtime=None) -> str:
    """
    查询订单信息，支持多种过滤条件
    
    Args:
        params: JSON格式的查询参数，例如：
            {"store_id": 1, "order_status": "pending", "start_date": "2024-01-01"}
            支持的参数：store_id, table_id, order_status, payment_status, start_date, end_date
    
    Returns:
        返回订单列表的JSON字符串，包含订单详情和订单项
    """
    try:
        import json
        from sqlalchemy import and_
        
        # 解析参数
        query_params = json.loads(params) if isinstance(params, str) else params
        
        db = get_session()
        try:
            query = db.query(Orders)
            
            # 应用过滤条件
            filters = []
            if query_params.get("store_id"):
                filters.append(Orders.store_id == query_params["store_id"])
            if query_params.get("table_id"):
                filters.append(Orders.table_id == query_params["table_id"])
            if query_params.get("order_status"):
                filters.append(Orders.order_status == query_params["order_status"])
            if query_params.get("payment_status"):
                filters.append(Orders.payment_status == query_params["payment_status"])
            if query_params.get("start_date"):
                start_date = datetime.strptime(query_params["start_date"], "%Y-%m-%d")
                filters.append(Orders.created_at >= start_date)
            if query_params.get("end_date"):
                end_date = datetime.strptime(query_params["end_date"], "%Y-%m-%d") + timedelta(days=1)
                filters.append(Orders.created_at < end_date)
            
            if filters:
                query = query.filter(and_(*filters))
            
            # 限制返回数量，避免数据过多
            orders = query.order_by(Orders.created_at.desc()).limit(100).all()
            
            # 构建返回结果
            result = []
            for order in orders:
                order_data = {
                    "id": order.id,
                    "order_number": order.order_number,
                    "store_id": order.store_id,
                    "table_id": order.table_id,
                    "customer_name": order.customer_name,
                    "customer_phone": order.customer_phone,
                    "total_amount": order.total_amount,
                    "discount_amount": order.discount_amount,
                    "final_amount": order.final_amount,
                    "payment_status": order.payment_status,
                    "payment_method": order.payment_method,
                    "payment_time": order.payment_time.isoformat() if order.payment_time else None,
                    "order_status": order.order_status,
                    "special_instructions": order.special_instructions,
                    "created_at": order.created_at.isoformat(),
                    "updated_at": order.updated_at.isoformat() if order.updated_at else None,
                    "items": []
                }
                
                # 获取订单项
                for item in order.order_items:
                    order_data["items"].append({
                        "id": item.id,
                        "menu_item_name": item.menu_item_name,
                        "menu_item_price": item.menu_item_price,
                        "quantity": item.quantity,
                        "subtotal": item.subtotal,
                        "special_instructions": item.special_instructions,
                        "status": item.status
                    })
                
                result.append(order_data)
            
            return json.dumps({
                "success": True,
                "count": len(result),
                "orders": result
            }, ensure_ascii=False, indent=2)
            
        finally:
            db.close()
            
    except Exception as e:
        import traceback
        return json.dumps({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }, ensure_ascii=False, indent=2)


@tool
def update_order_status(order_id: int, new_status: str, operator_id: Optional[int] = None, notes: Optional[str] = None, runtime=None) -> str:
    """
    更新订单状态，并记录状态变更日志
    
    Args:
        order_id: 订单ID
        new_status: 新状态（pending, confirmed, preparing, ready, serving, completed, cancelled）
        operator_id: 操作人ID（可选）
        notes: 备注（可选）
    
    Returns:
        返回操作结果的JSON字符串
    """
    import json
    
    try:
        db = get_session()
        try:
            # 查询订单
            order = db.query(Orders).filter(Orders.id == order_id).first()
            if not order:
                return json.dumps({
                    "success": False,
                    "error": f"订单ID {order_id} 不存在"
                }, ensure_ascii=False)
            
            # 记录旧状态
            old_status = order.order_status
            
            # 更新订单状态
            order.order_status = new_status
            order.updated_at = datetime.now()
            
            # 创建状态变更日志
            log = OrderStatusLogs(
                order_id=order_id,
                from_status=old_status,
                to_status=new_status,
                operator_id=operator_id,
                notes=notes
            )
            db.add(log)
            
            # 如果订单状态变为completed，更新支付状态
            if new_status == "completed" and order.payment_status == "unpaid":
                order.payment_status = "paid"
                order.payment_time = datetime.now()
            
            db.commit()
            db.refresh(order)
            
            return json.dumps({
                "success": True,
                "message": f"订单 {order.order_number} 状态已从 {old_status} 更新为 {new_status}",
                "order_id": order.id,
                "order_number": order.order_number,
                "old_status": old_status,
                "new_status": new_status
            }, ensure_ascii=False)
            
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        import traceback
        return json.dumps({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }, ensure_ascii=False, indent=2)


@tool
def analyze_order_anomalies(store_id: int, runtime=None) -> str:
    """
    分析异常订单，包括长时间未处理、支付失败等
    
    Args:
        store_id: 店铺ID
    
    Returns:
        返回异常订单列表的JSON字符串
    """
    import json
    from sqlalchemy import or_
    
    try:
        db = get_session()
        try:
            now = datetime.now()
            anomalies = []
            
            # 查询长时间未支付的订单（超过30分钟）
            pending_payment_orders = db.query(Orders).filter(
                Orders.store_id == store_id,
                Orders.payment_status == "unpaid",
                Orders.created_at < now - timedelta(minutes=30),
                Orders.order_status != "cancelled"
            ).all()
            
            for order in pending_payment_orders:
                anomalies.append({
                    "type": "长时间未支付",
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "table_id": order.table_id,
                    "amount": order.final_amount,
                    "waiting_time": (now - order.created_at).total_seconds() / 60,
                    "unit": "分钟",
                    "suggestion": "建议联系顾客确认支付情况"
                })
            
            # 查询长时间未处理的订单（超过15分钟）
            pending_orders = db.query(Orders).filter(
                Orders.store_id == store_id,
                Orders.order_status == "pending",
                Orders.created_at < now - timedelta(minutes=15)
            ).all()
            
            for order in pending_orders:
                anomalies.append({
                    "type": "长时间未确认",
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "table_id": order.table_id,
                    "amount": order.final_amount,
                    "waiting_time": (now - order.created_at).total_seconds() / 60,
                    "unit": "分钟",
                    "suggestion": "建议尽快确认订单并开始准备"
                })
            
            # 查询烹饪时间过长的订单（超过60分钟）
            preparing_orders = db.query(Orders).filter(
                Orders.store_id == store_id,
                Orders.order_status == "preparing",
                Orders.created_at < now - timedelta(minutes=60)
            ).all()
            
            for order in preparing_orders:
                anomalies.append({
                    "type": "烹饪时间过长",
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "table_id": order.table_id,
                    "amount": order.final_amount,
                    "waiting_time": (now - order.created_at).total_seconds() / 60,
                    "unit": "分钟",
                    "suggestion": "建议检查厨房进度，加快烹饪速度"
                })
            
            # 查询已准备好但未上菜的订单（超过10分钟）
            ready_orders = db.query(Orders).filter(
                Orders.store_id == store_id,
                Orders.order_status == "ready",
                Orders.created_at < now - timedelta(minutes=10)
            ).all()
            
            for order in ready_orders:
                anomalies.append({
                    "type": "已准备好但未上菜",
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "table_id": order.table_id,
                    "amount": order.final_amount,
                    "waiting_time": (now - order.created_at).total_seconds() / 60,
                    "unit": "分钟",
                    "suggestion": "建议尽快安排传菜员上菜"
                })
            
            return json.dumps({
                "success": True,
                "store_id": store_id,
                "analysis_time": now.isoformat(),
                "total_anomalies": len(anomalies),
                "anomalies": anomalies
            }, ensure_ascii=False, indent=2)
            
        finally:
            db.close()
            
    except Exception as e:
        import traceback
        return json.dumps({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }, ensure_ascii=False, indent=2)


@tool
def get_order_detail(order_id: int, runtime=None) -> str:
    """
    获取订单详细信息，包括订单项、支付信息、状态变更历史
    
    Args:
        order_id: 订单ID
    
    Returns:
        返回订单详情的JSON字符串
    """
    import json
    
    try:
        db = get_session()
        try:
            # 查询订单
            order = db.query(Orders).filter(Orders.id == order_id).first()
            if not order:
                return json.dumps({
                    "success": False,
                    "error": f"订单ID {order_id} 不存在"
                }, ensure_ascii=False)
            
            # 构建订单详情
            order_data = {
                "id": order.id,
                "order_number": order.order_number,
                "store_id": order.store_id,
                "table_id": order.table_id,
                "customer_name": order.customer_name,
                "customer_phone": order.customer_phone,
                "total_amount": order.total_amount,
                "discount_amount": order.discount_amount,
                "final_amount": order.final_amount,
                "payment_status": order.payment_status,
                "payment_method": order.payment_method,
                "payment_time": order.payment_time.isoformat() if order.payment_time else None,
                "order_status": order.order_status,
                "special_instructions": order.special_instructions,
                "created_at": order.created_at.isoformat(),
                "updated_at": order.updated_at.isoformat() if order.updated_at else None,
                "items": [],
                "payments": [],
                "status_logs": []
            }
            
            # 获取订单项
            for item in order.order_items:
                order_data["items"].append({
                    "id": item.id,
                    "menu_item_name": item.menu_item_name,
                    "menu_item_price": item.menu_item_price,
                    "quantity": item.quantity,
                    "subtotal": item.subtotal,
                    "special_instructions": item.special_instructions,
                    "status": item.status
                })
            
            # 获取支付信息
            for payment in order.payments:
                order_data["payments"].append({
                    "id": payment.id,
                    "payment_method": payment.payment_method,
                    "amount": payment.amount,
                    "transaction_id": payment.transaction_id,
                    "payment_time": payment.payment_time.isoformat() if payment.payment_time else None,
                    "status": payment.status,
                    "refund_amount": payment.refund_amount,
                    "refund_time": payment.refund_time.isoformat() if payment.refund_time else None,
                    "refund_reason": payment.refund_reason
                })
            
            # 获取状态变更历史
            for log in order.order_status_logs:
                order_data["status_logs"].append({
                    "id": log.id,
                    "from_status": log.from_status,
                    "to_status": log.to_status,
                    "operator_id": log.operator_id,
                    "operator_name": log.operator_name,
                    "notes": log.notes,
                    "created_at": log.created_at.isoformat()
                })
            
            return json.dumps({
                "success": True,
                "order": order_data
            }, ensure_ascii=False, indent=2)
            
        finally:
            db.close()
            
    except Exception as e:
        import traceback
        return json.dumps({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }, ensure_ascii=False, indent=2)
