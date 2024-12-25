# app/models/companies/company.py
from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
from ..base import Base
from ...utils.enums import EmailProviderEnum
from sqlalchemy.sql import func

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    domain = Column(String, unique=True, nullable=False)
    email_provider = Column(Enum(EmailProviderEnum), nullable=False)
    email_provider_settings = Column(JSON, nullable=True)
    onboarding_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="company")
    company_settings = relationship("CompanySettings", back_populates="company", uselist=False)

    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name}, domain={self.domain})>"
