# app/models/users/user.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..base import Base
from ...utils.enums import UserStatusEnum, UserTypeEnum

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    status = Column(Enum(UserStatusEnum), default=UserStatusEnum.PENDING)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False, index=True)
    user_type = Column(Enum(UserTypeEnum), nullable=False)
    verification_token = Column(String, nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # subscriptions = relationship("Subscription", back_populates="user")
    company = relationship("Company", back_populates="users")
    role = relationship("Role", back_populates="users")
    emails = relationship("Email", back_populates="user")
    email_integrations = relationship("EmailIntegration", back_populates="user", cascade="all, delete-orphan")
    two_factor_auth = relationship("TwoFactorAuth", back_populates="user", uselist=False)
    notifications = relationship("UserNotification", back_populates="user")
    settings = relationship("UserSettings", back_populates="user", uselist=False)

    __table_args__ = (
        CheckConstraint(
            "(user_type = 'INDIVIDUAL' AND company_id IS NULL) OR (user_type = 'COMPANY' AND company_id IS NOT NULL)",
            name="user_type_company_check"
        ),
    )

    def __repr__(self):
        return (f"<User(id={self.id}, email={self.email}, role_id={self.role_id}, "
                f"status={self.status}, is_active={self.is_active})>")
