from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.models.transaction import Transaction
from app.models.risk_assessment import RiskAssessment
from app.models.alert import Alert, AlertStatus
from app.models.customer_profile import CustomerRiskProfile
from app.models.feedback import Feedback, FeedbackType
from app.schemas.investigation import (
    CustomerProfile, RelatedTransaction, DeviceInfo, IPInfo,
    LocationInfo, InvestigationDetail, InvestigationNoteResponse
)


class InvestigationService:
    """Service for transaction investigation"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_investigation_detail(self, transaction_id: str) -> Optional[InvestigationDetail]:
        """Get complete investigation detail for a transaction"""
        # Get transaction with risk assessment
        stmt = (
            select(Transaction, RiskAssessment)
            .outerjoin(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .where(Transaction.transaction_id == transaction_id)
        )
        result = await self.db.execute(stmt)
        row = result.first()
        
        if not row:
            return None
        
        transaction, risk_assessment = row
        
        # Get customer profile
        customer_profile = await self._get_customer_profile(transaction.customer_id)
        
        # Get related transactions
        related_transactions = await self._get_related_transactions(transaction)
        
        # Get devices
        devices = await self._get_device_info(transaction)
        
        # Get IPs
        ips = await self._get_ip_info(transaction)
        
        # Get locations
        locations = await self._get_location_info(transaction)
        
        # Get alerts
        alerts = await self._get_alerts_for_transaction(transaction_id)
        
        # Get risk flags
        risk_flags = risk_assessment.risk_flags if risk_assessment else []
        
        # Get AI explanation
        ai_explanation = risk_assessment.ai_explanation if risk_assessment else None
        
        # Get investigation notes
        investigation_notes = await self._get_investigation_notes(transaction_id)
        
        # Build transaction detail
        from app.schemas.transaction import TransactionDetail
        txn_detail = TransactionDetail(
            id=transaction.id,
            transaction_id=transaction.transaction_id,
            customer_id=transaction.customer_id,
            amount=transaction.amount,
            currency=transaction.currency,
            country=transaction.country,
            bin_country=transaction.bin_country,
            channel=transaction.channel,
            merchant_category=transaction.merchant_category,
            promo_used=transaction.promo_used,
            avs_match=transaction.avs_match,
            cvv_result=transaction.cvv_result,
            three_ds_flag=transaction.three_ds_flag,
            shipping_distance_km=transaction.shipping_distance_km,
            account_age_days=transaction.account_age_days,
            total_transactions_user=transaction.total_transactions_user,
            avg_amount_user=transaction.avg_amount_user,
            ip_address=transaction.ip_address,
            device_id=transaction.device_id,
            device_type=transaction.device_type,
            location=transaction.location,
            is_fraud=transaction.is_fraud,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
            risk_assessment=risk_assessment
        )
        
        return InvestigationDetail(
            transaction=txn_detail,
            customer_profile=customer_profile,
            related_transactions=related_transactions,
            devices=devices,
            ips=ips,
            locations=locations,
            risk_factors=risk_flags,
            ai_explanation=ai_explanation,
            alerts=alerts,
            investigation_notes=investigation_notes
        )
    
    async def _get_customer_profile(self, customer_id: str) -> CustomerProfile:
        """Get or create customer risk profile"""
        stmt = select(CustomerRiskProfile).where(CustomerRiskProfile.customer_id == customer_id)
        result = await self.db.execute(stmt)
        profile = result.scalar_one_or_none()
        
        if not profile:
            # Create profile from transaction data
            stmt = (
                select(
                    func.count(Transaction.id).label("total_txns"),
                    func.count(Transaction.id).filter(Transaction.is_fraud == True).label("fraud_txns"),
                    func.array_agg(Transaction.device_id).label("devices"),
                    func.array_agg(Transaction.ip_address).label("ips"),
                    func.array_agg(Transaction.location).label("locations"),
                    func.max(Transaction.created_at).label("last_txn")
                )
                .where(Transaction.customer_id == customer_id)
            )
            result = await self.db.execute(stmt)
            row = result.first()
            
            devices = list(set([d for d in (row.devices or []) if d])) if row else []
            ips = list(set([ip for ip in (row.ips or []) if ip])) if row else []
            locations = list(set([loc for loc in (row.locations or []) if loc])) if row else []
            
            risk_score = 0.0
            if row and row.total_txns:
                fraud_rate = (row.fraud_txns or 0) / row.total_txns
                risk_score = min(fraud_rate * 100, 100)
            
            risk_level = "HIGH" if risk_score >= 71 else "MEDIUM" if risk_score >= 31 else "LOW"
            
            profile = CustomerRiskProfile(
                customer_id=customer_id,
                risk_level=risk_level,
                risk_score=risk_score,
                total_transactions=row.total_txns or 0,
                suspicious_transactions=row.fraud_txns or 0,
                devices_used=devices,
                ips_used=ips,
                locations_used=locations,
                previous_fraud_reports=row.fraud_txns or 0,
                last_transaction_at=row.last_txn if row else None
            )
            self.db.add(profile)
            await self.db.commit()
            await self.db.refresh(profile)
        
        return CustomerProfile(
            customer_id=profile.customer_id,
            risk_level=profile.risk_level,
            risk_score=float(profile.risk_score),
            total_transactions=profile.total_transactions,
            suspicious_transactions=profile.suspicious_transactions,
            devices_used=profile.devices_used,
            ips_used=profile.ips_used,
            locations_used=profile.locations_used,
            previous_fraud_reports=profile.previous_fraud_reports,
            last_transaction_at=profile.last_transaction_at
        )
    
    async def _get_related_transactions(self, transaction: Transaction) -> List[RelatedTransaction]:
        """Find transactions related by device, IP, or customer"""
        stmt = (
            select(Transaction, RiskAssessment)
            .outerjoin(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .where(
                and_(
                    Transaction.id != transaction.id,
                    or_(
                        Transaction.customer_id == transaction.customer_id,
                        Transaction.device_id == transaction.device_id,
                        Transaction.ip_address == transaction.ip_address
                    )
                )
            )
            .order_by(desc(Transaction.created_at))
            .limit(20)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        
        related = []
        for txn, risk in rows:
            relationship_type = "same_customer"
            if txn.device_id == transaction.device_id:
                relationship_type = "same_device"
            elif txn.ip_address == transaction.ip_address:
                relationship_type = "same_ip"
            
            risk_score = float(risk.final_risk_score) if risk else 0.0
            risk_level = "HIGH" if risk_score >= 71 else "MEDIUM" if risk_score >= 31 else "LOW"
            
            related.append(RelatedTransaction(
                transaction_id=txn.transaction_id,
                amount=txn.amount,
                risk_level=risk_level,
                risk_score=risk_score,
                created_at=txn.created_at,
                relationship_type=relationship_type
            ))
        
        return related
    
    async def _get_device_info(self, transaction: Transaction) -> List[DeviceInfo]:
        """Get device information"""
        if not transaction.device_id:
            return []
        
        stmt = (
            select(
                Transaction.device_id,
                Transaction.device_type,
                func.min(Transaction.created_at).label("first_seen"),
                func.max(Transaction.created_at).label("last_seen"),
                func.count(Transaction.id).label("txn_count"),
                func.max(RiskAssessment.risk_level).label("max_risk"),
                func.array_agg(Transaction.customer_id).label("customers")
            )
            .outerjoin(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .where(Transaction.device_id == transaction.device_id)
            .group_by(Transaction.device_id, Transaction.device_type)
        )
        result = await self.db.execute(stmt)
        row = result.first()
        
        if not row:
            return []
        
        customers = list(set([c for c in (row.customers or []) if c]))
        risk_level = row.max_risk or "LOW"
        
        return [DeviceInfo(
            device_id=row.device_id,
            device_type=row.device_type,
            first_seen=row.first_seen,
            last_seen=row.last_seen,
            transaction_count=row.txn_count,
            risk_level=risk_level,
            associated_customers=customers
        )]
    
    async def _get_ip_info(self, transaction: Transaction) -> List[IPInfo]:
        """Get IP address information"""
        if not transaction.ip_address:
            return []
        
        stmt = (
            select(
                Transaction.ip_address,
                Transaction.country,
                Transaction.location,
                func.min(Transaction.created_at).label("first_seen"),
                func.max(Transaction.created_at).label("last_seen"),
                func.count(Transaction.id).label("txn_count"),
                func.max(RiskAssessment.risk_level).label("max_risk"),
                func.array_agg(Transaction.customer_id).label("customers")
            )
            .outerjoin(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .where(Transaction.ip_address == transaction.ip_address)
            .group_by(Transaction.ip_address, Transaction.country, Transaction.location)
        )
        result = await self.db.execute(stmt)
        row = result.first()
        
        if not row:
            return []
        
        customers = list(set([c for c in (row.customers or []) if c]))
        risk_level = row.max_risk or "LOW"
        
        return [IPInfo(
            ip_address=row.ip_address,
            country=row.country,
            city=row.location,
            is_proxy=False,  # Would need external service
            is_vpn=False,
            first_seen=row.first_seen,
            last_seen=row.last_seen,
            transaction_count=row.txn_count,
            risk_level=risk_level,
            associated_customers=customers
        )]
    
    async def _get_location_info(self, transaction: Transaction) -> List[LocationInfo]:
        """Get location information"""
        if not transaction.location:
            return []
        
        stmt = (
            select(
                Transaction.location,
                Transaction.country,
                func.min(Transaction.created_at).label("first_seen"),
                func.max(Transaction.created_at).label("last_seen"),
                func.count(Transaction.id).label("txn_count"),
                func.max(RiskAssessment.risk_level).label("max_risk")
            )
            .outerjoin(RiskAssessment, Transaction.transaction_id == RiskAssessment.transaction_id)
            .where(Transaction.location == transaction.location)
            .group_by(Transaction.location, Transaction.country)
        )
        result = await self.db.execute(stmt)
        row = result.first()
        
        if not row:
            return []
        
        risk_level = row.max_risk or "LOW"
        
        return [LocationInfo(
            location=row.location,
            country=row.country,
            first_seen=row.first_seen,
            last_seen=row.last_seen,
            transaction_count=row.txn_count,
            risk_level=risk_level
        )]
    
    async def _get_alerts_for_transaction(self, transaction_id: str) -> List:
        """Get alerts for a transaction"""
        from app.schemas.alert import AlertSummary
        stmt = (
            select(Alert)
            .where(Alert.transaction_id == transaction_id)
            .order_by(desc(Alert.created_at))
        )
        result = await self.db.execute(stmt)
        alerts = result.scalars().all()
        
        return [
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
    
    async def _get_investigation_notes(self, transaction_id: str) -> Optional[str]:
        """Get investigation notes (stored in alert.investigation_notes)"""
        stmt = (
            select(Alert.investigation_notes)
            .where(and_(
                Alert.transaction_id == transaction_id,
                Alert.investigation_notes.isnot(None)
            ))
            .order_by(desc(Alert.created_at))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        notes = result.scalar_one_or_none()
        return notes
    
    async def add_investigation_note(self, transaction_id: str, note: str, user_id: int) -> Alert:
        """Add investigation note to the latest alert for a transaction"""
        stmt = (
            select(Alert)
            .where(Alert.transaction_id == transaction_id)
            .order_by(desc(Alert.created_at))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        alert = result.scalar_one_or_none()
        
        if not alert:
            # Create a new alert for this transaction if none exists
            alert = Alert(
                transaction_id=transaction_id,
                severity="LOW",
                reason="Investigation note added",
                status=AlertStatus.INVESTIGATING,
                assigned_to=user_id,
                investigation_notes=note
            )
            self.db.add(alert)
        else:
            existing_notes = alert.investigation_notes or ""
            alert.investigation_notes = f"{existing_notes}\n\n[{datetime.utcnow().isoformat()}] User {user_id}: {note}"
            alert.status = AlertStatus.INVESTIGATING
            alert.assigned_to = user_id
        
        await self.db.commit()
        await self.db.refresh(alert)
        return alert