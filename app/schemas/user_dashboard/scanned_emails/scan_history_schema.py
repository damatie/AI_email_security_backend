from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class ScanHistoryItemSchema(BaseModel):
    timestamp: datetime = Field(..., description="Timestamp when the fetch log was recorded")
    history_id: str = Field(..., description="Unique identifier for the scan history record")
    initial_scan_completed: bool = Field(..., description="Indicates whether the initial scan was completed")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-02-20T22:31:01.077361+00:00",
                "history_id": "abcd1234",
                "initial_scan_completed": True
            }
        }

class ScanHistoryDataSchema(BaseModel):
    scan_history: List[ScanHistoryItemSchema] = Field(..., description="List of scan history records")

class ScanHistoryResponseSchema(BaseModel):
    status: str = Field(..., description="Response status")
    msg: str = Field(..., description="Response message")
    data: ScanHistoryDataSchema = Field(..., description="Payload containing scan history records")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "Scan history retrieved successfully.",
                "data": {
                    "scan_history": [
                        {
                            "timestamp": "2025-02-20T22:31:01.077361+00:00",
                            "history_id": "abcd1234",
                            "initial_scan_completed": True
                        }
                    ]
                }
            }
        }
