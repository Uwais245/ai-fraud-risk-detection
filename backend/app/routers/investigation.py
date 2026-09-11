from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.deps import get_current_active_user, require_analyst
from app.models.user import User
from app.services.investigation import InvestigationService
from app.schemas.investigation import (
    InvestigationDetail, InvestigationNoteCreate, InvestigationNoteResponse
)
from app.services.ai_integration import ai_service

router = APIRouter()


@router.get("/transaction/{transaction_id}", response_model=InvestigationDetail)
async def get_investigation(
    transaction_id: str,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get complete investigation detail for a transaction"""
    service = InvestigationService(db)
    detail = await service.get_investigation_detail(transaction_id)
    
    if not detail:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return detail


@router.get("/customer/{customer_id}/profile")
async def get_customer_profile(
    customer_id: str,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get customer risk profile"""
    from app.models.customer_profile import CustomerRiskProfile
    from sqlalchemy import select
    
    stmt = select(CustomerRiskProfile).where(CustomerRiskProfile.customer_id == customer_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if not profile:
        # Build on-the-fly
        service = InvestigationService(db)
        profile = await service._get_customer_profile(customer_id)
    
    return profile


@router.post("/transaction/{transaction_id}/notes", response_model=InvestigationNoteResponse)
async def add_investigation_note(
    transaction_id: str,
    note: InvestigationNoteCreate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Add investigation note to a transaction"""
    service = InvestigationService(db)
    alert = await service.add_investigation_note(transaction_id, note.note, current_user.id)
    
    return InvestigationNoteResponse(
        id=alert.id,
        transaction_id=alert.transaction_id,
        note=alert.investigation_notes or "",
        created_by=alert.assigned_to or current_user.id,
        created_at=alert.updated_at
    )


@router.post("/question")
async def ask_investigation_question(
    question: str,
    transaction_id: str,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Ask AI assistant a question about an investigation"""
    service = InvestigationService(db)
    detail = await service.get_investigation_detail(transaction_id)
    
    if not detail:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Build context for AI
    context = {
        "customer_id": detail.customer_profile.customer_id,
        "risk_profile": {
            "risk_level": detail.customer_profile.risk_level,
            "risk_score": detail.customer_profile.risk_score,
            "total_transactions": detail.customer_profile.total_transactions,
            "suspicious_transactions": detail.customer_profile.suspicious_transactions
        },
        "recent_transactions": [
            {
                "transaction_id": rt.transaction_id,
                "amount": str(rt.amount),
                "risk_level": rt.risk_level,
                "created_at": rt.created_at.isoformat()
            }
            for rt in detail.related_transactions[:10]
        ],
        "devices": [
            {
                "device_id": d.device_id,
                "risk_level": d.risk_level,
                "associated_customers": d.associated_customers
            }
            for d in detail.devices
        ],
        "ips": [
            {
                "ip_address": ip.ip_address,
                "country": ip.country,
                "risk_level": ip.risk_level
            }
            for ip in detail.ips
        ],
        "alerts": [
            {
                "id": a.id,
                "severity": a.severity,
                "reason": a.reason,
                "status": a.status
            }
            for a in detail.alerts
        ]
    }
    
    answer = ai_service.answer_investigation_question(question, context)
    
    return {"question": question, "answer": answer}