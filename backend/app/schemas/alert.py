from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    NEW = "NEW"
    INVESTIGATING = "INVESTIGATING"
    CONFIRMED_FRAUD = "CONFIRMED_FRAUD"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    RESOLVED = "RESOLVED"


class AlertBase(BaseModel):
    transaction_id: str
    severity: AlertSeverity
    reason: str
    risk_score: int
    risk_flags: List[str] = []
    ai_explanation: Optional[str] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    assigned_to: Optional[int] = None
    investigation_notes: Optional[str] = None


class AlertResponse(BaseModel):
    id: int
    transaction_id: str
    severity: AlertSeverity
    reason: str
    status: AlertStatus
    assigned_to: Optional[int]
    risk_score: int
    risk_flags: List[str]
    ai_explanation: Optional[str]
    investigation_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class AlertSummary(BaseModel):
    id: int
    transaction_id: str
    severity: str
    reason: str
    status: str
    created_at: datetime
    risk_score: int


class AlertListResponse(BaseModel):
    alerts: List[AlertResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class AlertFilter(BaseModel):
    status: Optional[AlertStatus] = None
    severity: Optional[AlertSeverity] = None
    assigned_to: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)