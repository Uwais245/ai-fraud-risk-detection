from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class FeedbackType(str, enum.Enum):
    CONFIRMED_FRAUD = "CONFIRMED_FRAUD"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(50), ForeignKey("transactions.transaction_id"), nullable=False, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    feedback_type = Column(SQLEnum(FeedbackType), nullable=False)
    notes = Column(Text)
    submitted_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    transaction = relationship("Transaction")
    alert = relationship("Alert")
    submitter = relationship("User")

    def __repr__(self):
        return f"<Feedback(txn={self.transaction_id}, type={self.feedback_type})>"