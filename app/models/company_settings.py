# app/models/company_settings.py
from sqlalchemy import Column, Integer, Float, Boolean, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.sql import func

class CompanySettings(Base):
    __tablename__ = 'company_settings'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    phishing_threshold = Column(Float, default=0.7)
    auto_quarantine = Column(Boolean, default=True)
    notification_settings = Column(JSON, nullable=False, default=dict)
    security_policies = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="company_settings")

    def __repr__(self):
        return f"<CompanySettings(company_id={self.company_id})>"
