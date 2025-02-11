# app/models/emails/email_fetch_log.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class FetchEmailLog(Base):
    __tablename__ = "fetch_email_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    history_id = Column(String, nullable=False)
    last_fetched_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    initial_scan_completed = Column(Boolean, default=False, nullable=False)  # New field

    user = relationship("User", back_populates="fetch_email_logs")
