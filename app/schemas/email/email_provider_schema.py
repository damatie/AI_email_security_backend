# app/schemas/email/email_provider_schema.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Union
from datetime import datetime
from ...utils.enums import ServiceStatusEnum



class EmailProviderBaseSchema(BaseModel):
    name: str = Field(
        ..., 
        description="Name must contain only alphabetic characters and cannot be empty."
    )
    service_status: ServiceStatusEnum
    service_up: bool

    # Custom validator for the name field
    @field_validator("name", mode="before")
    def validate_name(cls, value: str) -> str:
        sanitized_value = value.strip()
        if not sanitized_value:
            raise ValueError("Name cannot be empty or just whitespace.")
        if not sanitized_value.isalpha():
            raise ValueError("Name must contain only alphabetic characters.")
        return sanitized_value

    class Config:
        orm_mode = True


class EmailProviderCreateSchema(EmailProviderBaseSchema):
    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "name": "GMAIL",
                "service_status": "AVAILABLE",
                "service_up": True,
            }
        }


class EmailProviderUpdateSchema(BaseModel):
    service_status: Optional[ServiceStatusEnum]
    service_up: Optional[bool]

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "service_status": "COMING_SOON",
                "service_up": False,
            }
        }


class EmailProviderResponseDataSchema(EmailProviderBaseSchema):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "GMAIL",
                "service_status": "AVAILABLE",
                "service_up": True,
                "created_at": "2024-12-21T12:00:00Z",
                "updated_at": "2024-12-21T12:30:00Z",
            }
        }


class EmailProviderGetResponseSchema(BaseModel):
    msg: str
    data: Optional[Union[EmailProviderResponseDataSchema, List[EmailProviderResponseDataSchema]]]

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "Email provider retrieved successfully.",
                "data": {
                    "id": 1,
                    "name": "GMAIL",
                    "service_status": "AVAILABLE",
                    "service_up": True,
                    "created_at": "2024-12-21T12:00:00Z",
                    "updated_at": "2024-12-21T12:30:00Z",
                },
            }
        }


class EmailProviderCreateResponseSchema(BaseModel):
    msg: str
    data: Optional[EmailProviderResponseDataSchema]

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "Email provider created successfully.",
                "data": {
                    "id": 2,
                    "name": "GMAIL",
                    "service_status": "AVAILABLE",
                    "service_up": True,
                    "created_at": "2024-12-24T15:00:00Z",
                    "updated_at": None,
                },
            }
        }


class EmailProviderUpdateResponseSchema(BaseModel):
    msg: str
    data: Optional[EmailProviderResponseDataSchema]

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "Email provider updated successfully.",
                "data": {
                    "id": 1,
                    "name": "GMAIL",
                    "service_status": "COMING_SOON",
                    "service_up": False,
                    "created_at": "2024-12-21T12:00:00Z",
                    "updated_at": "2024-12-24T15:30:00Z",
                },
            }
        }


class EmailProviderDeleteResponseSchema(BaseModel):
    msg: str
    data: Optional[None]

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "msg": "Email provider deleted successfully.",
                "data": None,
            }
        }
