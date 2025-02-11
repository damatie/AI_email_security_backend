# app/models/email_integration.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
from app.utils.encryption import encrypt_token, decrypt_token


class EmailIntegration(Base):
    __tablename__ = "email_integrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for company integration
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)  # Nullable for individual integration
    provider_name = Column(String, nullable=False)
    is_connected = Column(Boolean, default=False)
    encrypted_token = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_notification_sent = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="email_integrations", uselist=False)
    company = relationship("Company", back_populates="email_integrations", uselist=False)

    # Constraints to ensure only one of `user_id` or `company_id` is set
    __table_args__ = (
        CheckConstraint(
            "(user_id IS NOT NULL AND company_id IS NULL) OR (user_id IS NULL AND company_id IS NOT NULL)",
            name="check_user_or_company"
        ),
    )

    def set_token(self, token: str):
        """
        Encrypt and store the token securely.
        """
        self.encrypted_token = encrypt_token(token)

    def get_token(self) -> str:
        """
        Decrypt and return the token.
        """
        return decrypt_token(self.encrypted_token)

    def __repr__(self):
        return (
            f"<EmailIntegration("
            f"user_id={self.user_id}, "
            f"company_id={self.company_id}, "
            f"provider_name={self.provider_name}, "
            f"is_connected={self.is_connected})>"
        )
