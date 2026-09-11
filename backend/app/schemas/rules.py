from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RuleOperator(str, Enum):
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"


class RuleAction(str, Enum):
    INCREASE_RISK = "increase_risk"
    FLAG = "flag"
    BLOCK = "block"
    ALERT = "alert"


class RuleCondition(BaseModel):
    field: str
    operator: RuleOperator
    value: Any


class RuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    condition: RuleCondition
    action: RuleAction
    risk_increase: int = Field(default=0, ge=0, le=100)
    is_active: bool = True


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    condition: Optional[RuleCondition] = None
    action: Optional[RuleAction] = None
    risk_increase: Optional[int] = Field(default=None, ge=0, le=100)
    is_active: Optional[bool] = None


class RuleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    condition: RuleCondition
    action: RuleAction
    risk_increase: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RuleListResponse(BaseModel):
    rules: List[RuleResponse]
    total: int
    page: int
    per_page: int
    total_pages: int