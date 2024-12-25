# app/models/threat_analysis.py
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from ..base import Base
from ...utils.enums import ThreatTypeEnum, ThreatSeverityEnum
from sqlalchemy.sql import func

class PhishingAnalysis(Base):
    __tablename__ = 'phishing_analysis'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)
    is_threat = Column(Boolean, nullable=False)
    threat_type = Column(Enum(ThreatTypeEnum), nullable=False, default=ThreatTypeEnum.PHISHING)
    severity = Column(Enum(ThreatSeverityEnum), nullable=True)
    confidence_score = Column(Float, nullable=False)
    analysis_details = Column(JSON, nullable=True)  # Detailed phishing analysis
    analyzed_at = Column(DateTime(timezone=True), nullable=False)
    model_version = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    email = relationship("Email", back_populates="phishing_analysis")

    def __repr__(self):
        return f"<PhishingAnalysis(email_id={self.email_id}, is_threat={self.is_threat}, type={self.threat_type})>"