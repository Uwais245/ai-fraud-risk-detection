from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class CustomerRiskProfile(Base):
    __tablename__ = "customer_risk_profiles"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(50), unique=True, index=True, nullable=False)
    risk_level = Column(String(10), default="LOW")
    risk_score = Column(Numeric(5, 2), default=0)
    total_transactions = Column(Integer, default=0)
    suspicious_transactions = Column(Integer, default=0)
    devices_used = Column(JSON, default=list)
    ips_used = Column(JSON, default=list)
    locations_used = Column(JSON, default=list)
    previous_fraud_reports = Column(Integer, default=0)
    last_transaction_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<CustomerRiskProfile(customer={self.customer_id}, score={self.risk_score}, level={self.risk_level})>"