# app/models/email_analysis_highlights.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy.sql import func

class EmailAnalysisHighlights(Base):
    __tablename__ = 'email_analysis_highlights'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)
    threat_analysis_id = Column(Integer, ForeignKey('threat_analysis.id'), nullable=True)
    
    # A standardized type for the indicator (e.g., "Urgency", "Suspicious URL", "Domain Mismatch")
    highlight_type = Column(String, nullable=False)
    # The specific content or snippet that triggered this indicator
    content = Column(String, nullable=False)
    # Severity of this specific indicator (e.g., "High", "Medium", "Low")
    severity = Column(String, nullable=True)
    # Additional description or context for the indicator
    description = Column(String, nullable=True)
    # Recommended remediation for this particular indicator
    remediation_suggestion = Column(String, nullable=True)
    # Timestamp when this highlight was recorded
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    email = relationship("Email", back_populates="analysis_highlights")
    threat_analysis = relationship("ThreatAnalysis", back_populates="highlights")

    def __repr__(self):
        return f"<EmailAnalysisHighlights(email_id={self.email_id}, type={self.highlight_type}, severity={self.severity})>"
