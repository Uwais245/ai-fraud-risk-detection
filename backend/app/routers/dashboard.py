from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.deps import get_current_active_user, require_analyst
from app.models.user import User
from app.services.dashboard_stats import DashboardService
from app.schemas.dashboard import DashboardData

router = APIRouter()


@router.get("/stats", response_model=DashboardData)
async def get_dashboard_stats(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get all dashboard statistics in one call"""
    service = DashboardService(db)
    
    stats = await service.get_stats()
    trends = await service.get_trends(days=days)
    risk_distribution = await service.get_risk_distribution()
    suspicious_customers = await service.get_suspicious_customers(limit=10)
    suspicious_devices = await service.get_suspicious_devices(limit=10)
    recent_alerts = await service.get_recent_alerts(limit=20)
    
    return DashboardData(
        stats=stats,
        trends=trends,
        risk_distribution=risk_distribution,
        suspicious_customers=suspicious_customers,
        suspicious_devices=suspicious_devices,
        recent_alerts=recent_alerts
    )


@router.get("/trends")
async def get_trends(
    days: int = Query(7, ge=1, le=90),
    interval: str = Query("1d", pattern="^(1h|1d|1w)$"),
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get transaction trends over time"""
    service = DashboardService(db)
    return await service.get_trends(days=days)


@router.get("/risk-distribution")
async def get_risk_distribution(
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get risk level distribution"""
    service = DashboardService(db)
    return await service.get_risk_distribution()


@router.get("/suspicious-customers")
async def get_suspicious_customers(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get top suspicious customers"""
    service = DashboardService(db)
    return await service.get_suspicious_customers(limit=limit)


@router.get("/suspicious-devices")
async def get_suspicious_devices(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get top suspicious devices/IPs"""
    service = DashboardService(db)
    return await service.get_suspicious_devices(limit=limit)


@router.get("/alerts")
async def get_recent_alerts(
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get recent alerts"""
    service = DashboardService(db)
    alerts = await service.get_recent_alerts(limit=limit)
    
    if status:
        alerts.alerts = [a for a in alerts.alerts if a.status == status.upper()]
    
    return alerts