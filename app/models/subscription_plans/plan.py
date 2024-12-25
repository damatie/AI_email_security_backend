# app/models/subscription_plans/plan.py
from sqlalchemy import Column, Integer, String, Enum, Float, JSON, Text
from sqlalchemy.orm import relationship
from ..base import Base
from ...utils.enums import PlanTypeEnum

class Plan(Base):
    __tablename__ = 'plans'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    plan_type = Column(Enum(PlanTypeEnum), nullable=False)  # Enum: INDIVIDUAL, BUSINESS
    price = Column(Float, nullable=False)
    features = Column(JSON, nullable=True)

    subscriptions = relationship("Subscription", back_populates="plan")

    def __repr__(self):
        return f"<Plan(name={self.name}, type={self.plan_type}, price={self.price})>"
