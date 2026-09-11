from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class CustomerProfile(BaseModel):
    customer_id: str
    risk_level: str
    risk_score: float
    total_transactions: int
    suspicious_transactions: int
    devices_used: List[str]
    ips_used: List[str]
    locations_used: List[str]
    previous_fraud_reports: int
    last_transaction_at: Optional[datetime]


class RelatedTransaction(BaseModel):
    transaction_id: str
    amount: Decimal
    risk_level: str
    risk_score: float
    created_at: datetime
    relationship_type: str  # same_device, same_ip, same_customer


class DeviceInfo(BaseModel):
    device_id: str
    device_type: Optional[str]
    first_seen: datetime
    last_seen: datetime
    transaction_count: int
    risk_level: str
    associated_customers: List[str]


class IPInfo(BaseModel):
    ip_address: str
    country: Optional[str]
    city: Optional[str]
    is_proxy: bool = False
    is_vpn: bool = False
    first_seen: datetime
    last_seen: datetime
    transaction_count: int
    risk_level: str
    associated_customers: List[str]


class LocationInfo(BaseModel):
    location: str
    country: Optional[str]
    first_seen: datetime
    last_seen: datetime
    transaction_count: int
    risk_level: str


class InvestigationDetail(BaseModel):
    transaction: "TransactionDetail"
    customer_profile: CustomerProfile
    related_transactions: List[RelatedTransaction]
    devices: List[DeviceInfo]
    ips: List[IPInfo]
    locations: List[LocationInfo]
    risk_factors: List[str]
    ai_explanation: Optional[str]
    alerts: List["AlertSummary"]
    investigation_notes: Optional[str]


class InvestigationNoteCreate(BaseModel):
    note: str


class InvestigationNoteResponse(BaseModel):
    id: int
    transaction_id: str
    note: str
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Forward references
from app.schemas.transaction import TransactionDetail
from app.schemas.alert import AlertSummary

InvestigationDetail.model_rebuild()