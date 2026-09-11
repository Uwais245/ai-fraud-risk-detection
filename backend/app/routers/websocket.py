import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_token
from app.core.config import settings
from app.models.user import User
from sqlalchemy import select
from app.services.websocket import manager

router = APIRouter()


async def get_user_from_token(token: str, db: AsyncSession) -> User:
    """Get user from JWT token"""
    payload = decode_token(token)
    if not payload:
        return None
    email = payload.get("sub")
    if not email:
        return None
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time updates"""
    # Authenticate user
    user = await get_user_from_token(token, db)
    if not user:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    # Connect
    await manager.connect(websocket, user.id)
    
    try:
        # Keep connection alive, listen for messages
        while True:
            data = await websocket.receive_text()
            # Echo back or handle client messages
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
    except Exception as e:
        manager.disconnect(websocket, user.id)
        # Log error
        print(f"WebSocket error: {e}")


@router.websocket("/ws/dashboard")
async def dashboard_websocket(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint specifically for dashboard updates"""
    user = await get_user_from_token(token, db)
    if not user:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    await manager.connect(websocket, user.id)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "subscribe":
                    # Client wants to subscribe to specific events
                    pass
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
    except Exception as e:
        manager.disconnect(websocket, user.id)
        print(f"Dashboard WebSocket error: {e}")