# app/models/users/user_settings.py
from sqlalchemy import Column, Integer, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from ..base import Base
from sqlalchemy.sql import func

class UserSettings(Base):
    __tablename__ = 'user_settings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    notification_preferences = Column(JSON, nullable=False, default=dict)
    ui_preferences = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="settings")

    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id})>"