# app/models/emails/email_provider.py
from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime
from sqlalchemy.sql import func
from ..base import Base
from ...utils.enums import ServiceStatusEnum



class EmailProvider(Base):
    __tablename__ = 'email_providers'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # e.g., 'GMAIL', 'OUTLOOK'
    service_status = Column(Enum(ServiceStatusEnum), nullable=False)
    service_up = Column(Boolean, default=True)  # True if the service is operational
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return (f"<EmailProvider(name={self.name}, status={self.service_status}, "
                f"service_up={self.service_up})>")
