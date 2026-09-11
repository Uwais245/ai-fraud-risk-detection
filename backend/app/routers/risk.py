from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_active_user, require_analyst
from app.models.user import User
from app.schemas.risk import (
    RiskScoreRequest, RiskScoreBatchRequest, RiskAssessmentResponse, RiskFlagsResponse
)
from app.services.ml_integration import ml_service
from app.services.ai_integration import ai_service
from app.models.risk_assessment import RiskAssessment
from app.models.transaction import Transaction
from sqlalchemy import select
from typing import List

router = APIRouter()


@router.post("/score", response_model=RiskAssessmentResponse)
async def score_transaction(
    request: RiskScoreRequest,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Score a single transaction for fraud risk"""
    # Convert request to dict for ML service
    txn_data = request.model_dump()
    
    # Score using ML engine
    result = ml_service.score_transaction(txn_data)
    
    # Generate AI explanation if high risk or has flags
    if result.get("risk_flags"):
        ai_explanation = ai_service.generate_explanation(
            result["risk_flags"],
            {"amount": txn_data.get("amount"), "customer_id": txn_data.get("customer_id")}
        )
        result["ai_explanation"] = ai_explanation
    
    # Save to database if transaction exists
    stmt = select(Transaction).where(Transaction.transaction_id == request.transaction_id)
    db_txn = (await db.execute(stmt)).scalar_one_or_none()
    
    if db_txn:
        risk_assessment = RiskAssessment(
            transaction_id=request.transaction_id,
            ml_anomaly_score=result.get("ml_anomaly_score", 0),
            rule_engine_score=result.get("rule_engine_score", 0),
            final_risk_score=result["final_risk_score"],
            risk_level=result["risk_level"],
            decision=result["decision"],
            risk_flags=result["risk_flags"],
            ai_explanation=result.get("ai_explanation")
        )
        db.add(risk_assessment)
        
        # Create alert if high risk
        if result["risk_level"] == "HIGH":
            from app.models.alert import Alert, AlertSeverity, AlertStatus
            alert = Alert(
                transaction_id=request.transaction_id,
                severity=AlertSeverity.HIGH,
                reason="; ".join(result["risk_flags"][:3]),
                status=AlertStatus.NEW,
                risk_score=int(result["final_risk_score"]),
                risk_flags=result["risk_flags"],
                ai_explanation=result.get("ai_explanation")
            )
            db.add(alert)
        
        await db.commit()
    
    return RiskAssessmentResponse(**result)


@router.post("/batch", response_model=List[RiskAssessmentResponse])
async def score_transactions_batch(
    request: RiskScoreBatchRequest,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Score multiple transactions for fraud risk"""
    transactions_data = [txn.model_dump() for txn in request.transactions]
    results = ml_service.batch_score(transactions_data)
    
    # Generate AI explanations
    for result in results:
        if result.get("risk_flags"):
            ai_explanation = ai_service.generate_explanation(
                result["risk_flags"],
                {"amount": result.get("amount"), "customer_id": result.get("customer_id")}
            )
            result["ai_explanation"] = ai_explanation
    
    return [RiskAssessmentResponse(**r) for r in results]


@router.get("/flags", response_model=RiskFlagsResponse)
async def get_risk_flags(
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get all unique risk flags that have been triggered"""
    stmt = select(RiskAssessment.risk_flags).where(RiskAssessment.risk_flags.isnot(None))
    result = await db.execute(stmt)
    all_flags = result.scalars().all()
    
    # Flatten and deduplicate
    unique_flags = set()
    for flags in all_flags:
        if flags:
            unique_flags.update(flags)
    
    return RiskFlagsResponse(
        flags=sorted(list(unique_flags)),
        total_count=len(unique_flags)
    )