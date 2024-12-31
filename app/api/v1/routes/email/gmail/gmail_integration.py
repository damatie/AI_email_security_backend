from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.email.email_integration_schema import (
    GmailAuthUrlResponseSchema,
)
from app.services.email_services.gmail_service.connect_gmail_service import generate_gmail_auth_url, fetch_gmail_token
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
async def gmail_token( request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user), ):
    """
    Handle the Gmail OAuth2 callback and store tokens.
    """
    try:
        # Extract the authorization code from the request
        auth_code = request.query_params.get("code")
        if not auth_code:
            raise HTTPException(status_code=400, detail="Authorization code not found.")

        # Fetch the token using the auth code
        integration = fetch_gmail_token(auth_code, db, user_id=current_user.id)
        return create_response(
            status="success",
            msg="Gmail connected successfully.",
            data=integration,
        )
    except Exception as e:
        logger.error(f"Error completing Gmail integration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete Gmail integration: {e}",
        )


