from pydantic import BaseModel, Field
from typing import Optional, Dict, Union
from datetime import datetime

class DashboardOverviewResponseSchema(BaseModel):
    """
    Pydantic schema describing the structure of the dashboard overview response.
    """
    status: str = Field(..., description="Response status (e.g. success or fail)")
    msg: str = Field(..., description="Short message describing the response")
    data: Optional[Dict[str, Union[int, float, Dict[str, int], str, None]]] = Field(
        None,
        description="High-level email security details, such as total scanned, threat summary, last scan time, etc."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "Dashboard overview retrieved successfully.",
                "data": {
                    "total_emails_scanned": 150,
                    "threat_summary": {
                        "phishing": 10,
                        "malware": 5
                    },
                    "last_scan_at": "2025-02-11T14:35:20.123Z",
                    "next_scheduled_scan": None
                }
            }
        }