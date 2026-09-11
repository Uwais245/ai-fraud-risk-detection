from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.core.deps import get_current_active_user, require_analyst
from app.models.user import User
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.schemas.alert import AlertUpdate, AlertResponse, AlertListResponse, AlertFilter

router = APIRouter()


@router.get("/", response_model=AlertListResponse)
async def list_alerts(
    filter_params: AlertFilter = Depends(),
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """List alerts with filtering and pagination"""
    stmt = select(Alert)
    
    if filter_params.status:
        stmt = stmt.where(Alert.status == filter_params.status)
    if filter_params.severity:
        stmt = stmt.where(Alert.severity == filter_params.severity)
    if filter_params.assigned_to:
        stmt = stmt.where(Alert.assigned_to == filter_params.assigned_to)
    if filter_params.date_from:
        stmt = stmt.where(Alert.created_at >= filter_params.date_from)
    if filter_params.date_to:
        stmt = stmt.where(Alert.created_at <= filter_params.date_to)
    
    stmt = stmt.order_by(desc(Alert.created_at))
    
    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0
    
    # Paginate
    stmt = stmt.offset((filter_params.page - 1) * filter_params.per_page).limit(filter_params.per_page)
    result = await db.execute(stmt)
    alerts = result.scalars().all()
    
    return AlertListResponse(
        alerts=alerts,
        total=total,
        page=filter_params.page,
        per_page=filter_params.per_page,
        total_pages=(total + filter_params.per_page - 1) // filter_params.per_page
    )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get alert by ID"""
    stmt = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return alert


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    update: AlertUpdate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Update alert status, assignment, or notes"""
    stmt = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if update.status is not None:
        alert.status = update.status
        if update.status in [AlertStatus.CONFIRMED_FRAUD, AlertStatus.FALSE_POSITIVE, AlertStatus.RESOLVED]:
            alert.resolved_at = datetime.utcnow()
    
    if update.assigned_to is not None:
        alert.assigned_to = update.assigned_to
    
    if update.investigation_notes is not None:
        existing = alert.investigation_notes or ""
        alert.investigation_notes = f"{existing}\n\n[{datetime.utcnow().isoformat()}] User {current_user.id}: {update.investigation_notes}"
    
    await db.commit()
    await db.refresh(alert)
    
    return alert


@router.post("/{alert_id}/assign")
async def assign_alert(
    alert_id: int,
    user_id: int,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Assign alert to a user"""
    stmt = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.assigned_to = user_id
    alert.status = AlertStatus.INVESTIGATING
    
    await db.commit()
    await db.refresh(alert)
    
    return {"message": "Alert assigned", "alert": alert}


@router.get("/stats/summary")
async def get_alerts_summary(
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get alert statistics summary"""
    from sqlalchemy import select, func
    
    # Count by status
    stmt = (
        select(Alert.status, func.count(Alert.id))
        .group_by(Alert.status)
    )
    result = await db.execute(stmt)
    by_status = {row[0].value: row[1] for row in result.all()}
    
    # Count by severity
    stmt = (
        select(Alert.severity, func.count(Alert.id))
        .group_by(Alert.severity)
    )
    result = await db.execute(stmt)
    by_severity = {row[0].value: row[1] for row in result.all()}
    
    # Total
    total = await db.scalar(select(func.count(Alert.id))) or 0
    
    return {
        "total": total,
        "by_status": by_status,
        "by_severity": by_severity
    }