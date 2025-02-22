from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models.emails.email_integrations import EmailIntegration
from app.schemas.email.email_integration_schema import (
    EmailIntegrationResponseSchema,
    EmailIntegrationUpdateSchema,
    EmailIntegrationListResponseSchema,
)

from app.utils.response_helper import create_response
from app.utils.get_current_user import get_current_user
import logging

# Initialize router
email_integrations_router = APIRouter()
logger = logging.getLogger(__name__)


@email_integrations_router.get("/", response_model=EmailIntegrationListResponseSchema)
async def get_email_integrations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Retrieve all email integrations for the current user.
    """
    integrations = db.query(EmailIntegration).filter(EmailIntegration.user_id == current_user.id).all()
    return create_response(
        status="success",
        msg="Email integrations retrieved successfully.",
        data=integrations,
    )


@email_integrations_router.put("/{integration_id}", response_model=EmailIntegrationResponseSchema)
async def update_email_integration(
    integration_id: int,
    data: EmailIntegrationUpdateSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update an email integration.
    """
    integration = db.query(EmailIntegration).filter(
        EmailIntegration.id == integration_id,
        EmailIntegration.user_id == current_user.id,
    ).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_response(
                status="error",
                msg="Email integration not found.",
                data=None,
            ),
        )

    # Update fields
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(integration, key, value)

    db.commit()
    db.refresh(integration)

    return create_response(
        status="success",
        msg="Email integration updated successfully.",
        data=integration,
    )


@email_integrations_router.delete("/{integration_id}", response_model=EmailIntegrationResponseSchema)
async def delete_email_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete an email integration.
    """
    integration = db.query(EmailIntegration).filter(
        EmailIntegration.id == integration_id,
        EmailIntegration.user_id == current_user.id,
    ).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_response(
                status="error",
                msg="Email integration not found.",
                data=None,
            ),
        )

    db.delete(integration)
    db.commit()

    return create_response(
        status="success",
        msg="Email integration deleted successfully.",
        data=None,
    )
