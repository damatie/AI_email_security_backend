# app/schemas/user_dashboard/scanned_emails/get_emails_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class EmailItemSchema(BaseModel):
    email_id: str = Field(..., description="Unique identifier for the email")
    subject: str = Field(..., description="Subject of the email")
    sender: str = Field(..., description="Sender email address")
    sender_name: Optional[str] = Field(
        None, description="Display name of the sender (if available)"
    )
    recipient: str = Field(..., description="Email address of the recipient")
    received_at: datetime = Field(..., description="Timestamp when the email was received")
    processed_at: Optional[datetime] = Field(
        None, description="Timestamp when the email was processed"
    )
    threat_type: str = Field(
        ..., description="Threat type identified by threat analysis"
    )
    threat_severity: str = Field(
        ..., description="Threat severity identified by threat analysis"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email_id": "abcd1234",
                "subject": "Important Notice",
                "sender": "messaging-digest-noreply@linkedin.com",
                "sender_name": "Aryan Agrawal via LinkedIn",
                "recipient": "edafemaxwell@gmail.com",
                "received_at": "2025-02-11T14:35:20.123Z",
                "processed_at": "2025-02-11T15:00:00.123Z",
                "threat_type": "SAFE",
                "threat_severity": "LOW"
            }
        }


class EmailListDataSchema(BaseModel):
    emails: List[EmailItemSchema] = Field(..., description="List of processed emails")
    total: int = Field(..., description="Total number of emails for the current user")
    limit: int = Field(..., description="Number of emails per page")
    page: int = Field(..., description="Current page number (1-based)")
    total_pages: int = Field(..., description="Total pages available based on total and limit")

    class Config:
        json_schema_extra = {
            "example": {
                "emails": [
                    {
                        "email_id": "abcd1234",
                        "subject": "Important Notice",
                        "sender": "messaging-digest-noreply@linkedin.com",
                        "sender_name": "Aryan Agrawal via LinkedIn",
                        "recipient": "edafemaxwell@gmail.com",
                        "received_at": "2025-02-11T14:35:20.123Z",
                        "processed_at": "2025-02-11T15:00:00.123Z",
                        "threat_type": "SAFE",
                        "threat_severity": "LOW"
                    }
                ],
                "total": 100,
                "limit": 50,
                "page": 1,
                "total_pages": 2
            }
        }


class EmailListResponseSchema(BaseModel):
    status: str = Field(..., description="Response status")
    msg: str = Field(..., description="Response message")
    data: EmailListDataSchema = Field(..., description="Response data containing the emails list")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "Scanned email list retrieved successfully.",
                "data": {
                    "emails": [
                        {
                            "email_id": "abcd1234",
                            "subject": "Important Notice",
                            "sender": "messaging-digest-noreply@linkedin.com",
                            "sender_name": "Aryan Agrawal via LinkedIn",
                            "recipient": "edafemaxwell@gmail.com",
                            "received_at": "2025-02-11T14:35:20.123Z",
                            "processed_at": "2025-02-11T15:00:00.123Z",
                            "threat_type": "SAFE",
                            "threat_severity": "LOW"
                        }
                    ],
                    "total": 100,
                    "limit": 50,
                    "page": 1,
                    "total_pages": 2
                }
            }
        }
