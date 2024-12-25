from fastapi import APIRouter, HTTPException, Depends, status, Cookie, Query
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models import User, TwoFactorAuth
from app.schemas.auth.login import LoginResponseSchema
from app.core.security import create_access_token
from app.core.config import settings
from app.core.redis import redis_client
from app.utils.response_helper import create_response
import pyotp
import logging

# Initialize router
login_2fa_router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)


@login_2fa_router.post("/", response_model=LoginResponseSchema, status_code=status.HTTP_200_OK)
async def verify_two_factor(
    code: str = Query(..., description="The 2FA code sent to the user's email"),
    temp_token: str = Cookie(None),
    db: Session = Depends(get_db),
):
    """
    Verify 2FA code or backup code and log in the user.
    """
    if not temp_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_response(
                status="error",
                msg="Temporary token is missing or invalid.",
                data=None,
            ),
        )

    # Retrieve user email from Redis using the temp_token
    email = redis_client.get(f"temp_token:{temp_token}")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_response(
                status="error",
                msg="Invalid or expired temporary token.",
                data=None,
            ),
        )

    # Find user by email (email is already a string, no need to decode)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_response(
                status="error",
                msg="User not found.",
                data=None,
            ),
        )

    # Fetch 2FA details
    two_fa = db.query(TwoFactorAuth).filter(TwoFactorAuth.user_id == user.id).first()
    if not two_fa or not two_fa.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_response(
                status="error",
                msg="Two-factor authentication is not enabled for this account.",
                data=None,
            ),
        )

    # Validate OTP
    totp = pyotp.TOTP(two_fa.secret_key)
    if not totp.verify(code, valid_window=settings.VALID_WINDOW):
        logger.error(f"Invalid OTP for user {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=create_response(
                status="error",
                msg="Invalid 2FA code.",
                data=None,
            ),
        )

    # Generate JWT token
    token = create_access_token({"sub": user.email}, settings.JWT_SECRET_KEY)

    # Delete the temp_token from Redis after successful verification
    redis_client.delete(f"temp_token:{temp_token}")

    logger.info(f"2FA verification successful for user {user.email}")
    return create_response(
        status="success",
        msg="Two-factor authentication successful.",
        data={
            "access_token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        },
    )
