# app/models/threat_analysis.py
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.utils.enums import ThreatTypeEnum, ThreatSeverityEnum
from sqlalchemy.sql import func

class ThreatAnalysis(Base):
    __tablename__ = 'threat_analysis'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)  # Link to the Email table
    is_threat = Column(Boolean, nullable=False)  # Indicates if a threat was detected
    threat_type = Column(Enum(ThreatTypeEnum), nullable=False)  # e.g., PHISHING, SUSPICIOUS, SAFE
    severity = Column(Enum(ThreatSeverityEnum), nullable=True)  # e.g., LOW, MEDIUM, HIGH
    confidence_score = Column(Float, nullable=False)  # AI model confidence score (0-1)
    remediation_steps = Column(JSON, nullable=True)  # Suggested remediation actions
    explanation = Column(JSON, nullable=True)  # Detailed explanation (could include model breakdowns)
    model_version = Column(String, nullable=False)  # Version of the AI model used
    analyzed_at = Column(DateTime(timezone=True), nullable=False)  # When analysis was completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    email = relationship("Email", back_populates="threat_analysis")
    highlights = relationship("EmailAnalysisHighlights", back_populates="threat_analysis")

    def __repr__(self):
        return f"<ThreatAnalysis(email_id={self.email_id}, type={self.threat_type}, severity={self.severity})>"
