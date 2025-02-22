from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class ThreatAnalysisHighlightSchema(BaseModel):
    highlight_type: str = Field(..., description="Type of the highlight")
    content: str = Field(..., description="Highlighted content")
    severity: str = Field(..., description="Severity level of the highlight")
    description: Optional[str] = Field(None, description="Description of the highlight")
    remediation_suggestion: Optional[str] = Field(
        None, description="Remediation suggestion for the highlight"
    )
    created_at: datetime = Field(..., description="Timestamp when the highlight was created")

    class Config:
        schema_extra = {
            "example": {
                "highlight_type": "subject",
                "content": "Urgent",
                "severity": "HIGH",
                "description": "The subject contains urgent keywords",
                "remediation_suggestion": "Verify the sender's authenticity",
                "created_at": "2025-02-11T14:50:00Z"
            }
        }

class ThreatAnalysisSchema(BaseModel):
    is_threat: bool = Field(..., description="Indicates whether the email is considered a threat")
    threat_type: str = Field(..., description="The classified threat type")
    severity: Optional[str] = Field(None, description="The severity of the threat")
    confidence_score: float = Field(..., description="Confidence score of the threat analysis")
    remediation_steps: List[str] = Field(..., description="List of remediation steps")
    explanation: Union[Dict[str, Any], str] = Field(
        ..., description="Explanation for the threat analysis; can be a dict or a string"
    )
    model_version: str = Field(..., description="Version of the model used for analysis")
    analyzed_at: datetime = Field(..., description="Timestamp when the analysis was performed")
    highlights: List[ThreatAnalysisHighlightSchema] = Field(
        [], description="List of analysis highlights"
    )

    class Config:
        schema_extra = {
            "example": {
                "is_threat": True,
                "threat_type": "PHISHING",
                "severity": "HIGH",
                "confidence_score": 0.95,
                "remediation_steps": ["Do not click on suspicious links", "Verify sender details"],
                "explanation": {"detail": "Suspicious link detected in the email body."},
                "model_version": "v1.2.3",
                "analyzed_at": "2025-02-11T15:00:00Z",
                "highlights": [
                    {
                        "highlight_type": "subject",
                        "content": "Urgent",
                        "severity": "HIGH",
                        "description": "The subject contains urgent keywords",
                        "remediation_suggestion": "Verify the sender's authenticity",
                        "created_at": "2025-02-11T14:50:00Z"
                    }
                ]
            }
        }

class RemediationLogSchema(BaseModel):
    action_taken: str = Field(..., description="The action taken as part of remediation")
    performed_by: str = Field(..., description="Identifier of who performed the remediation")
    timestamp: datetime = Field(..., description="Timestamp when the remediation was logged")

    class Config:
        schema_extra = {
            "example": {
                "action_taken": "Reclassified as Phishing",
                "performed_by": "User 123",
                "timestamp": "2025-02-11T15:10:00Z"
            }
        }

class EmailDetailDataSchema(BaseModel):
    email_id: str = Field(..., description="Unique identifier of the email")
    subject: str = Field(..., description="Subject of the email")
    sender: str = Field(..., description="Sender email address")
    recipient: str = Field(..., description="Recipient email address")
    received_at: datetime = Field(..., description="Timestamp when the email was received")
    processed_at: Optional[datetime] = Field(
        None, description="Timestamp when the email was processed"
    )
    threat_analysis: Optional[ThreatAnalysisSchema] = Field(
        None, description="Detailed threat analysis of the email"
    )
    remediation_logs: List[RemediationLogSchema] = Field(
        [], description="List of remediation logs for the email"
    )

    class Config:
        schema_extra = {
            "example": {
                "email_id": "abcd1234",
                "subject": "Important Notice",
                "sender": "sender@example.com",
                "recipient": "recipient@example.com",
                "received_at": "2025-02-11T14:35:20Z",
                "processed_at": "2025-02-11T15:00:00Z",
                "threat_analysis": {
                    "is_threat": True,
                    "threat_type": "PHISHING",
                    "severity": "HIGH",
                    "confidence_score": 0.95,
                    "remediation_steps": ["Do not click on suspicious links", "Verify sender details"],
                    "explanation": "This email shows few or no signs of being malicious",
                    "model_version": "v1.2.3",
                    "analyzed_at": "2025-02-11T15:00:00Z",
                    "highlights": [
                        {
                            "highlight_type": "subject",
                            "content": "Urgent",
                            "severity": "HIGH",
                            "description": "The subject contains urgent keywords",
                            "remediation_suggestion": "Verify the sender's authenticity",
                            "created_at": "2025-02-11T14:50:00Z"
                        }
                    ]
                },
                "remediation_logs": [
                    {
                        "action_taken": "Reclassified as Phishing",
                        "performed_by": "User 123",
                        "timestamp": "2025-02-11T15:10:00Z"
                    }
                ]
            }
        }

class EmailDetailResponseSchema(BaseModel):
    status: str = Field(..., description="Response status")
    msg: str = Field(..., description="Response message")
    data: EmailDetailDataSchema = Field(..., description="Detailed email data")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "Email detail retrieved successfully.",
                "data": {
                    "email_id": "abcd1234",
                    "subject": "Important Notice",
                    "sender": "sender@example.com",
                    "recipient": "recipient@example.com",
                    "received_at": "2025-02-11T14:35:20Z",
                    "processed_at": "2025-02-11T15:00:00Z",
                    "threat_analysis": {
                        "is_threat": True,
                        "threat_type": "PHISHING",
                        "severity": "HIGH",
                        "confidence_score": 0.95,
                        "remediation_steps": ["Do not click on suspicious links", "Verify sender details"],
                        "explanation": {"detail": "Suspicious link detected in the email body."},
                        "model_version": "v1.2.3",
                        "analyzed_at": "2025-02-11T15:00:00Z",
                        "highlights": [
                            {
                                "highlight_type": "subject",
                                "content": "Urgent",
                                "severity": "HIGH",
                                "description": "The subject contains urgent keywords",
                                "remediation_suggestion": "Verify the sender's authenticity",
                                "created_at": "2025-02-11T14:50:00Z"
                            }
                        ]
                    },
                    "remediation_logs": [
                        {
                            "action_taken": "Reclassified as Phishing",
                            "performed_by": "User 123",
                            "timestamp": "2025-02-11T15:10:00Z"
                        }
                    ]
                }
            }
        }
