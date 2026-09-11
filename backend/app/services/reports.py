import csv
import io
from datetime import datetime, timedelta
from typing import List, Optional, BinaryIO
from decimal import Decimal
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction
from app.models.risk_assessment import RiskAssessment
from app.models.alert import Alert, AlertStatus
from app.models.feedback import Feedback, FeedbackType
from app.schemas.reports import ReportType, ReportFormat


class ReportsService:
    """Service for generating reports"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_report(
        self, 
        report_type: ReportType, 
        period: str, 
        format: ReportFormat
    ) -> bytes:
        """Generate a report and return as bytes"""
        # Parse period
        if report_type in [ReportType.DAILY_FRAUD]:
            date = datetime.strptime(period, "%Y-%m-%d")
            start_date = date
            end_date = date + timedelta(days=1)
        elif report_type in [ReportType.MONTHLY_FRAUD]:
            date = datetime.strptime(period, "%Y-%m")
            start_date = date
            if date.month == 12:
                end_date = date.replace(year=date.year + 1, month=1)
            else:
                end_date = date.replace(month=date.month + 1)
        else:
            # Default to last 30 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
        
        # Generate data based on report type
        if report_type == ReportType.DAILY_FRAUD:
            data = await self._get_daily_fraud_data(start_date, end_date)
            headers = ["Transaction ID", "Customer ID", "Amount", "Risk Score", "Risk Level", "Decision", "Flags", "Status", "Created At"]
        elif report_type == ReportType.MONTHLY_FRAUD:
            data = await self._get_monthly_fraud_data(start_date, end_date)
            headers = ["Date", "Total Transactions", "High Risk", "Medium Risk", "Low Risk", "Confirmed Fraud", "False Positives", "Avg Risk Score"]
        elif report_type == ReportType.HIGH_RISK_CUSTOMERS:
            data = await self._get_high_risk_customers(start_date, end_date)
            headers = ["Customer ID", "Risk Score", "Risk Level", "Total Transactions", "Suspicious Transactions", "Devices Used", "IPs Used", "Fraud Reports"]
        elif report_type == ReportType.HIGH_RISK_TRANSACTIONS:
            data = await self._get_high_risk_transactions(start_date, end_date)
            headers = ["Transaction ID", "Customer ID", "Amount", "Risk Score", "Risk Level", "Decision", "Flags", "Created At"]
        elif report_type == ReportType.CONFIRMED_FRAUD:
            data = await self._get_confirmed_fraud(start_date, end_date)
            headers = ["Transaction ID", "Customer ID", "Amount", "Risk Score", "Confirmed At", "Analyst"]
        elif report_type == ReportType.FALSE_POSITIVES:
            data = await self._get_false_positives(start_date, end_date)
            headers = ["Transaction ID", "Customer ID", "Amount", "Risk Score", "Marked At", "Analyst"]
        elif report_type == ReportType.FRAUD_TRENDS:
            data = await self._get_fraud_trends(start_date, end_date)
            headers = ["Date", "Total Transactions", "High Risk", "Medium Risk", "Low Risk", "Avg Risk Score"]
        else:
            data = []
            headers = []
        
        # Format output
        if format == ReportFormat.CSV:
            return self._generate_csv(data, headers)
        else:
            return self._generate_pdf(data, headers, report_type.value, period)
    
    async def _get_daily_fraud_data(self, start: datetime, end: datetime) -> List[List]:
        stmt = (
            select(Transaction, RiskAssessment, Alert)
            .outerjoin(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .outerjoin(Alert, Transaction.transaction_id == Alert.transaction_id)
            .where(Transaction.created_at >= start, Transaction.created_at < end)
            .order_by(desc(Transaction.created_at))
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        
        data = []
        for txn, risk, alert in rows:
            data.append([
                txn.transaction_id,
                txn.customer_id,
                str(txn.amount),
                str(risk.final_risk_score) if risk else "N/A",
                risk.risk_level if risk else "N/A",
                risk.decision if risk else "N/A",
                ", ".join(risk.risk_flags) if risk and risk.risk_flags else "N/A",
                alert.status.value if alert else "N/A",
                txn.created_at.isoformat()
            ])
        return data
    
    async def _get_monthly_fraud_data(self, start: datetime, end: datetime) -> List[List]:
        stmt = (
            select(
                func.date(Transaction.created_at).label("date"),
                func.count(Transaction.id).label("total"),
                func.count(RiskAssessment.id).filter(RiskAssessment.risk_level == "HIGH").label("high"),
                func.count(RiskAssessment.id).filter(RiskAssessment.risk_level == "MEDIUM").label("medium"),
                func.count(RiskAssessment.id).filter(RiskAssessment.risk_level == "LOW").label("low"),
                func.count(Alert.id).filter(Alert.status == AlertStatus.CONFIRMED_FRAUD).label("confirmed"),
                func.count(Alert.id).filter(Alert.status == AlertStatus.FALSE_POSITIVE).label("false_pos"),
                func.avg(RiskAssessment.final_risk_score).label("avg_score")
            )
            .outerjoin(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .outerjoin(Alert, Transaction.transaction_id == Alert.transaction_id)
            .where(Transaction.created_at >= start, Transaction.created_at < end)
            .group_by(func.date(Transaction.created_at))
            .order_by(func.date(Transaction.created_at))
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        
        data = []
        for row in rows:
            data.append([
                row.date.isoformat() if row.date else "",
                row.total or 0,
                row.high or 0,
                row.medium or 0,
                row.low or 0,
                row.confirmed or 0,
                row.false_pos or 0,
                round(float(row.avg_score), 2) if row.avg_score else 0
            ])
        return data
    
    async def _get_high_risk_customers(self, start: datetime, end: datetime) -> List[List]:
        stmt = (
            select(
                Transaction.customer_id,
                func.avg(RiskAssessment.final_risk_score).label("avg_score"),
                func.count(Transaction.id).label("total_txns"),
                func.count(Transaction.id).filter(Transaction.is_fraud == True).label("fraud_txns"),
                func.array_agg(Transaction.device_id).label("devices"),
                func.array_agg(Transaction.ip_address).label("ips")
            )
            .join(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .where(Transaction.created_at >= start, Transaction.created_at < end)
            .group_by(Transaction.customer_id)
            .having(func.avg(RiskAssessment.final_risk_score) >= 71)
            .order_by(desc("avg_score"))
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        
        data = []
        for row in rows:
            devices = list(set([d for d in (row.devices or []) if d]))
            ips = list(set([ip for ip in (row.ips or []) if ip]))
            data.append([
                row.customer_id,
                round(float(row.avg_score), 2),
                "HIGH",
                row.total_txns,
                row.fraud_txns,
                len(devices),
                len(ips),
                row.fraud_txns
            ])
        return data
    
    async def _get_high_risk_transactions(self, start: datetime, end: datetime) -> List[List]:
        stmt = (
            select(Transaction, RiskAssessment)
            .join(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .where(
                Transaction.created_at >= start,
                Transaction.created_at < end,
                RiskAssessment.risk_level == "HIGH"
            )
            .order_by(desc(RiskAssessment.final_risk_score))
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        
        data = []
        for txn, risk in rows:
            data.append([
                txn.transaction_id,
                txn.customer_id,
                str(txn.amount),
                str(risk.final_risk_score),
                risk.risk_level,
                risk.decision,
                ", ".join(risk.risk_flags) if risk.risk_flags else "N/A",
                txn.created_at.isoformat()
            ])
        return data
    
    async def _get_confirmed_fraud(self, start: datetime, end: datetime) -> List[List]:
        stmt = (
            select(Transaction, RiskAssessment, Alert)
            .join(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .join(Alert, Transaction.transaction_id == Alert.transaction_id)
            .where(
                Alert.status == AlertStatus.CONFIRMED_FRAUD,
                Alert.resolved_at >= start,
                Alert.resolved_at < end
            )
            .order_by(desc(Alert.resolved_at))
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        
        data = []
        for txn, risk, alert in rows:
            data.append([
                txn.transaction_id,
                txn.customer_id,
                str(txn.amount),
                str(risk.final_risk_score),
                alert.resolved_at.isoformat() if alert.resolved_at else "",
                str(alert.assigned_to) if alert.assigned_to else "N/A"
            ])
        return data
    
    async def _get_false_positives(self, start: datetime, end: datetime) -> List[List]:
        stmt = (
            select(Transaction, RiskAssessment, Alert)
            .join(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .join(Alert, Transaction.transaction_id == Alert.transaction_id)
            .where(
                Alert.status == AlertStatus.FALSE_POSITIVE,
                Alert.resolved_at >= start,
                Alert.resolved_at < end
            )
            .order_by(desc(Alert.resolved_at))
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        
        data = []
        for txn, risk, alert in rows:
            data.append([
                txn.transaction_id,
                txn.customer_id,
                str(txn.amount),
                str(risk.final_risk_score),
                alert.resolved_at.isoformat() if alert.resolved_at else "",
                str(alert.assigned_to) if alert.assigned_to else "N/A"
            ])
        return data
    
    async def _get_fraud_trends(self, start: datetime, end: datetime) -> List[List]:
        return await self._get_monthly_fraud_data(start, end)
    
    def _generate_csv(self, data: List[List], headers: List[str]) -> bytes:
        """Generate CSV report"""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(data)
        return output.getvalue().encode("utf-8")
    
    def _generate_pdf(self, data: List[List], headers: List[str], report_type: str, period: str) -> bytes:
        """Generate PDF report (placeholder - would use reportlab or weasyprint in production)"""
        # For now, return a simple text-based PDF-like format
        # In production, use reportlab or weasyprint
        lines = [
            f"Fraud Detection Report",
            f"Type: {report_type}",
            f"Period: {period}",
            f"Generated: {datetime.utcnow().isoformat()}",
            "",
            " | ".join(headers),
            "-" * 80
        ]
        for row in data[:50]:  # Limit to 50 rows for text format
            lines.append(" | ".join(str(cell) for cell in row))
        
        if len(data) > 50:
            lines.append(f"\n... and {len(data) - 50} more rows")
        
        return "\n".join(lines).encode("utf-8")