# app/models/emails/email.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy.sql import func

class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Links to the user
    email_id = Column(String, unique=True, nullable=False)  # Unique email ID from the provider
    subject = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    received_at = Column(DateTime(timezone=True), nullable=False)  # Timestamp when the email was received
    processed_at = Column(DateTime(timezone=True), nullable=True)  # Timestamp when processing completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Auto-generated timestamp

    # Relationships
    user = relationship("User", back_populates="emails")
    threat_analysis = relationship("ThreatAnalysis", back_populates="email", uselist=False)
    remediation_logs = relationship("RemediationLog", back_populates="email")
    analysis_highlights = relationship("EmailAnalysisHighlights", back_populates="email")

    __table_args__ = (
        UniqueConstraint('email_id', name='uq_email_id'),
    )

    def __repr__(self):
        return f"<Email(id={self.id}, email_id={self.email_id}, subject={self.subject})>"

