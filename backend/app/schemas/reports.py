from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


class ReportType(str, Enum):
    DAILY_FRAUD = "daily_fraud"
    MONTHLY_FRAUD = "monthly_fraud"
    HIGH_RISK_CUSTOMERS = "high_risk_customers"
    HIGH_RISK_TRANSACTIONS = "high_risk_transactions"
    CONFIRMED_FRAUD = "confirmed_fraud"
    FALSE_POSITIVES = "false_positives"
    FRAUD_TRENDS = "fraud_trends"


class ReportFormat(str, Enum):
    CSV = "csv"
    PDF = "pdf"


class ReportRequest(BaseModel):
    report_type: ReportType
    period: str  # YYYY-MM-DD or YYYY-MM
    format: ReportFormat = ReportFormat.CSV


class ReportResponse(BaseModel):
    report_id: str
    download_url: str
    expires_at: datetime
    report_type: ReportType
    format: ReportFormat
    generated_at: datetime


class ReportTemplate(BaseModel):
    type: ReportType
    name: str
    description: str
    parameters: List[str]


class ReportTemplatesResponse(BaseModel):
    templates: List[ReportTemplate]