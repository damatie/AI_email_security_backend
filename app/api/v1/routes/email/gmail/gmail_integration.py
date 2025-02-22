from fastapi import APIRouter, HTTPException, status, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.email.email_integration_schema import GmailAuthUrlResponseSchema
from app.services.email_services.gmail_service.connect_gmail_service import (
    generate_gmail_auth_url, 
    fetch_gmail_token
)
from app.services.email_services.gmail_service.fetch_email_service import check_for_new_emails_task
from app.utils.response_helper import create_response
from app.utils.get_current_user import get_current_user
import logging

# Initialize router
gmail_integrations_router = APIRouter()
logger = logging.getLogger(__name__)



@gmail_integrations_router.get("/auth-url", response_model=GmailAuthUrlResponseSchema)
async def get_gmail_auth_url(
    _=Depends(get_current_user),
):
    """
    Get the Gmail OAuth2 authorization URL.
    """
    try:
        auth_url = generate_gmail_auth_url()
        return create_response(
            status="success",
            msg="Gmail auth URL generated successfully.",
            data={"auth_url": auth_url},
        )
    except Exception as e:
        logger.error(f"Error generating Gmail auth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Gmail auth URL: {e}",
        )


@gmail_integrations_router.get("/token")
async def gmail_callback(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        logger.info("Token endpoint called")
        auth_code = request.query_params.get("code")
        if not auth_code:
            raise HTTPException(status_code=400, detail="Authorization code not found.")
        
        logger.info(f"Current user: id={current_user.id}, email={current_user.email}")

        integration = fetch_gmail_token(auth_code, db, user_id=current_user.id)

        logger.info("Scheduling initial scan background task")
        background_tasks.add_task(check_for_new_emails_task, user_id=current_user.id, email_address=current_user.email)

        response_data = {
            "id": integration.id,
            "user_id": integration.user_id,
            "provider_name": integration.provider_name,
            "is_connected": integration.is_connected,
            "created_at": integration.created_at.isoformat(),
            "updated_at": integration.updated_at.isoformat() if integration.updated_at else None,
        }

        return create_response(
            status="success",
            msg="Gmail connected successfully. Initial scan started.",
            data=response_data,
        )
    except Exception as e:
        logger.error(f"Error completing Gmail integration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete Gmail integration: {e}",
        )