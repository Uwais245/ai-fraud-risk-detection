from typing import Dict, List, Set
from fastapi import WebSocket
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Active connections: {user_id: Set[WebSocket]}
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # All connections for broadcast
        self.all_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.all_connections.add(websocket)
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected. Total connections: {len(self.all_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove a WebSocket connection"""
        self.all_connections.discard(websocket)
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected. Total connections: {len(self.all_connections)}")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user"""
        if user_id in self.active_connections:
            disconnected = set()
            for ws in self.active_connections[user_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    disconnected.add(ws)
            
            # Clean up disconnected
            for ws in disconnected:
                self.disconnect(ws, user_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for ws in self.all_connections:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.add(ws)
        
        # Clean up disconnected
        for ws in disconnected:
            self.all_connections.discard(ws)
    
    async def broadcast_to_role(self, message: dict, role: str):
        """Broadcast to users with specific role (would need user-role mapping)"""
        # For now, broadcast to all
        await self.broadcast(message)


# Global connection manager
manager = ConnectionManager()


async def notify_new_alert(alert_data: dict):
    """Notify all users about new alert"""
    message = {
        "type": "alert:created",
        "data": alert_data
    }
    await manager.broadcast(message)


async def notify_alert_update(alert_data: dict):
    """Notify about alert status change"""
    message = {
        "type": "alert:updated",
        "data": alert_data
    }
    await manager.broadcast(message)


async def notify_new_transaction(transaction_data: dict):
    """Notify about new high-risk transaction"""
    message = {
        "type": "transaction:high_risk",
        "data": transaction_data
    }
    await manager.broadcast(message)


async def notify_risk_recalculated(transaction_id: str, new_score: float):
    """Notify about risk score recalculation"""
    message = {
        "type": "risk:recalculated",
        "data": {
            "transaction_id": transaction_id,
            "new_risk_score": new_score
        }
    }
    await manager.broadcast(message)


async def notify_dashboard_update(stats: dict):
    """Notify dashboard clients of stats update"""
    message = {
        "type": "dashboard:stats_update",
        "data": stats
    }
    await manager.broadcast(message)