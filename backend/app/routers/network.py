from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.deps import get_current_active_user, require_analyst
from app.models.user import User
from app.services.network import NetworkService
from app.schemas.network import (
    NetworkGraphResponse, NetworkClustersResponse, NetworkGraphRequest
)

router = APIRouter()


@router.get("/graph", response_model=NetworkGraphResponse)
async def get_network_graph(
    customer_id: Optional[str] = Query(None),
    transaction_id: Optional[str] = Query(None),
    device_id: Optional[str] = Query(None),
    ip_address: Optional[str] = Query(None),
    depth: int = Query(2, ge=1, le=5),
    risk_level: Optional[str] = Query(None, pattern="^(LOW|MEDIUM|HIGH)$"),
    limit: int = Query(500, ge=10, le=2000),
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get fraud network graph data for visualization"""
    service = NetworkService(db)
    return await service.get_network_graph(
        customer_id=customer_id,
        transaction_id=transaction_id,
        device_id=device_id,
        ip_address=ip_address,
        depth=depth,
        risk_level=risk_level,
        limit=limit
    )


@router.post("/graph", response_model=NetworkGraphResponse)
async def get_network_graph_post(
    request: NetworkGraphRequest,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get fraud network graph data (POST for complex queries)"""
    service = NetworkService(db)
    return await service.get_network_graph(
        customer_id=request.customer_id,
        transaction_id=request.transaction_id,
        device_id=request.device_id,
        ip_address=request.ip_address,
        depth=request.depth,
        risk_level=request.risk_level,
        limit=request.limit
    )


@router.get("/clusters", response_model=NetworkClustersResponse)
async def get_suspicious_clusters(
    min_size: int = Query(3, ge=2, le=20),
    risk_threshold: str = Query("HIGH", pattern="^(MEDIUM|HIGH)$"),
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get suspicious network clusters (shared devices, IPs, etc.)"""
    service = NetworkService(db)
    return await service.get_suspicious_clusters(
        min_size=min_size,
        risk_threshold=risk_threshold
    )