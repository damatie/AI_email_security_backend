# app/schemas/auth/register_user.py

from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterNewUserRequest(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="User's email address", 
        example="user@example.com"
    )
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=128, 
        description="User's password (must be between 8 and 128 characters)",
        example="securepassword123"
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


    @field_validator("email", mode="before")
    def normalize_email(cls, email: str) -> str:
        
        return email.strip().lower()
    
    @field_validator("password")
    def validate_password(cls, value:str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Password canot be empty")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must include at least one number.")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must include at least one letter.")
        if not any(char in "!@#$%^&*()-_+=" for char in value):
            raise ValueError("Password must include at least one special character (!@#$%^&*()-_+=).")
        return value

    @field_validator("first_name", "last_name", mode="before")
    def validate_name(cls, value:str, info) -> str:
        field_name = info.field_name
        value =  value.strip()
        if not value:
            raise ValueError(f"{field_name.capitalize()} cannot be empty or consist only of whitespace.")
        if not value.isalpha():
            raise ValueError(f"{field_name.capitalize()} Names must contain only alphabetic characters.")
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


class RegisterNewUserResponse(BaseModel):
    message: str
    user_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "message": "User registered successfully. Please verify your email.",
                "user_id": 5
            }
        }
