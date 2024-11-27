# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
from ..utils.enums import UserStatusEnum

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    status = Column(Enum(UserStatusEnum), default=UserStatusEnum.PENDING)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    onboarding_completed = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="users")
    role = relationship("Role", back_populates="users")
    emails = relationship("Email", back_populates="user")
    two_factor_auth = relationship("TwoFactorAuth", back_populates="user", uselist=False)
    notifications = relationship("UserNotification", back_populates="user")
    settings = relationship("UserSettings", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role_id={self.role_id})>"