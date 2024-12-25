# app/models/emails/email.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from ..base import Base
from sqlalchemy.sql import func

class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    email_id = Column(String, unique=True, nullable=False)  # Original email ID from provider
    subject = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    html_content = Column(Text, nullable=True)
    received_at = Column(DateTime(timezone=True), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    is_processed = Column(Boolean, default=False)
    email_metadata = Column(JSON, nullable=True)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="emails")
    attachments = relationship("EmailAttachment", back_populates="email")
    phishing_analysis = relationship("PhishingAnalysis", back_populates="email", uselist=False)

    def __repr__(self):
        return f"<Email(id={self.id}, subject={self.subject}, user_id={self.user_id})>"
