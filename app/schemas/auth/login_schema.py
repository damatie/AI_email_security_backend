from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class LoginSchema(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="User's email address", 
        example="user@example.com"
    )
    password: str = Field(
        ..., 
        example="securePassword1!"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "edafemaxwell@gmail.com",
                "password": "securePassword1!"
            }
        }
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
        return value

class UserResponseDataSchema(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "id": 34,
                "email": "edafemaxwell@gmail.com",
                "first_name": "Max",
                "last_name": "Doe",
            }
        }


class LoginResponseDataSchema(BaseModel):
    access_token: Optional[str] = None
    two_factor_required: bool
    user: UserResponseDataSchema

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "two_factor_required": True,
                "user": {
                    "id": 34,
                    "email": "edafemaxwell@gmail.com",
                    "first_name": "Max",
                    "last_name": "Doe",
                },
            }
        }


class LoginResponseSchema(BaseModel):
    status: str
    msg: str
    data: LoginResponseDataSchema

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "Login successful.",
                "data": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "two_factor_required": False,
                    "user": {
                        "id": 34,
                        "email": "edafemaxwell@gmail.com",
                        "first_name": "Max",
                        "last_name": "Doe",
                    },
                },
            }
        }
