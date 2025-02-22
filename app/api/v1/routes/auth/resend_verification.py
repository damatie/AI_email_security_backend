from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.models import User
from app.db.deps import get_db
from app.services.email_services.send_email_notifications.email_sending_service import EmailSendingService
from app.core.security import create_verification_token
from app.utils.enums import UserStatusEnum
from app.utils.response_helper import create_response
import logging

resend_verification_router = APIRouter()
logger = logging.getLogger(__name__)


@resend_verification_router.post("/", status_code=status.HTTP_200_OK)
async def resend_verification_email(
    email: str, db: Session = Depends(get_db), email_service: EmailSendingService = Depends()
):
    """
    Resend the email verification link to the user.
    """
    try:
        # Fetch the user by email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.warning(f"Resend verification: User not found for email {email}")
            return create_response(
                status="error",
                msg="User not found.",
                data=None,
            )

        if user.status == UserStatusEnum.ACTIVE:
            logger.info(f"Resend verification: Email {email} is already verified.")
            return create_response(
                status="error",
                msg="Email is already verified.",
                data=None,
            )

        # Generate a new verification token
        token = create_verification_token(user.email)
        user.verification_token = token
        db.commit()

        # Send verification email
        try:
            email_service.send_verification_email(user.email, token)
            logger.info(f"Resend verification: Email sent successfully to {email}")
        except Exception as e:
            logger.error(f"Failed to send verification email to {email}: {str(e)}")
            return create_response(
                status="error",
                msg="Failed to send verification email. Please try again later.",
                data=None,
            )

        return create_response(
            status="success",
            msg="Verification email resent successfully.",
            data={"email": email},
        )

    except HTTPException:
        # Re-raise known HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        logger.exception(f"Unexpected error during resend verification for {email}: {str(e)}")
        return create_response(
            status="error",
            msg="An unexpected error occurred. Please try again later.",
            data=None,
        )
