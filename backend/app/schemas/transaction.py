from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


class TransactionChannel(str, Enum):
    WEB = "web"
    MOBILE = "mobile"
    API = "api"
    POS = "pos"


class TransactionBase(BaseModel):
    customer_id: str = Field(..., min_length=1, max_length=50)
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")
    country: Optional[str] = None
    bin_country: Optional[str] = None
    channel: TransactionChannel = TransactionChannel.WEB
    merchant_category: Optional[str] = None
    promo_used: bool = False
    avs_match: bool = True
    cvv_result: bool = True
    three_ds_flag: bool = False
    shipping_distance_km: Optional[Decimal] = None
    account_age_days: Optional[int] = Field(default=None, ge=0)
    total_transactions_user: Optional[int] = Field(default=None, ge=0)
    avg_amount_user: Optional[Decimal] = Field(default=None, ge=0)
    ip_address: Optional[str] = None
    device_id: Optional[str] = None
    device_type: Optional[str] = None
    location: Optional[str] = None


class TransactionCreate(TransactionBase):
    transaction_id: str = Field(..., min_length=1, max_length=50)


class TransactionCreateBatch(BaseModel):
    transactions: List[TransactionCreate]


class TransactionUpdate(BaseModel):
    is_fraud: Optional[bool] = None


class TransactionResponse(BaseModel):
    id: int
    transaction_id: str
    customer_id: str
    amount: Decimal
    currency: str
    country: Optional[str]
    bin_country: Optional[str]
    channel: TransactionChannel
    merchant_category: Optional[str]
    promo_used: bool
    avs_match: bool
    cvv_result: bool
    three_ds_flag: bool
    shipping_distance_km: Optional[Decimal]
    account_age_days: Optional[int]
    total_transactions_user: Optional[int]
    avg_amount_user: Optional[Decimal]
    ip_address: Optional[str]
    device_id: Optional[str]
    device_type: Optional[str]
    location: Optional[str]
    is_fraud: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionDetail(TransactionResponse):
    risk_assessment: Optional["RiskAssessmentResponse"] = None
    alerts: List["AlertResponse"] = []


class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class TransactionFilter(BaseModel):
    customer_id: Optional[str] = None
    transaction_id: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    risk_level: Optional[str] = None
    is_fraud: Optional[bool] = None
    channel: Optional[TransactionChannel] = None
    country: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


# Forward references
from app.schemas.risk import RiskAssessmentResponse
from app.schemas.alert import AlertResponse

TransactionDetail.model_rebuild()