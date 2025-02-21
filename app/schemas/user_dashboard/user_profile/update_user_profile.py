from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Request schema for updating the user profile.
class UserProfileUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    # Add additional fields here if needed.

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Doe"
            }
        }

# Inner response data schema containing user profile details.
class UpdateUserProfileResponseDataSchema(BaseModel):
    id: int = Field(..., description="Unique identifier for the user")
    email: str = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    status: Optional[str] = Field(None, description="User's status")
    is_active: bool = Field(..., description="Indicates whether the user is active")
    is_admin: bool = Field(..., description="Indicates whether the user is an administrator")
    user_type: Optional[str] = Field(None, description="User type")
    last_login: Optional[datetime] = Field(None, description="Timestamp of last login")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the profile was last updated")


# Top-level response schema wrapping the profile update data.
class UpdateUserProfileResponseSchema(BaseModel):
    status: str = Field(..., description="Response status")
    msg: str = Field(..., description="Response message")
    data: UpdateUserProfileResponseDataSchema = Field(..., description="Updated user profile details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "User profile updated successfully.",
                "data": {
                    "id": 123,
                    "email": "user@example.com",
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "status": "ACTIVE",
                    "is_active": True,
                    "is_admin": False,
                    "user_type": "regular",
                    "last_login": "2025-02-20T22:31:01.077361+00:00",
                    "created_at": "2025-01-15T12:00:00+00:00",
                    "updated_at": "2025-02-20T22:31:01.077361+00:00"
                }
            }
        }
