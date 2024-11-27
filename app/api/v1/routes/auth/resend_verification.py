# app/api/v1/routes/auth/resend_verification.py

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.models import User
from app.db.deps import get_db
from app.services.email_service import EmailService
from app.core.security import create_verification_token
from app.utils.enums import  UserStatusEnum
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification_email(
    email: str, db: Session = Depends(get_db), email_service: EmailService = Depends()
):
    """
    Resend the email verification link to the user.
    """
    try:
        # Fetch the user by email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.warning(f"Resend verification: User not found for email {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        if user.status == UserStatusEnum.ACTIVE:
            logger.info(f"Resend verification: Email {email} is already verified.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified.",
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email. Please try again later.",
            )

        return {"message": "Verification email resent successfully."}

    except HTTPException:
        # Re-raise known HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        logger.exception(f"Unexpected error during resend verification for {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )
