from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class FeedbackType(str, Enum):
    CONFIRMED_FRAUD = "CONFIRMED_FRAUD"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class FeedbackCreate(BaseModel):
    transaction_id: str
    alert_id: Optional[int] = None
    feedback_type: FeedbackType
    notes: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    transaction_id: str
    alert_id: Optional[int]
    feedback_type: FeedbackType
    notes: Optional[str]
    submitted_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)