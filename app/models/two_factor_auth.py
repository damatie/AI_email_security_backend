# models/two_factor_auth.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.sql import func


class TwoFactorAuth(Base):
    __tablename__ = 'two_factor_auth'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    secret_key = Column(String, nullable=False)
    is_enabled = Column(Boolean, default=False)
    backup_codes = Column(String, nullable=True)  # Stored as JSON string of hashed backup codes
    last_used = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="two_factor_auth")

    def __repr__(self):
        return f"<TwoFactorAuth(user_id={self.user_id}, is_enabled={self.is_enabled})>"