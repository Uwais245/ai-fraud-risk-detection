from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.core.deps import get_current_active_user, require_analyst
from app.models.user import User
from app.models.feedback import Feedback, FeedbackType
from app.models.alert import Alert, AlertStatus
from app.models.transaction import Transaction
from app.schemas.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter()


@router.post("/", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Submit feedback on a transaction (Confirmed Fraud / False Positive)"""
    # Verify transaction exists
    stmt = select(Transaction).where(Transaction.transaction_id == feedback_data.transaction_id)
    result = await db.execute(stmt)
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Create feedback
    feedback = Feedback(
        transaction_id=feedback_data.transaction_id,
        alert_id=feedback_data.alert_id,
        feedback_type=feedback_data.feedback_type,
        notes=feedback_data.notes,
        submitted_by=current_user.id
    )
    db.add(feedback)
    
    # Update alert status if alert_id provided
    if feedback_data.alert_id:
        stmt = select(Alert).where(Alert.id == feedback_data.alert_id)
        result = await db.execute(stmt)
        alert = result.scalar_one_or_none()
        
        if alert:
            if feedback_data.feedback_type == FeedbackType.CONFIRMED_FRAUD:
                alert.status = AlertStatus.CONFIRMED_FRAUD
                transaction.is_fraud = True
            elif feedback_data.feedback_type == FeedbackType.FALSE_POSITIVE:
                alert.status = AlertStatus.FALSE_POSITIVE
            
            from datetime import datetime
            alert.resolved_at = datetime.utcnow()
            alert.assigned_to = current_user.id
    
    await db.commit()
    await db.refresh(feedback)
    
    return feedback


@router.get("/transaction/{transaction_id}", response_model=List[FeedbackResponse])
async def get_feedback_for_transaction(
    transaction_id: str,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get all feedback for a transaction"""
    stmt = (
        select(Feedback)
        .where(Feedback.transaction_id == transaction_id)
        .order_by(Feedback.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()