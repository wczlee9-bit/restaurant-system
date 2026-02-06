from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from websocket_manager import manager
from datetime import datetime

router = APIRouter(prefix="/ws", tags=["WebSocket"])

@router.websocket("/orders")
async def websocket_orders(
    websocket: WebSocket,
    store_id: int = Query(1, description="店铺ID")
):
    """订单实时推送 WebSocket"""
    room = f"orders_{store_id}"
    await manager.connect(websocket, room)
    
    try:
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "message": f"已连接到店铺 {store_id} 的订单推送",
            "timestamp": str(datetime.now())
        })
        
        # 保持连接，等待消息
        while True:
            # 这里可以接收客户端的消息（如心跳包）
            data = await websocket.receive_text()
            await websocket.send_json({
                "type": "pong",
                "message": f"收到消息: {data}",
                "timestamp": str(datetime.now())
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, room)

@router.websocket("/table/{table_id}")
async def websocket_table(
    websocket: WebSocket,
    table_id: int,
    store_id: int = Query(1, description="店铺ID")
):
    """桌台订单实时推送 WebSocket（用于顾客端）"""
    room = f"table_{table_id}_store_{store_id}"
    await manager.connect(websocket, room)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "message": f"已连接到 {table_id} 号桌的订单推送",
            "timestamp": str(datetime.now())
        })
        
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({
                "type": "pong",
                "message": f"收到消息: {data}",
                "timestamp": str(datetime.now())
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, room)

# 辅助函数：在订单状态更新时调用
async def notify_order_update(store_id: int, order_id: int, status: str):
    """通知订单更新"""
    room = f"orders_{store_id}"
    await manager.broadcast({
        "type": "order_update",
        "order_id": order_id,
        "status": status,
        "timestamp": str(datetime.now())
    }, room)

# 辅助函数：在新订单创建时调用
async def notify_new_order(store_id: int, order_data: dict, table_id: int):
    """通知新订单"""
    # 通知管理端
    room = f"orders_{store_id}"
    await manager.broadcast({
        "type": "new_order",
        "order": order_data,
        "timestamp": str(datetime.now())
    }, room)
    
    # 通知桌台
    room = f"table_{table_id}_store_{store_id}"
    await manager.broadcast({
        "type": "new_order",
        "order": order_data,
        "timestamp": str(datetime.now())
    }, room)
