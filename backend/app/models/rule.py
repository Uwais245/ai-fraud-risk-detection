from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    condition = Column(JSON, nullable=False)  # e.g., {"field": "amount", "operator": ">", "value": 5000}
    action = Column(String(50), nullable=False)  # "increase_risk", "flag", "block"
    risk_increase = Column(Integer, default=0)  # points to add to risk score
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    creator = relationship("User")

    def __repr__(self):
        return f"<Rule(id={self.id}, name={self.name}, active={self.is_active})>"