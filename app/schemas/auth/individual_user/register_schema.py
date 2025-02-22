# app/schemas/auth/individual_user/register_user.py

from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterNewUserSchema(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="User's email address", 
        example="user@example.com"
    )
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=128, 
        description="User's password (must be between 8 and 128 characters and include letters, numbers, and special characters)",
        example="securePassword1!"
    )
    first_name: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="User's first name (must be between 1 and 50 characters)",
        example="John"
    )
    last_name: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="User's last name (must be between 1 and 50 characters)",
        example="Doe"
    )

    # Normalize email
    @field_validator("email", mode="before")
    def normalize_email(cls, email: str) -> str:
        return email.strip().lower()

    # Validate password with strong rules
    @field_validator("password")
    def validate_password(cls, value: str) -> str:
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

    # Validate first name and last name
    @field_validator("first_name", "last_name", mode="before")
    def validate_name(cls, value: str, info) -> str:
        field_name = info.field_name
        value = value.strip()
        if not value:
            raise ValueError(f"{field_name.capitalize()} cannot be empty or consist only of whitespace.")
        if not value.isalpha():
            raise ValueError(f"{field_name.capitalize()} must contain only alphabetic characters.")
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "email": "edafemaxwell@gmail.com",
                "password": "securePassword1!",
                "first_name": "John",
                "last_name": "Doe"
            }
        }


class RegisterNewUserResponseSchema(BaseModel):
    status: str = Field(..., description="Response status", example="success")
    msg: str = Field(..., description="Message describing the outcome", example="User registered successfully. Please verify your email.")
    data: dict = Field(
        ..., 
        description="Relevant data for the response", 
        example={"user_id": 5}
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "User registered successfully. Please verify your email.",
                "data": {"user_id": 5}
            }
        }
