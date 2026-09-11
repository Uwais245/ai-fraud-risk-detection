from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class RiskLevel(str):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Decision(str):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class RiskScoreRequest(BaseModel):
    transaction_id: str
    customer_id: str
    amount: Decimal
    currency: str = "USD"
    country: Optional[str] = None
    bin_country: Optional[str] = None
    channel: str = "web"
    merchant_category: Optional[str] = None
    promo_used: bool = False
    avs_match: bool = True
    cvv_result: bool = True
    three_ds_flag: bool = False
    shipping_distance_km: Optional[Decimal] = None
    account_age_days: Optional[int] = None
    total_transactions_user: Optional[int] = None
    avg_amount_user: Optional[Decimal] = None
    ip_address: Optional[str] = None
    device_id: Optional[str] = None
    device_type: Optional[str] = None
    location: Optional[str] = None


class RiskScoreBatchRequest(BaseModel):
    transactions: List[RiskScoreRequest]


class RiskAssessmentResponse(BaseModel):
    id: int
    transaction_id: str
    ml_anomaly_score: Optional[Decimal]
    rule_engine_score: Optional[Decimal]
    customer_behavior_score: Optional[Decimal]
    final_risk_score: Decimal
    risk_level: str
    decision: str
    risk_flags: List[str]
    ai_explanation: Optional[str]
    assessed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RiskFlagsResponse(BaseModel):
    flags: List[str]
    total_count: int