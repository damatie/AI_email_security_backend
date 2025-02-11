# app/api/v1/routes/auth/login.py
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models import User, TwoFactorAuth
from app.schemas.auth.login_schema import LoginSchema, LoginResponseSchema
from app.core.security import verify_password, create_access_token
from app.services.email_services.send_email_notifications.email_sending_service import EmailSendingService
from app.utils.enums import UserStatusEnum
from app.core.config import settings
from app.core.redis import redis_client
from app.utils.response_helper import create_response
import pyotp
import logging
import uuid

# Initialize router and email service
login_router = APIRouter()
email_service = EmailSendingService()

# Configure logger
logger = logging.getLogger(__name__)


@login_router.post("/", response_model=LoginResponseSchema, status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    login_data: LoginSchema,
    db: Session = Depends(get_db),
):
    """
    Log in a user with email and password. Handle 2FA states.
    """
    email = login_data.email.lower()  # Normalize email

    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning(f"Login failed: User not found for email {email} from IP: {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_response(
                status="error",
                msg="Invalid email or password.",
                data=None,
            ),
        )

    # Check if user is active
    if user.status != UserStatusEnum.ACTIVE or not user.is_active:
        logger.warning(f"Login failed: Inactive account for email {email} from IP: {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=create_response(
                status="error",
                msg="Account is inactive or not verified.",
                data=None,
            ),
        )

    # Validate password
    if not verify_password(login_data.password, user.password_hash):
        logger.warning(f"Login failed: Incorrect password for email {email} from IP: {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=create_response(
                status="error",
                msg="Invalid email or password.",
                data=None,
            ),
        )

    # Check if 2FA is enabled
    two_fa = db.query(TwoFactorAuth).filter(TwoFactorAuth.user_id == user.id).first()
    if two_fa and two_fa.is_enabled:
        # Generate OTP and send to email
        otp = pyotp.TOTP(two_fa.secret_key).now()
        email_service.send_otp_email(user.email, otp)
        logger.info(f"2FA OTP sent to {email}")

        # Generate temporary session token and store it in Redis with 10 minutes expiry
        temp_token = str(uuid.uuid4())
        redis_client.setex(f"temp_token:{temp_token}", 600, user.email)  # 10 minutes expiry

        # Create response and set the temp_token as an HTTP-only cookie
        response = JSONResponse(
            content=create_response(
                status="success",
                msg="Two-factor authentication is required to complete login.",
                data={
                    "two_factor_required": True,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                },
            )
        )
        response.set_cookie(key="temp_token", value=temp_token, httponly=True, max_age=600, secure=True)
        return response

    # Generate JWT token for successful login without 2FA
    token = create_access_token({"sub": user.email}, settings.JWT_SECRET_KEY)

    logger.info(f"Login successful for {email}")
    return create_response(
        status="success",
        msg="Login successful.",
        data={
            "access_token": token,
            "two_factor_required": False,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        },
    )
