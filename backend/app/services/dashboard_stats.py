from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from app.models.transaction import Transaction
from app.models.risk_assessment import RiskAssessment
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.user import User
from app.schemas.dashboard import (
    DashboardStats, TrendPoint, TransactionTrends, RiskDistribution,
    SuspiciousEntity, SuspiciousCustomers, SuspiciousDevices, AlertSummary, RecentAlerts
)


class DashboardService:
    """Service for generating dashboard statistics and charts"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_stats(self) -> DashboardStats:
        """Get KPI statistics for dashboard"""
        # Total transactions
        total_txns = await self.db.scalar(select(func.count(Transaction.id)))
        
        # Risk level counts
        high_risk = await self.db.scalar(
            select(func.count(RiskAssessment.id))
            .where(RiskAssessment.risk_level == "HIGH")
        )
        medium_risk = await self.db.scalar(
            select(func.count(RiskAssessment.id))
            .where(RiskAssessment.risk_level == "MEDIUM")
        )
        low_risk = await self.db.scalar(
            select(func.count(RiskAssessment.id))
            .where(RiskAssessment.risk_level == "LOW")
        )
        
        # Confirmed fraud / False positives
        confirmed_fraud = await self.db.scalar(
            select(func.count(Alert.id))
            .where(Alert.status == AlertStatus.CONFIRMED_FRAUD)
        )
        false_positives = await self.db.scalar(
            select(func.count(Alert.id))
            .where(Alert.status == AlertStatus.FALSE_POSITIVE)
        )
        
        # Open alerts
        open_alerts = await self.db.scalar(
            select(func.count(Alert.id))
            .where(Alert.status.in_([AlertStatus.NEW, AlertStatus.INVESTIGATING]))
        )
        
        # Average risk score
        avg_score = await self.db.scalar(
            select(func.avg(RiskAssessment.final_risk_score))
        )
        
        return DashboardStats(
            total_transactions=total_txns or 0,
            high_risk_count=high_risk or 0,
            medium_risk_count=medium_risk or 0,
            low_risk_count=low_risk or 0,
            confirmed_fraud=confirmed_fraud or 0,
            false_positives=false_positives or 0,
            open_alerts=open_alerts or 0,
            avg_risk_score=float(avg_score) if avg_score else 0.0
        )
    
    async def get_trends(self, days: int = 7, interval: str = "1d") -> TransactionTrends:
        """Get transaction trends over time"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Group by date
        stmt = (
            select(
                func.date(Transaction.created_at).label("date"),
                func.count(Transaction.id).label("total"),
                func.count(RiskAssessment.id).filter(RiskAssessment.risk_level == "HIGH").label("high"),
                func.count(RiskAssessment.id).filter(RiskAssessment.risk_level == "MEDIUM").label("medium"),
                func.count(RiskAssessment.id).filter(RiskAssessment.risk_level == "LOW").label("low"),
                func.avg(RiskAssessment.final_risk_score).label("avg_score")
            )
            .outerjoin(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .where(Transaction.created_at >= start_date)
            .group_by(func.date(Transaction.created_at))
            .order_by(func.date(Transaction.created_at))
        )
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        trends = []
        for row in rows:
            trends.append(TrendPoint(
                date=row.date.isoformat() if row.date else "",
                total_transactions=row.total or 0,
                high_risk=row.high or 0,
                medium_risk=row.medium or 0,
                low_risk=row.low or 0,
                avg_risk_score=float(row.avg_score) if row.avg_score else 0.0
            ))
        
        return TransactionTrends(trends=trends)
    
    async def get_risk_distribution(self) -> RiskDistribution:
        """Get risk level distribution"""
        low = await self.db.scalar(
            select(func.count(RiskAssessment.id))
            .where(RiskAssessment.risk_level == "LOW")
        )
        medium = await self.db.scalar(
            select(func.count(RiskAssessment.id))
            .where(RiskAssessment.risk_level == "MEDIUM")
        )
        high = await self.db.scalar(
            select(func.count(RiskAssessment.id))
            .where(RiskAssessment.risk_level == "HIGH")
        )
        
        return RiskDistribution(
            low=low or 0,
            medium=medium or 0,
            high=high or 0
        )
    
    async def get_suspicious_customers(self, limit: int = 10) -> SuspiciousCustomers:
        """Get top suspicious customers by risk score"""
        stmt = (
            select(
                Transaction.customer_id,
                func.avg(RiskAssessment.final_risk_score).label("avg_score"),
                func.count(Transaction.id).label("txn_count"),
                func.max(RiskAssessment.risk_level).label("max_risk")
            )
            .join(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .group_by(Transaction.customer_id)
            .order_by(desc("avg_score"))
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        customers = []
        for row in rows:
            risk_level = "HIGH" if row.avg_score >= 71 else "MEDIUM" if row.avg_score >= 31 else "LOW"
            customers.append(SuspiciousEntity(
                id=row.customer_id,
                name=row.customer_id,
                risk_score=float(row.avg_score),
                transaction_count=row.txn_count,
                risk_level=risk_level
            ))
        
        return SuspiciousCustomers(customers=customers)
    
    async def get_suspicious_devices(self, limit: int = 10) -> SuspiciousDevices:
        """Get top suspicious devices by risk score"""
        stmt = (
            select(
                Transaction.device_id,
                func.avg(RiskAssessment.final_risk_score).label("avg_score"),
                func.count(Transaction.id).label("txn_count"),
                func.max(RiskAssessment.risk_level).label("max_risk")
            )
            .join(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .where(Transaction.device_id.isnot(None))
            .group_by(Transaction.device_id)
            .order_by(desc("avg_score"))
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        rows = result.all()
        
        devices = []
        for row in rows:
            risk_level = "HIGH" if row.avg_score >= 71 else "MEDIUM" if row.avg_score >= 31 else "LOW"
            devices.append(SuspiciousEntity(
                id=row.device_id,
                name=row.device_id,
                risk_score=float(row.avg_score),
                transaction_count=row.txn_count,
                risk_level=risk_level
            ))
        
        return SuspiciousDevices(devices=devices)
    
    async def get_recent_alerts(self, limit: int = 20) -> RecentAlerts:
        """Get recent alerts"""
        stmt = (
            select(Alert)
            .order_by(desc(Alert.created_at))
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        alerts = result.scalars().all()
        
        alert_summaries = [
            AlertSummary(
                id=alert.id,
                transaction_id=alert.transaction_id,
                severity=alert.severity.value,
                reason=alert.reason,
                status=alert.status.value,
                created_at=alert.created_at,
                risk_score=alert.risk_score
            )
            for alert in alerts
        ]
        
        return RecentAlerts(alerts=alert_summaries)