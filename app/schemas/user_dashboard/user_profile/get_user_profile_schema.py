from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserProfileDataSchema(BaseModel):
    id: int = Field(..., description="Unique identifier for the user")
    email: str = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    status: Optional[str] = Field(None, description="User's status")
    is_active: bool = Field(..., description="Indicates whether the user is active")
    is_admin: bool = Field(..., description="Indicates whether the user is an administrator")
    user_type: Optional[str] = Field(None, description="Type of user")
    last_login: Optional[datetime] = Field(None, description="Timestamp of last login")
    created_at: Optional[datetime] = Field(None, description="Timestamp of account creation")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of last update")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        schema_extra = {
            "example": {
                "id": 123,
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "status": "ACTIVE",
                "is_active": True,
                "is_admin": False,
                "user_type": "INDIVIDUAL",
                "last_login": "2025-02-20T22:31:01.077361+00:00",
                "created_at": "2025-01-15T12:00:00+00:00",
                "updated_at": "2025-02-19T18:45:00+00:00"
            }
        }

class UserProfileResponseSchema(BaseModel):
    status: str = Field(..., description="Response status")
    msg: str = Field(..., description="Response message")
    data: UserProfileDataSchema = Field(..., description="User profile details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "User profile retrieved successfully.",
                "data": {
                    "id": 123,
                    "email": "user@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "status": "ACTIVE",
                    "is_active": True,
                    "is_admin": False,
                    "user_type": "INDIVIDUAL",
                    "last_login": "2025-02-20T22:31:01.077361+00:00",
                    "created_at": "2025-01-15T12:00:00+00:00",
                    "updated_at": "2025-02-19T18:45:00+00:00"
                }
            }
        }
