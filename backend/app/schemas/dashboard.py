from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class DashboardStats(BaseModel):
    total_transactions: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    confirmed_fraud: int
    false_positives: int
    open_alerts: int
    avg_risk_score: float


class TrendPoint(BaseModel):
    date: str
    total_transactions: int
    high_risk: int
    medium_risk: int
    low_risk: int
    avg_risk_score: float


class TransactionTrends(BaseModel):
    trends: List[TrendPoint]


class RiskDistribution(BaseModel):
    low: int
    medium: int
    high: int


class SuspiciousEntity(BaseModel):
    id: str
    name: str
    risk_score: float
    transaction_count: int
    risk_level: str


class SuspiciousCustomers(BaseModel):
    customers: List[SuspiciousEntity]


class SuspiciousDevices(BaseModel):
    devices: List[SuspiciousEntity]


class AlertSummary(BaseModel):
    id: int
    transaction_id: str
    severity: str
    reason: str
    status: str
    created_at: datetime
    risk_score: int


class RecentAlerts(BaseModel):
    alerts: List[AlertSummary]


class DashboardData(BaseModel):
    stats: DashboardStats
    trends: TransactionTrends
    risk_distribution: RiskDistribution
    suspicious_customers: SuspiciousCustomers
    suspicious_devices: SuspiciousDevices
    recent_alerts: RecentAlerts