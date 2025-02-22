# error_response_schema.py
from pydantic import BaseModel, Field
from typing import List

class ValidationErrorDetailSchema(BaseModel):
    field: str = Field(..., description="The name of the field with the error")
    message: str = Field(..., description="A description of the validation error")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "current_password",
                "message": "Current password cannot be empty."
            }
        }

class ValidationErrorResponseSchema(BaseModel):
    error_code: str = Field(..., description="A code representing the type of error")
    error_message: str = Field(..., description="A general error message")
    errors: List[ValidationErrorDetailSchema] = Field(..., description="List of field-specific errors")

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "VALIDATION_ERROR",
                "error_message": "One or more validation errors occurred.",
                "errors": [
                    {
                        "field": "field_name",
                        "message": "field_name cannot be empty."
                    }
                ]
            }
        }
