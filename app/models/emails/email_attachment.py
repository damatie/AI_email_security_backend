# app/models/emails/email_attachment.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..base import Base
from sqlalchemy.sql import func

class EmailAttachment(Base):
    __tablename__ = 'email_attachments'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    storage_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    email = relationship("Email", back_populates="attachments")
    email_attachment_threat_analysis = relationship("AttachmentThreatAnalysis", back_populates="attachment", uselist=False)

    def __repr__(self):
        return f"<EmailAttachment(email_id={self.email_id}, filename={self.filename})>"
