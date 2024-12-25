# app/models/threat_analysis.py
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from ..base import Base
from ...utils.enums import ThreatTypeEnum, ThreatSeverityEnum
from sqlalchemy.sql import func

class AttachmentThreatAnalysis(Base):
    __tablename__ = 'email_attachment_threat_analysis'

    id = Column(Integer, primary_key=True)
    attachment_id = Column(Integer, ForeignKey('email_attachments.id'), nullable=False)
    is_threat = Column(Boolean, nullable=False)
    threat_type = Column(Enum(ThreatTypeEnum), nullable=False, default=ThreatTypeEnum.MALWARE)
    severity = Column(Enum(ThreatSeverityEnum), nullable=True)
    confidence_score = Column(Float, nullable=False)
    analysis_details = Column(JSON, nullable=True)  # Detailed malware/threat analysis
    analyzed_at = Column(DateTime(timezone=True), nullable=False)
    model_version = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    attachment = relationship("EmailAttachment", back_populates="email_attachment_threat_analysis")

    def __repr__(self):
        return f"<AttachmentThreatAnalysis(attachment_id={self.attachment_id}, is_threat={self.is_threat}, type={self.threat_type})>"