# app/models/email_integration.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class EmailIntegration(Base):
    __tablename__ = "email_integrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_name = Column(String, nullable=False)
    credentials = Column(JSON, nullable=False)  # Store provider credentials as JSON
    connected_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="email_integrations")

    def __repr__(self):
        return f"<EmailIntegration(user_id={self.user_id}, provider_name={self.provider_name})>"
