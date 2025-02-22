# app/models/subscription_plans/subscription.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..base import Base
from ...utils.enums import UserTypeEnum

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    plan_id = Column(Integer, ForeignKey('plans.id'), nullable=False)
    product_name = Column(String, nullable=False)  # Product name associated with the subscription
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    user_type = Column(Enum(UserTypeEnum), nullable=False) 

    plan = relationship("Plan", back_populates="subscriptions")
    user = relationship("User", back_populates="subscriptions")
    company = relationship("Company", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription(tenant_type={self.user_type}, product_name={self.product_name}, is_active={self.is_active})>"
