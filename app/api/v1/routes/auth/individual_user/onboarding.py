import json
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models import User, TwoFactorAuth
from app.core.config import settings
from app.models.emails.email_integrations import EmailIntegration
from app.schemas.auth.individual_user.onboarding_schema import (
    OnboardingSchema,
    OnboardingResponseSchema,
    TwoFASetupSchema,
)
from app.utils.get_current_user import get_current_user
from app.services.email_services.send_email_notifications.email_sending_service import EmailSendingService
import pyotp
import logging

# Initialize router and email service
onboarding_router = APIRouter()
email_service = EmailSendingService()

# Configure logger
logger = logging.getLogger(__name__)


@onboarding_router.get("/", response_model=OnboardingResponseSchema)
async def get_onboarding_details(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve user information for onboarding prepopulation.
    """
    logger.info(f"Retrieving onboarding details for user {current_user.email}")

    # Check if 2FA is enabled for the current user
    two_fa = db.query(TwoFactorAuth).filter(TwoFactorAuth.user_id == current_user.id).first()
    two_factor_required = two_fa.is_enabled if two_fa else False

    return {
        "status": "success",
        "msg": "User information retrieved successfully.",
        "data": {
            "onboarding_completed": current_user.onboarding_completed,
            "two_factor_required": two_factor_required,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "email": current_user.email,
        },
    }



@onboarding_router.post("/setup-2fa", status_code=status.HTTP_200_OK)
async def setup_two_factor_authentication(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Set up Two-Factor Authentication for the user.
    """
    logger.info(f"Setting up 2FA for user {current_user.email}")

    # Check if 2FA is already enabled
    two_fa = db.query(TwoFactorAuth).filter(TwoFactorAuth.user_id == current_user.id).first()

    if two_fa and two_fa.is_enabled:
        logger.error(f"2FA setup attempt failed: Already enabled for user {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "msg": "2FA is already enabled for this account.",
                "data": None,
            },
        )

    # Generate TOTP secret key
    secret_key = pyotp.random_base32()

    # Generate backup codes
    backup_codes = [pyotp.random_base32()[:8] for _ in range(5)]  # Generate 5 backup codes
    hashed_backup_codes = json.dumps(backup_codes)  # Store as JSON

    # Send OTP to user's email
    totp = pyotp.TOTP(secret_key)
    otp = totp.now()
    email_service.send_otp_email(current_user.email, otp)

    # Save 2FA entry in the database
    if not two_fa:
        two_fa = TwoFactorAuth(
            user_id=current_user.id,
            secret_key=secret_key,
            is_enabled=False,
            backup_codes=hashed_backup_codes,
        )
        db.add(two_fa)
    else:
        two_fa.secret_key = secret_key
        two_fa.backup_codes = hashed_backup_codes

    db.commit()
    logger.info(f"2FA setup initiated for user {current_user.email}")
    return {
        "status": "success",
        "msg": "2FA setup initiated. Check your email for the OTP.",
        "data": {
            "backup_codes": backup_codes,  # Optionally return backup codes for user to save securely
        },
    }


@onboarding_router.post("/verify-2fa", status_code=status.HTTP_200_OK)
async def verify_two_factor_authentication(
    data: TwoFASetupSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verify the 2FA OTP or backup code provided by the user.
    """
    logger.info(f"Verifying 2FA for user {current_user.email}")
    two_fa = db.query(TwoFactorAuth).filter(TwoFactorAuth.user_id == current_user.id).first()

    if not two_fa:
        logger.error(f"2FA verification failed: Setup not initiated for user {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "msg": "2FA setup not initiated.",
                "data": None,
            },
        )

    # Verify OTP
    totp = pyotp.TOTP(two_fa.secret_key)
    expected_otp = totp.now()
    logger.info(f"Expected OTP: {expected_otp}, User entered OTP: {data.otp}")
    
    if totp.verify(data.otp, valid_window=settings.VALID_WINDOW): # 20 intervals (10 minutes total)
        logger.info(f"2FA OTP verified for user {current_user.email}")
        two_fa.is_enabled = True
        two_fa.last_used = func.now()
        db.commit()
        return {
            "status": "success",
            "msg": "2FA successfully verified and enabled.",
            "data": None,
        }

    # Check backup codes
    if two_fa.backup_codes:
        backup_codes = json.loads(two_fa.backup_codes)
        if data.otp in backup_codes:
            logger.info(f"2FA backup code used for user {current_user.email}")
            backup_codes.remove(data.otp)  # Remove used backup code
            two_fa.backup_codes = json.dumps(backup_codes)
            two_fa.is_enabled = True
            two_fa.last_used = func.now()
            db.commit()
            return {
                "status": "success",
                "msg": "2FA successfully verified using backup code.",
                "data": None,
            }

    logger.error(f"2FA verification failed: Invalid code for user {current_user.email}")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "status": "error",
            "msg": "Invalid OTP or backup code.",
            "data": None,
        },
    )


@onboarding_router.post("/connect-email", status_code=status.HTTP_200_OK)
async def connect_email_provider(
    data: OnboardingSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Connect the user's preferred email provider.
    """
    if not data.email_provider or not data.email_provider_credentials:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "msg": "Email provider and credentials are required.",
                "data": None,
            },
        )

    # Save connected email provider details
    connected_provider = EmailIntegration(
        user_id=current_user.id,
        provider_name=data.email_provider,
        credentials=data.email_provider_credentials,
    )
    db.add(connected_provider)
    db.commit()

    logger.info(f"Email provider {data.email_provider} connected for user {current_user.email}")
    return {
        "status": "success",
        "msg": f"Successfully connected to {data.email_provider}.",
        "data": {
            "provider_name": data.email_provider,
            "connected_at": connected_provider.connected_at,
        },
    }


@onboarding_router.post("/complete", status_code=status.HTTP_200_OK)
async def complete_onboarding(
    data: OnboardingSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Complete the onboarding process for the user.
    """
    logger.info(f"Completing onboarding for user {current_user.email}")
    if current_user.onboarding_completed:
        logger.warning(f"Onboarding already completed for user {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "msg": "Onboarding is already completed.",
                "data": None,
            },
        )

    current_user.first_name = data.first_name or current_user.first_name
    current_user.last_name = data.last_name or current_user.last_name
    current_user.onboarding_completed = True
    db.commit()
    logger.info(f"Onboarding completed for user {current_user.email}")
    return {
        "status": "success",
        "msg": "Onboarding completed successfully.",
        "data": None,
    }
