from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

class NotificationItemSchema(BaseModel):
    id: int = Field(..., description="Unique identifier for the notification")
    title: str = Field(..., description="Title of the notification")
    message: str = Field(..., description="Detailed message of the notification")
    data: Any = Field(..., description="Additional data associated with the notification")
    is_read: bool = Field(..., description="Indicates whether the notification has been read")
    created_at: datetime = Field(..., description="Timestamp when the notification was created")
    read_at: Optional[datetime] = Field(
        None, description="Timestamp when the notification was read, if applicable"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 101,
                "title": "New Message Received",
                "message": "You have received a new message from support.",
                "data": {"conversation_id": "abc123"},
                "is_read": False,
                "created_at": "2025-02-20T22:31:01.077361+00:00",
                "read_at": None
            }
        }

class NotificationsDataSchema(BaseModel):
    notifications: List[NotificationItemSchema] = Field(
        ..., description="List of user notifications"
    )

class NotificationResponseSchema(BaseModel):
    status: str = Field(..., description="Response status")
    msg: str = Field(..., description="Response message")
    data: NotificationsDataSchema = Field(..., description="Payload containing user notifications")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "User notifications retrieved successfully.",
                "data": {
                    "notifications": [
                        {
                            "id": 101,
                            "title": "New Message Received",
                            "message": "You have received a new message from support.",
                            "data": {"conversation_id": "abc123"},
                            "is_read": False,
                            "created_at": "2025-02-20T22:31:01.077361+00:00",
                            "read_at": None
                        },
                        {
                            "id": 102,
                            "title": "System Update",
                            "message": "The system will be down for maintenance at midnight.",
                            "data": {"duration": "2 hours"},
                            "is_read": True,
                            "created_at": "2025-02-19T18:00:00+00:00",
                            "read_at": "2025-02-19T18:05:00+00:00"
                        }
                    ]
                }
            }
        }
