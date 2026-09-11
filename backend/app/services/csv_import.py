import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Tuple
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.transaction import Transaction
from app.services.ml_integration import ml_service
from app.services.ai_integration import ai_service
from app.models.risk_assessment import RiskAssessment
from app.models.alert import Alert, AlertSeverity, AlertStatus


class CSVImportService:
    """Service for importing transactions from CSV"""
    
    # Expected CSV columns (flexible mapping)
    REQUIRED_COLUMNS = ["transaction_id", "customer_id", "amount"]
    OPTIONAL_COLUMNS = [
        "currency", "country", "bin_country", "channel", "merchant_category",
        "promo_used", "avs_match", "cvv_result", "three_ds_flag",
        "shipping_distance_km", "account_age_days", "total_transactions_user",
        "avg_amount_user", "ip_address", "device_id", "device_type",
        "location", "created_at"
    ]
    
    COLUMN_MAPPING = {
        "transaction_id": "transaction_id",
        "customer_id": "customer_id",
        "amount": "amount",
        "currency": "currency",
        "country": "country",
        "bin_country": "bin_country",
        "channel": "channel",
        "merchant_category": "merchant_category",
        "promo_used": "promo_used",
        "avs_match": "avs_match",
        "cvv_result": "cvv_result",
        "three_ds_flag": "three_ds_flag",
        "shipping_distance_km": "shipping_distance_km",
        "account_age_days": "account_age_days",
        "total_transactions_user": "total_transactions_user",
        "avg_amount_user": "avg_amount_user",
        "ip_address": "ip_address",
        "device_id": "device_id",
        "device_type": "device_type",
        "location": "location",
        "date": "created_at",
        "datetime": "created_at",
        "timestamp": "created_at",
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def import_csv(self, file_content: bytes, user_id: int) -> Dict[str, Any]:
        """
        Import transactions from CSV file.
        Returns summary of import results.
        """
        # Decode content
        try:
            text_content = file_content.decode("utf-8")
        except UnicodeDecodeError:
            text_content = file_content.decode("latin-1")
        
        # Parse CSV
        reader = csv.DictReader(io.StringIO(text_content))
        rows = list(reader)
        
        if not rows:
            return {"success": 0, "failed": 0, "errors": ["Empty CSV file"]}
        
        # Validate columns
        columns = reader.fieldnames or []
        missing_required = [col for col in self.REQUIRED_COLUMNS if col not in columns]
        if missing_required:
            return {
                "success": 0, 
                "failed": len(rows), 
                "errors": [f"Missing required columns: {', '.join(missing_required)}"]
            }
        
        # Process each row
        success = 0
        failed = 0
        errors = []
        
        for i, row in enumerate(rows):
            try:
                await self._process_row(row, user_id)
                success += 1
            except Exception as e:
                failed += 1
                errors.append(f"Row {i+2}: {str(e)}")
        
        await self.db.commit()
        
        return {
            "success": success,
            "failed": failed,
            "errors": errors[:50]  # Limit error messages
        }
    
    async def _process_row(self, row: Dict[str, str], user_id: int):
        """Process a single CSV row"""
        # Map columns
        txn_data = {}
        for csv_col, model_col in self.COLUMN_MAPPING.items():
            if csv_col in row and row[csv_col]:
                txn_data[model_col] = row[csv_col]
        
        # Validate required fields
        if not txn_data.get("transaction_id") or not txn_data.get("customer_id"):
            raise ValueError("Missing transaction_id or customer_id")
        
        # Check for duplicate
        stmt = select(Transaction).where(Transaction.transaction_id == txn_data["transaction_id"])
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError(f"Duplicate transaction_id: {txn_data['transaction_id']}")
        
        # Parse and convert fields
        txn_data = self._convert_fields(txn_data)
        
        # Create transaction
        transaction = Transaction(**txn_data)
        self.db.add(transaction)
        await self.db.flush()  # Get ID
        
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
            transaction_id=txn_data["transaction_id"],
            ml_anomaly_score=risk_result.get("ml_anomaly_score", 0),
            rule_engine_score=risk_result.get("rule_engine_score", 0),
            final_risk_score=risk_result["final_risk_score"],
            risk_level=risk_result["risk_level"],
            decision=risk_result["decision"],
            risk_flags=risk_result["risk_flags"],
            ai_explanation=ai_explanation
        )
        self.db.add(risk_assessment)
        
        # Create alert if high risk
        if risk_result["risk_level"] == "HIGH":
            alert = Alert(
                transaction_id=txn_data["transaction_id"],
                severity=AlertSeverity.HIGH,
                reason="; ".join(risk_result["risk_flags"][:3]),
                status=AlertStatus.NEW,
                risk_score=int(risk_result["final_risk_score"]),
                risk_flags=risk_result["risk_flags"],
                ai_explanation=ai_explanation
            )
            self.db.add(alert)
    
    def _convert_fields(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Convert string fields to appropriate types"""
        converted = {}
        
        for key, value in data.items():
            if not value or value.strip() == "":
                continue
            
            value = value.strip()
            
            if key == "amount":
                converted[key] = Decimal(value)
            elif key in ["shipping_distance_km", "avg_amount_user"]:
                converted[key] = Decimal(value)
            elif key in ["account_age_days", "total_transactions_user", "promo_used", "avs_match", "cvv_result", "three_ds_flag"]:
                converted[key] = int(value)
            elif key == "created_at":
                # Try multiple date formats
                for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y", "%m/%d/%Y"]:
                    try:
                        converted[key] = datetime.strptime(value, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    converted[key] = datetime.utcnow()
            elif key in ["promo_used", "avs_match", "cvv_result", "three_ds_flag"]:
                # Handle boolean-like strings
                converted[key] = value.lower() in ["true", "1", "yes", "y", "t"]
            else:
                converted[key] = value
        
        # Set defaults
        converted.setdefault("currency", "USD")
        converted.setdefault("channel", "web")
        converted.setdefault("promo_used", False)
        converted.setdefault("avs_match", True)
        converted.setdefault("cvv_result", True)
        converted.setdefault("three_ds_flag", False)
        
        return converted