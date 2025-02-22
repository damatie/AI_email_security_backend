# app/models/users/user_notification.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from ..base import Base
from sqlalchemy.sql import func

class UserNotification(Base):
    __tablename__ = 'user_notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    data = Column(JSON, nullable=True)  # Additional notification data
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<UserNotification(user_id={self.user_id}, title={self.title}, is_read={self.is_read})>"
