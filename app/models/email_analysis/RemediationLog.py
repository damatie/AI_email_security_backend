# app/models/email_analysis_highlights.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..base import Base
from sqlalchemy.sql import func

class RemediationLog(Base):
    __tablename__ = 'remediation_logs'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)  # Links to the `Email` table
    action_taken = Column(String, nullable=False)  # e.g., "Quarantined", "Blocked Sender"
    performed_by = Column(String, nullable=False)  # e.g., "System", "User"
    timestamp = Column(DateTime(timezone=True), server_default=func.now())  # When the action was taken

    # Relationships
    email = relationship("Email", back_populates="remediation_logs")

    def __repr__(self):
        return f"<RemediationLog(email_id={self.email_id}, action={self.action_taken})>"
