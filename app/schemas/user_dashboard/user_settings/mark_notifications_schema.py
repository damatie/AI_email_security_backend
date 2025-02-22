from pydantic import BaseModel, Field
from typing import Optional

# Request schema for marking a notification as read.
class NotificationMarkReadDataSchema(BaseModel):
    notification_id: int = Field(..., description="The ID of the notification that was marked as read")

    class Config:
        schema_extra = {
            "example": {
                "notification_id": 123
            }
        }

# Top-level response schema wrapping the status, message, and data.
class UserNotificationMarkReadResponseSchema(BaseModel):
    status: str = Field(..., description="Response status")
    msg: str = Field(..., description="Response message")
    data: NotificationMarkReadDataSchema = Field(..., description="Response payload data")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "Notification marked as read.",
                "data": {
                    "notification_id": 123
                }
            }
        }
