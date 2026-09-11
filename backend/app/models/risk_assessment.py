from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class RiskLevel(str):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Decision(str):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(50), ForeignKey("transactions.transaction_id"), nullable=False, index=True)
    ml_anomaly_score = Column(Numeric(5, 2))
    rule_engine_score = Column(Numeric(5, 2))
    customer_behavior_score = Column(Numeric(5, 2), nullable=True)
    final_risk_score = Column(Numeric(5, 2), nullable=False)
    risk_level = Column(String(10), nullable=False)
    decision = Column(String(20), nullable=False)
    risk_flags = Column(JSON, default=list)
    ai_explanation = Column(Text)
    assessed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    transaction = relationship("Transaction", back_populates="risk_assessments")

    def __repr__(self):
        return f"<RiskAssessment(txn={self.transaction_id}, score={self.final_risk_score}, level={self.risk_level})>"