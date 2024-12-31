#app/schemas/auth/individual_user/onboarding.py

from pydantic import BaseModel, Field
from typing import Optional, Dict


class OnboardingSchema(BaseModel):
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    email_provider: Optional[str] = Field(
        None, description="Preferred email provider (e.g., Gmail, Microsoft 365)"
    )
    email_provider_credentials: Optional[Dict[str, str]] = Field(
        None, description="Email provider connection details (e.g., client_id, client_secret)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Max",
                "last_name": "Doe",
                "email_provider": "Gmail",
                "email_provider_credentials": {
                    "client_id": "your-client-id",
                    "client_secret": "your-client-secret",
                },
            }
        }


class TwoFASetupSchema(BaseModel):
    otp: str = Field(..., description="OTP sent for 2FA setup verification")

    class Config:
        json_schema_extra = {
            "example": {
                "otp": "123456"
            }
        }


class OnboardingResponseSchema(BaseModel):
    status: str
    msg: str
    data: Optional[dict] = Field(
        None,
        description="Additional response data including user details and onboarding status",
    )
    connected_email_providers: Optional[list] = Field(
        None,
        description="List of connected email providers for the user.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "User information retrieved successfully.",
                "data": {
                    "onboarding_completed": False,
                    "two_factor_required": False,
                    "first_name": "Max",
                    "last_name": "Doe",
                    "email": "edafemaxwell@gmail.com",
                    "connected_email_providers": [
                        {
                            "provider_name": "Gmail",
                            "connected_at": "2024-11-19T10:30:00Z",
                        }
                    ],
                },
            }
        }

