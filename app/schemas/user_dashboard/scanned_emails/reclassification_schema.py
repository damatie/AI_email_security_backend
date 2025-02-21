from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

class EmailClassificationEnum(str, Enum):
    PHISHING = "PHISHING"
    SUSPICIOUS = "SUSPICIOUS"
    SAFE = "SAFE"

class ReclassificationRequestSchema(BaseModel):
    new_classification: EmailClassificationEnum
    reason: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "new_classification": "SAFE",
                "reason": "It looks like a clean email to me"
            }
        }

class ReclassificationResponseDataSchema(BaseModel):
    email_id: str = Field(..., description="Unique identifier of the email")
    new_classification: EmailClassificationEnum = Field(
        ..., description="Updated threat classification"
    )
    severity: str = Field(..., description="Updated threat severity")
    updated_at: datetime = Field(..., description="Timestamp when the reclassification occurred")
    reason: str = Field(..., description="Explanation for the reclassification")


class ReclassificationResponseSchema(BaseModel):
    status: str = Field(..., description="Response status")
    msg: str = Field(..., description="Response message")
    data: ReclassificationResponseDataSchema = Field(..., description="Reclassification details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "Email reclassified successfully.",
                "data": {
                    "email_id": "19525019fe8b61e4",
                    "new_classification": "SAFE",
                    "severity": "LOW",
                    "updated_at": "2025-02-20T22:31:01.077361+00:00",
                    "reason": "It looks like a clean email to me"
                }
            }
        }
