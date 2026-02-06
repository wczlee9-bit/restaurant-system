from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # 存储所有活跃的 WebSocket 连接
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room: str):
        """连接到指定房间"""
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = set()
        self.active_connections[room].add(websocket)
        logger.info(f"WebSocket connected to room: {room}, total: {len(self.active_connections[room])}")
    
    def disconnect(self, websocket: WebSocket, room: str):
        """断开连接"""
        if room in self.active_connections:
            self.active_connections[room].discard(websocket)
            if not self.active_connections[room]:
                del self.active_connections[room]
        logger.info(f"WebSocket disconnected from room: {room}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """发送个人消息"""
        await websocket.send_text(message)
    
    async def broadcast(self, message: dict, room: str):
        """向房间内所有连接广播消息"""
        if room not in self.active_connections:
            return
        
        message_str = json.dumps(message, ensure_ascii=False)
        disconnected = set()
        
        for connection in self.active_connections[room]:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                disconnected.add(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.active_connections[room].discard(connection)
    
    async def broadcast_order_update(self, order_id: int, status: str, room: str = "orders"):
        """广播订单更新"""
        await self.broadcast({
            "type": "order_update",
            "order_id": order_id,
            "status": status,
            "timestamp": str(datetime.now())
        }, room)
    
    async def broadcast_new_order(self, order_data: dict, room: str = "orders"):
        """广播新订单"""
        await self.broadcast({
            "type": "new_order",
            "order": order_data,
            "timestamp": str(datetime.now())
        }, room)

# 全局连接管理器
manager = ConnectionManager()
