from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models.emails.email_provider import EmailProvider
from app.schemas.email.email_provider_schema import (
    EmailProviderCreateSchema,
    EmailProviderUpdateSchema,
    EmailProviderGetResponseSchema,
    EmailProviderCreateResponseSchema,
    EmailProviderUpdateResponseSchema,
    EmailProviderDeleteResponseSchema,
)
from app.utils.response_helper import create_response
import logging

email_providers_router = APIRouter()
logger = logging.getLogger(__name__)


@email_providers_router.get("/", response_model=EmailProviderGetResponseSchema)
async def get_email_providers(db: Session = Depends(get_db)):
    """
    Retrieve all email providers.
    """
    providers = db.query(EmailProvider).all()
    if not providers:
        return create_response(
            status="success",
            msg="No email providers found.",
            data=[],
        )

    return create_response(
        status="success",
        msg="Email providers retrieved successfully.",
        data=providers,
    )


@email_providers_router.post(
    "/", response_model=EmailProviderCreateResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_email_provider(data: EmailProviderCreateSchema, db: Session = Depends(get_db)):
    """
    Create a new email provider.
    """
    provider = EmailProvider(**data.model_dump())
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return create_response(
        status="success",
        msg="Email provider created successfully.",
        data=provider,
    )


@email_providers_router.put(
    "/{provider_id}", response_model=EmailProviderUpdateResponseSchema
)
async def update_email_provider(
    provider_id: int, data: EmailProviderUpdateSchema, db: Session = Depends(get_db)
):
    """
    Update an email provider.
    """
    provider = db.query(EmailProvider).filter(EmailProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email provider not found.",
        )

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(provider, key, value)

    db.commit()
    db.refresh(provider)
    return create_response(
        status="success",
        msg="Email provider updated successfully.",
        data=provider,
    )


@email_providers_router.delete(
    "/{provider_id}", response_model=EmailProviderDeleteResponseSchema
)
async def delete_email_provider(provider_id: int, db: Session = Depends(get_db)):
    """
    Delete an email provider.
    """
    provider = db.query(EmailProvider).filter(EmailProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email provider not found.",
        )

    db.delete(provider)
    db.commit()
    return create_response(
        status="success",
        msg="Email provider deleted successfully.",
        data=None,
    )
