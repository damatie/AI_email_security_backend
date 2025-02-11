from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class GmailAuthUrlResponseSchema(BaseModel):
    status: str
    msg: str
    data: dict = Field(..., description="Authorization URL details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "Gmail auth URL generated successfully.",
                "data": {
                    "auth_url": "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=..."
                }
            }
        }


class EmailIntegrationUpdateSchema(BaseModel):
    is_connected: Optional[bool] = Field(None, description="Connection status of the email integration")

    class Config:
        json_schema_extra = {
            "example": {
                "is_connected": True
            }
        }


class EmailIntegrationResponseData(BaseModel):
    id: int
    provider_name: str
    is_connected: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "provider_name": "GMAIL",
                "is_connected": True,
                "created_at": "2024-12-24T15:30:00Z",
                "updated_at": "2024-12-24T16:00:00Z"
            }
        }


class EmailIntegrationResponseSchema(BaseModel):
    status: str
    msg: str
    data: Optional[EmailIntegrationResponseData] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "Gmail connected successfully.",
                "data": {
                    "id": 1,
                    "provider_name": "GMAIL",
                    "is_connected": True,
                    "created_at": "2024-12-24T15:30:00Z",
                    "updated_at": "2024-12-24T16:00:00Z"
                }
            }
        }


class EmailIntegrationListResponseSchema(BaseModel):
    status: str
    msg: str
    data: List[EmailIntegrationResponseData] = Field(..., description="List of email integrations")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "Email integrations retrieved successfully.",
                "data": [
                    {
                        "id": 1,
                        "provider_name": "GMAIL",
                        "is_connected": True,
                        "created_at": "2024-12-24T15:30:00Z",
                        "updated_at": "2024-12-24T16:00:00Z"
                    },
                    {
                        "id": 2,
                        "provider_name": "OUTLOOK",
                        "is_connected": False,
                        "created_at": "2024-12-24T15:40:00Z",
                        "updated_at": None
                    }
                ]
            }
        }
