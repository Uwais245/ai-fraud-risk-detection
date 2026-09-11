from sqlalchemy import (
    Column, Integer, String, DateTime, Numeric, Boolean, 
    ForeignKey, Text, Index, Enum as SQLEnum, BigInteger
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class TransactionChannel(str, enum.Enum):
    WEB = "web"
    MOBILE = "mobile"
    API = "api"
    POS = "pos"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    customer_id = Column(String(50), index=True, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    country = Column(String(100))
    bin_country = Column(String(100))
    channel = Column(SQLEnum(TransactionChannel), default=TransactionChannel.WEB)
    merchant_category = Column(String(100))
    promo_used = Column(Boolean, default=False)
    avs_match = Column(Boolean, default=True)
    cvv_result = Column(Boolean, default=True)
    three_ds_flag = Column(Boolean, default=False)
    shipping_distance_km = Column(Numeric(8, 2))
    account_age_days = Column(Integer)
    total_transactions_user = Column(Integer)
    avg_amount_user = Column(Numeric(12, 2))
    ip_address = Column(String(45))
    device_id = Column(String(100))
    device_type = Column(String(50))
    location = Column(String(100))
    is_fraud = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    risk_assessments = relationship("RiskAssessment", back_populates="transaction", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="transaction", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_transactions_customer_created", "customer_id", "created_at"),
        Index("ix_transactions_device_created", "device_id", "created_at"),
        Index("ix_transactions_ip_created", "ip_address", "created_at"),
        Index("ix_transactions_amount_created", "amount", "created_at"),
    )

    def __repr__(self):
        return f"<Transaction(id={self.transaction_id}, amount={self.amount}, risk={self.is_fraud})>"