"""
WebSocket 服务
支持订单状态实时推送
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Set
import json
import logging
from datetime import datetime

# 创建 FastAPI 应用
app = FastAPI(title="扫码点餐系统 - WebSocket服务", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)


# ============ 连接管理 ============

class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # store_id -> {connection_id: WebSocket}
        self.store_connections: Dict[int, Dict[str, WebSocket]] = {}
        # order_id -> {connection_id: WebSocket} 顾客订阅订单
        self.order_connections: Dict[int, Dict[str, WebSocket]] = {}
        # table_id -> {connection_id: WebSocket} 桌号连接（顾客端）
        self.table_connections: Dict[int, Dict[str, WebSocket]] = {}
    
    async def connect_to_store(self, websocket: WebSocket, store_id: int, connection_id: str):
        """连接到店铺（用于店员端）"""
        await websocket.accept()
        if store_id not in self.store_connections:
            self.store_connections[store_id] = {}
        self.store_connections[store_id][connection_id] = websocket
        logger.info(f"WebSocket连接到店铺: store_id={store_id}, connection_id={connection_id}")
        
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "message": "连接成功",
            "store_id": store_id,
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat()
        })
    
    async def connect_to_order(self, websocket: WebSocket, order_id: int, connection_id: str):
        """连接到订单（用于顾客端）"""
        await websocket.accept()
        if order_id not in self.order_connections:
            self.order_connections[order_id] = {}
        self.order_connections[order_id][connection_id] = websocket
        logger.info(f"WebSocket连接到订单: order_id={order_id}, connection_id={connection_id}")
        
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "message": "连接成功",
            "order_id": order_id,
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat()
        })
    
    async def connect_to_table(self, websocket: WebSocket, table_id: int, connection_id: str):
        """连接到桌号（用于顾客端）"""
        await websocket.accept()
        if table_id not in self.table_connections:
            self.table_connections[table_id] = {}
        self.table_connections[table_id][connection_id] = websocket
        logger.info(f"WebSocket连接到桌号: table_id={table_id}, connection_id={connection_id}")
        
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "message": "连接成功",
            "table_id": table_id,
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect(self, store_id: int = None, order_id: int = None, table_id: int = None, connection_id: str = None):
        """断开连接"""
        if store_id and store_id in self.store_connections:
            if connection_id and connection_id in self.store_connections[store_id]:
                del self.store_connections[store_id][connection_id]
                logger.info(f"断开店铺连接: store_id={store_id}, connection_id={connection_id}")
        
        if order_id and order_id in self.order_connections:
            if connection_id and connection_id in self.order_connections[order_id]:
                del self.order_connections[order_id][connection_id]
                logger.info(f"断开订单连接: order_id={order_id}, connection_id={connection_id}")
        
        if table_id and table_id in self.table_connections:
            if connection_id and connection_id in self.table_connections[table_id]:
                del self.table_connections[table_id][connection_id]
                logger.info(f"断开桌号连接: table_id={table_id}, connection_id={connection_id}")
    
    async def broadcast_to_store(self, store_id: int, message: dict):
        """向店铺的所有连接广播消息"""
        if store_id not in self.store_connections:
            return
        
        disconnected = []
        for connection_id, websocket in self.store_connections[store_id].items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败: store_id={store_id}, connection_id={connection_id}, error={str(e)}")
                disconnected.append(connection_id)
        
        # 清理断开的连接
        for connection_id in disconnected:
            del self.store_connections[store_id][connection_id]
    
    async def broadcast_to_order(self, order_id: int, message: dict):
        """向订单的所有连接广播消息（顾客端）"""
        if order_id not in self.order_connections:
            return
        
        disconnected = []
        for connection_id, websocket in self.order_connections[order_id].items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败: order_id={order_id}, connection_id={connection_id}, error={str(e)}")
                disconnected.append(connection_id)
        
        # 清理断开的连接
        for connection_id in disconnected:
            del self.order_connections[order_id][connection_id]
    
    async def broadcast_to_table(self, table_id: int, message: dict):
        """向桌号的所有连接广播消息（顾客端）"""
        if table_id not in self.table_connections:
            return
        
        disconnected = []
        for connection_id, websocket in self.table_connections[table_id].items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败: table_id={table_id}, connection_id={connection_id}, error={str(e)}")
                disconnected.append(connection_id)
        
        # 清理断开的连接
        for connection_id in disconnected:
            del self.table_connections[table_id][connection_id]
    
    async def broadcast_order_status(self, order_id: int, order_data: dict):
        """
        广播订单状态更新
        同时推送到店铺（店员端）和订单（顾客端）
        """
        message = {
            "type": "order_status_update",
            "order": order_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # 推送到店铺
        if "store_id" in order_data:
            await self.broadcast_to_store(order_data["store_id"], message)
        
        # 推送到订单
        await self.broadcast_to_order(order_id, message)
    
    async def broadcast_new_order(self, order_data: dict):
        """广播新订单到店铺"""
        message = {
            "type": "new_order",
            "order": order_data,
            "timestamp": datetime.now().isoformat()
        }
        
        if "store_id" in order_data:
            await self.broadcast_to_store(order_data["store_id"], message)
    
    async def broadcast_payment_status(self, order_id: int, payment_data: dict):
        """广播支付状态更新"""
        message = {
            "type": "payment_status_update",
            "payment": payment_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # 推送到店铺
        if "store_id" in payment_data:
            await self.broadcast_to_store(payment_data["store_id"], message)
        
        # 推送到订单
        await self.broadcast_to_order(order_id, message)


# 全局连接管理器
manager = ConnectionManager()


# ============ API 接口 ============

@app.get("/")
def root():
    """根路径"""
    return {
        "message": "扫码点餐系统 - WebSocket服务",
        "version": "1.0.0",
        "endpoints": {
            "WS /ws/store/{store_id}": "店铺WebSocket连接（店员端）",
            "WS /ws/order/{order_id}": "订单WebSocket连接（顾客端）",
            "WS /ws/table/{table_id}": "桌号WebSocket连接（顾客端）"
        }
    }


@app.websocket("/ws/store/{store_id}")
async def websocket_store(
    websocket: WebSocket,
    store_id: int,
    connection_id: str = Query(default=None)
):
    """
    店铺WebSocket连接
    店员端使用，接收新订单和订单状态更新
    """
    if not connection_id:
        connection_id = f"store_{store_id}_{datetime.now().timestamp()}"
    
    await manager.connect_to_store(websocket, store_id, connection_id)
    
    try:
        while True:
            # 接收客户端消息（心跳等）
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理心跳
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
    except WebSocketDisconnect:
        manager.disconnect(store_id=store_id, connection_id=connection_id)
    except Exception as e:
        logger.error(f"店铺WebSocket错误: {str(e)}")
        manager.disconnect(store_id=store_id, connection_id=connection_id)


@app.websocket("/ws/order/{order_id}")
async def websocket_order(
    websocket: WebSocket,
    order_id: int,
    connection_id: str = Query(default=None)
):
    """
    订单WebSocket连接
    顾客端使用，接收订单状态和支付状态更新
    """
    if not connection_id:
        connection_id = f"order_{order_id}_{datetime.now().timestamp()}"
    
    await manager.connect_to_order(websocket, order_id, connection_id)
    
    try:
        while True:
            # 接收客户端消息（心跳等）
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理心跳
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
    except WebSocketDisconnect:
        manager.disconnect(order_id=order_id, connection_id=connection_id)
    except Exception as e:
        logger.error(f"订单WebSocket错误: {str(e)}")
        manager.disconnect(order_id=order_id, connection_id=connection_id)


@app.websocket("/ws/table/{table_id}")
async def websocket_table(
    websocket: WebSocket,
    table_id: int,
    connection_id: str = Query(default=None)
):
    """
    桌号WebSocket连接
    顾客端使用，接收该桌号的订单状态更新
    """
    if not connection_id:
        connection_id = f"table_{table_id}_{datetime.now().timestamp()}"
    
    await manager.connect_to_table(websocket, table_id, connection_id)
    
    try:
        while True:
            # 接收客户端消息（心跳等）
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理心跳
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
    except WebSocketDisconnect:
        manager.disconnect(table_id=table_id, connection_id=connection_id)
    except Exception as e:
        logger.error(f"桌号WebSocket错误: {str(e)}")
        manager.disconnect(table_id=table_id, connection_id=connection_id)


# ============ 辅助函数（供其他模块调用）===========

def get_connection_manager():
    """获取连接管理器"""
    return manager


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
