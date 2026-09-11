from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.core.database import get_db
from app.core.deps import get_current_active_user, require_analyst
from app.models.user import User
from app.models.transaction import Transaction
from app.models.risk_assessment import RiskAssessment
from app.models.alert import Alert
from app.schemas.transaction import (
    TransactionCreate, TransactionCreateBatch, TransactionUpdate,
    TransactionResponse, TransactionDetail, TransactionListResponse, TransactionFilter,
    TransactionChannel
)
from app.schemas.risk import RiskAssessmentResponse
from app.schemas.alert import AlertResponse
from app.services.ml_integration import ml_service
from app.services.ai_integration import ai_service
from app.services.csv_import import CSVImportService

router = APIRouter()


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Submit a new transaction for analysis"""
    # Check for duplicate
    stmt = select(Transaction).where(Transaction.transaction_id == transaction.transaction_id)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction {transaction.transaction_id} already exists"
        )
    
    # Create transaction
    txn_data = transaction.model_dump()
    db_transaction = Transaction(**txn_data)
    db.add(db_transaction)
    await db.flush()
    
    # Score the transaction
    risk_result = ml_service.score_transaction(txn_data)
    
    # Generate AI explanation
    ai_explanation = None
    if risk_result.get("risk_flags"):
        ai_explanation = ai_service.generate_explanation(
            risk_result["risk_flags"],
            {"amount": txn_data.get("amount"), "customer_id": txn_data.get("customer_id")}
        )
    
    # Create risk assessment
    risk_assessment = RiskAssessment(
        transaction_id=transaction.transaction_id,
        ml_anomaly_score=risk_result.get("ml_anomaly_score", 0),
        rule_engine_score=risk_result.get("rule_engine_score", 0),
        final_risk_score=risk_result["final_risk_score"],
        risk_level=risk_result["risk_level"],
        decision=risk_result["decision"],
        risk_flags=risk_result["risk_flags"],
        ai_explanation=ai_explanation
    )
    db.add(risk_assessment)
    
    # Create alert if high risk
    if risk_result["risk_level"] == "HIGH":
        from app.models.alert import Alert, AlertSeverity, AlertStatus
        alert = Alert(
            transaction_id=transaction.transaction_id,
            severity=AlertSeverity.HIGH,
            reason="; ".join(risk_result["risk_flags"][:3]),
            status=AlertStatus.NEW,
            risk_score=int(risk_result["final_risk_score"]),
            risk_flags=risk_result["risk_flags"],
            ai_explanation=ai_explanation
        )
        db.add(alert)
    
    await db.commit()
    await db.refresh(db_transaction)
    
    return db_transaction


@router.post("/batch", response_model=List[TransactionResponse])
async def create_transactions_batch(
    batch: TransactionCreateBatch,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Submit multiple transactions for analysis"""
    results = []
    
    for transaction in batch.transactions:
        # Check for duplicate
        stmt = select(Transaction).where(Transaction.transaction_id == transaction.transaction_id)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            continue  # Skip duplicates
        
        txn_data = transaction.model_dump()
        db_transaction = Transaction(**txn_data)
        db.add(db_transaction)
        
        # Score
        risk_result = ml_service.score_transaction(txn_data)
        
        # AI explanation
        ai_explanation = None
        if risk_result.get("risk_flags"):
            ai_explanation = ai_service.generate_explanation(
                risk_result["risk_flags"],
                {"amount": txn_data.get("amount"), "customer_id": txn_data.get("customer_id")}
            )
        
        # Risk assessment
        risk_assessment = RiskAssessment(
            transaction_id=transaction.transaction_id,
            ml_anomaly_score=risk_result.get("ml_anomaly_score", 0),
            rule_engine_score=risk_result.get("rule_engine_score", 0),
            final_risk_score=risk_result["final_risk_score"],
            risk_level=risk_result["risk_level"],
            decision=risk_result["decision"],
            risk_flags=risk_result["risk_flags"],
            ai_explanation=ai_explanation
        )
        db.add(risk_assessment)
        
        # Alert if high risk
        if risk_result["risk_level"] == "HIGH":
            from app.models.alert import Alert, AlertSeverity, AlertStatus
            alert = Alert(
                transaction_id=transaction.transaction_id,
                severity=AlertSeverity.HIGH,
                reason="; ".join(risk_result["risk_flags"][:3]),
                status=AlertStatus.NEW,
                risk_score=int(risk_result["final_risk_score"]),
                risk_flags=risk_result["risk_flags"],
                ai_explanation=ai_explanation
            )
            db.add(alert)
        
        results.append(db_transaction)
    
    await db.commit()
    for r in results:
        await db.refresh(r)
    
    return results


@router.get("/", response_model=TransactionListResponse)
async def list_transactions(
    filter_params: TransactionFilter = Depends(),
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """List transactions with filtering and pagination"""
    stmt = select(Transaction)
    
    # Apply filters
    if filter_params.customer_id:
        stmt = stmt.where(Transaction.customer_id == filter_params.customer_id)
    if filter_params.transaction_id:
        stmt = stmt.where(Transaction.transaction_id.ilike(f"%{filter_params.transaction_id}%"))
    if filter_params.min_amount is not None:
        stmt = stmt.where(Transaction.amount >= filter_params.min_amount)
    if filter_params.max_amount is not None:
        stmt = stmt.where(Transaction.amount <= filter_params.max_amount)
    if filter_params.channel:
        stmt = stmt.where(Transaction.channel == filter_params.channel)
    if filter_params.country:
        stmt = stmt.where(Transaction.country == filter_params.country)
    if filter_params.date_from:
        stmt = stmt.where(Transaction.created_at >= filter_params.date_from)
    if filter_params.date_to:
        stmt = stmt.where(Transaction.created_at <= filter_params.date_to)
    if filter_params.is_fraud is not None:
        stmt = stmt.where(Transaction.is_fraud == filter_params.is_fraud)
    
    # Risk level filter (join with risk_assessments)
    if filter_params.risk_level:
        stmt = stmt.join(RiskAssessment).where(RiskAssessment.risk_level == filter_params.risk_level)
    
    # Order by created_at desc
    stmt = stmt.order_by(desc(Transaction.created_at))
    
    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0
    
    # Apply pagination
    stmt = stmt.offset((filter_params.page - 1) * filter_params.per_page).limit(filter_params.per_page)
    
    result = await db.execute(stmt)
    transactions = result.scalars().all()
    
    return TransactionListResponse(
        transactions=transactions,
        total=total,
        page=filter_params.page,
        per_page=filter_params.per_page,
        total_pages=(total + filter_params.per_page - 1) // filter_params.per_page
    )


@router.get("/search")
async def search_transactions(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Search transactions by ID or customer ID"""
    stmt = select(Transaction).where(
        or_(
            Transaction.transaction_id.ilike(f"%{q}%"),
            Transaction.customer_id.ilike(f"%{q}%")
        )
    ).order_by(desc(Transaction.created_at)).limit(limit)
    
    result = await db.execute(stmt)
    transactions = result.scalars().all()
    
    return transactions


@router.get("/{transaction_id}", response_model=TransactionDetail)
async def get_transaction(
    transaction_id: str,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Get transaction detail with risk assessment and alerts"""
    stmt = (
        select(Transaction)
        .options(selectinload(Transaction.risk_assessments), selectinload(Transaction.alerts))
        .where(Transaction.transaction_id == transaction_id)
    )
    result = await db.execute(stmt)
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    update: TransactionUpdate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Update transaction (e.g., mark as fraud)"""
    stmt = select(Transaction).where(Transaction.transaction_id == transaction_id)
    result = await db.execute(stmt)
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if update.is_fraud is not None:
        transaction.is_fraud = update.is_fraud
    
    await db.commit()
    await db.refresh(transaction)
    
    return transaction


@router.post("/import/csv")
async def import_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Import transactions from CSV file"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    content = await file.read()
    
    csv_service = CSVImportService(db)
    result = await csv_service.import_csv(content, current_user.id)
    
    return result


@router.post("/import/csv/template")
async def download_csv_template(
    current_user: User = Depends(require_analyst)
):
    """Download CSV template for import"""
    import io
    import csv
    from fastapi.responses import StreamingResponse
    
    headers = [
        "transaction_id", "customer_id", "amount", "currency", "country",
        "bin_country", "channel", "merchant_category", "promo_used",
        "avs_match", "cvv_result", "three_ds_flag", "shipping_distance_km",
        "account_age_days", "total_transactions_user", "avg_amount_user",
        "ip_address", "device_id", "device_type", "location", "date"
    ]
    
    sample_row = [
        "TXN-001", "CUST-100", "150.00", "USD", "US", "US", "web",
        "electronics", "false", "true", "true", "false", "100.5",
        "30", "5", "120.00", "192.168.1.1", "DEV-001", "mobile", "New York", "2026-01-15"
    ]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerow(sample_row)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transaction_template.csv"}
    )