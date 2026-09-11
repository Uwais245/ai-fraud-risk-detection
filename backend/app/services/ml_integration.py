import os
import sys
import logging
from typing import Dict, Any, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)

# Add ml_engine to path
ml_engine_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ml_engine")
if ml_engine_path not in sys.path:
    sys.path.insert(0, ml_engine_path)

# Try to import the ML engine
try:
    from ml_engine.risk_engine import generate_final_decision
    ML_ENGINE_AVAILABLE = True
    logger.info("ML Engine loaded successfully")
except ImportError as e:
    ML_ENGINE_AVAILABLE = False
    logger.warning(f"ML Engine not available: {e}. Using fallback rule-based scoring.")


class MLIntegrationService:
    """Service to integrate with the ML Engine (Isolation Forest + Rules)"""
    
    def __init__(self):
        self.ml_available = ML_ENGINE_AVAILABLE
        self.model_path = os.path.join(ml_engine_path, "saved_models")
    
    def score_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a transaction using the ML engine.
        Falls back to rule-only scoring if ML engine is not available.
        """
        if self.ml_available:
            try:
                return self._score_with_ml_engine(transaction_data)
            except Exception as e:
                logger.error(f"ML Engine scoring failed: {e}. Falling back to rules.")
                return self._score_with_rules_only(transaction_data)
        else:
            return self._score_with_rules_only(transaction_data)
    
    def _score_with_ml_engine(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use the full ML engine (Isolation Forest + Business Rules)"""
        # Prepare data in the format expected by the ML engine
        ml_input = self._prepare_ml_input(transaction_data)
        
        # Call the ML engine
        result = generate_final_decision(ml_input)
        
        # Convert Decimal values to float for JSON serialization
        return self._normalize_result(result)
    
    def _score_with_rules_only(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback: Rule-based scoring only"""
        rule_score, flags = self._evaluate_business_rules(transaction_data)
        
        # Use rule score as final score (no ML component)
        final_score = float(rule_score)
        
        if final_score >= 71:
            risk_level = "HIGH"
            decision = "REVIEW"
        elif final_score >= 31:
            risk_level = "MEDIUM"
            decision = "APPROVE"
        else:
            risk_level = "LOW"
            decision = "APPROVE"
        
        return {
            "transaction_id": transaction_data.get("transaction_id", "UNKNOWN"),
            "ml_anomaly_score": 0.0,
            "rule_engine_score": float(rule_score),
            "final_risk_score": round(final_score, 2),
            "risk_level": risk_level,
            "decision": decision,
            "risk_flags": flags,
            "ai_explanation": None
        }
    
    def _prepare_ml_input(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform transaction data to ML engine input format"""
        return {
            "transaction_id": transaction_data.get("transaction_id", "UNKNOWN"),
            "account_age_days": transaction_data.get("account_age_days", 999),
            "total_transactions_user": transaction_data.get("total_transactions_user", 0),
            "avg_amount_user": float(transaction_data.get("avg_amount_user", 0)),
            "amount": float(transaction_data.get("amount", 0)),
            "country": transaction_data.get("country", "US"),
            "bin_country": transaction_data.get("bin_country", "US"),
            "channel": transaction_data.get("channel", "web"),
            "merchant_category": transaction_data.get("merchant_category", "other"),
            "promo_used": int(transaction_data.get("promo_used", False)),
            "avs_match": int(transaction_data.get("avs_match", True)),
            "cvv_result": int(transaction_data.get("cvv_result", True)),
            "three_ds_flag": int(transaction_data.get("three_ds_flag", False)),
            "shipping_distance_km": float(transaction_data.get("shipping_distance_km", 0)),
        }
    
    def _evaluate_business_rules(self, transaction_data: Dict[str, Any]) -> tuple:
        """Evaluate hard business rules (same logic as risk_engine.py)"""
        rule_score = 0
        flags = []
        
        amount = float(transaction_data.get("amount", 0))
        account_age = transaction_data.get("account_age_days", 999)
        
        # Rule 1: Unusually high amount
        if amount > 1000:
            rule_score += 40
            flags.append("High transaction amount (>$1000)")
        
        # Rule 2: New account making large purchase
        if account_age < 14 and amount > 500:
            rule_score += 30
            flags.append("New account high-value transaction")
        
        # Rule 3: CVV or AVS mismatch
        if transaction_data.get("cvv_result") == 0 or transaction_data.get("avs_match") == 0:
            rule_score += 50
            flags.append("CVV or Address Verification failure")
        
        # Rule 4: High velocity (multiple transactions in short time)
        # This would need transaction history - simplified here
        txn_count = transaction_data.get("total_transactions_user", 0)
        if txn_count > 10 and amount > 500:
            rule_score += 20
            flags.append("High transaction velocity")
        
        # Rule 5: International transaction from new account
        if account_age < 30 and transaction_data.get("country") != transaction_data.get("bin_country"):
            rule_score += 25
            flags.append("Cross-border transaction from new account")
        
        # Cap rule score at 100
        rule_score = min(rule_score, 100)
        return rule_score, flags
    
    def _normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize result for consistent output"""
        normalized = {}
        for key, value in result.items():
            if isinstance(value, Decimal):
                normalized[key] = float(value)
            elif isinstance(value, (list, dict, str, int, float, bool)) or value is None:
                normalized[key] = value
            else:
                normalized[key] = str(value)
        return normalized
    
    def batch_score(self, transactions: list) -> list:
        """Score multiple transactions"""
        return [self.score_transaction(txn) for txn in transactions]
    
    def is_healthy(self) -> bool:
        """Check if ML engine is available"""
        return self.ml_available and os.path.exists(
            os.path.join(self.model_path, "isolation_forest.pkl")
        )


# Singleton instance
ml_service = MLIntegrationService()