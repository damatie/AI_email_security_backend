# app/schemas/auth/register_company.py

from pydantic import BaseModel, EmailStr, Field,field_validator

class RegisterNewCompanyRequest(BaseModel):
    email: EmailStr = Field(..., description="Admin's email address")
    password: str = Field(..., min_length=8, description="Admin's password")
       
    @field_validator("password")
    def validate_password(cls, value):
        if not value.strip():
            raise ValueError("Password canot be empty")
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
                "email": "admin@example.com",
                "password": "securepassword123!"
            }
        }

class RegisterNewCompanyResponse(BaseModel):
    message: str
    admin_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Company",
                "admin_id": 5
            }
        }
