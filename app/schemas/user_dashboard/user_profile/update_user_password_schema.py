from pydantic import BaseModel, Field, field_validator
from typing import Dict, List

# Request schema for updating the password.
class PasswordUpdateSchema(BaseModel):
    current_password: str = Field(..., description="The user's current password")
    new_password: str = Field(
        ...,
        min_length=8, 
        max_length=128,  
        description="The new password the user wants to set. User's password (must be between 8 and 128 characters and include letters, numbers, and special characters"
        )
    
    # Validate password with strong rules
    @field_validator("current_password")
    def validate_current_password(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Current password cannot be empty.")
        return value
    
    @field_validator("new_password")
    def validate_new_password(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Password cannot be empty.")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must include at least one number.")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must include at least one letter.")
        if not any(char in "!@#$%^&*()-_+=" for char in value):
            raise ValueError("Password must include at least one special character (!@#$%^&*()-_+=).")
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "old_password123",
                "new_password": "new_password456"
            }
        }

# Response schema for password update.
class UpdatePasswordResponseSchema(BaseModel):
    status: str = Field(..., description="Response status")
    msg: str = Field(..., description="Response message")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "Password updated successfully.",
            }
        }

