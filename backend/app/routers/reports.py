from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io
from app.core.database import get_db
from app.core.deps import get_current_active_user, require_analyst
from app.models.user import User
from app.services.reports import ReportsService
from app.schemas.reports import (
    ReportType, ReportFormat, ReportRequest, ReportResponse,
    ReportTemplate, ReportTemplatesResponse
)

router = APIRouter()


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Generate a fraud report"""
    service = ReportsService(db)
    report_data = await service.generate_report(
        request.report_type,
        request.period,
        request.format
    )
    
    # In production, save to file storage and return download URL
    # For now, return the data directly
    import base64
    import uuid
    from datetime import datetime, timedelta
    
    report_id = str(uuid.uuid4())
    
    # Determine media type and filename
    if request.format == ReportFormat.CSV:
        media_type = "text/csv"
        filename = f"{request.report_type.value}_{request.period}.csv"
    else:
        media_type = "application/pdf"
        filename = f"{request.report_type.value}_{request.period}.pdf"
    
    return ReportResponse(
        report_id=report_id,
        download_url=f"/api/v1/reports/download/{report_id}",
        expires_at=datetime.utcnow() + timedelta(hours=1),
        report_type=request.report_type,
        format=request.format,
        generated_at=datetime.utcnow()
    )


@router.get("/download/{report_id}")
async def download_report(
    report_id: str,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Download a generated report"""
    # In production, retrieve from file storage
    # For now, return a placeholder
    raise HTTPException(status_code=404, detail="Report not found. Use POST /generate to create.")


@router.post("/generate/stream")
async def generate_report_stream(
    request: ReportRequest,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Generate and stream a report directly"""
    service = ReportsService(db)
    report_data = await service.generate_report(
        request.report_type,
        request.period,
        request.format
    )
    
    if request.format == ReportFormat.CSV:
        media_type = "text/csv"
        filename = f"{request.report_type.value}_{request.period}.csv"
    else:
        media_type = "application/pdf"
        filename = f"{request.report_type.value}_{request.period}.pdf"
    
    return StreamingResponse(
        io.BytesIO(report_data),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/templates", response_model=ReportTemplatesResponse)
async def get_report_templates(
    current_user: User = Depends(require_analyst)
):
    """Get available report templates"""
    templates = [
        ReportTemplate(
            type=ReportType.DAILY_FRAUD,
            name="Daily Fraud Activity",
            description="All transactions with risk scores for a specific day",
            parameters=["period (YYYY-MM-DD)"]
        ),
        ReportTemplate(
            type=ReportType.MONTHLY_FRAUD,
            name="Monthly Fraud Summary",
            description="Aggregated fraud statistics by day for a month",
            parameters=["period (YYYY-MM)"]
        ),
        ReportTemplate(
            type=ReportType.HIGH_RISK_CUSTOMERS,
            name="High Risk Customers",
            description="Customers with HIGH risk level and their details",
            parameters=["period (YYYY-MM-DD or YYYY-MM)"]
        ),
        ReportTemplate(
            type=ReportType.HIGH_RISK_TRANSACTIONS,
            name="High Risk Transactions",
            description="All transactions with HIGH risk level",
            parameters=["period (YYYY-MM-DD or YYYY-MM)"]
        ),
        ReportTemplate(
            type=ReportType.CONFIRMED_FRAUD,
            name="Confirmed Fraud Cases",
            description="Transactions confirmed as fraud by analysts",
            parameters=["period (YYYY-MM-DD or YYYY-MM)"]
        ),
        ReportTemplate(
            type=ReportType.FALSE_POSITIVES,
            name="False Positives",
            description="Transactions marked as false positives",
            parameters=["period (YYYY-MM-DD or YYYY-MM)"]
        ),
        ReportTemplate(
            type=ReportType.FRAUD_TRENDS,
            name="Fraud Trends",
            description="Time-series fraud trends and statistics",
            parameters=["period (YYYY-MM-DD or YYYY-MM)"]
        ),
    ]
    
    return ReportTemplatesResponse(templates=templates)