# app/api/v1/routes/auth/individual_user/register.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.auth.individual_user.register import RegisterNewUserRequest, RegisterNewUserResponse
from app.models import User, Role
from app.core.security import get_password_hash
from app.utils.enums import RoleEnum, UserStatusEnum
from app.services.email_service import EmailService
from app.core.security import create_verification_token, get_password_hash
import logging

router = APIRouter()

from app.services.email_service import EmailService

@router.post("/", response_model=RegisterNewUserResponse, status_code=status.HTTP_201_CREATED)
async def user_register(
    user_data: RegisterNewUserRequest,
    db: Session = Depends(get_db),
):
    """
    User registration endpoint for individual users with email verification.
    """
    logger = logging.getLogger(__name__)

    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )
        
        # Assign the USER role
        role = db.query(Role).filter(Role.name == RoleEnum.USER).first()
        if not role:
            logger.error("Default role (USER) not configured in the database.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Role configuration error. Please contact support.",
            )
        
        # Generate verification token
        token = create_verification_token(user_data.email)

        # Create the user
        new_user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            status=UserStatusEnum.PENDING,
            is_active=True,
            onboarding_completed=False,
            verification_token=token,
            role_id=role.id,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Send verification email
        try:
            email_service = EmailService()
            email_service.send_verification_email(new_user.email, token)
        except Exception as e:
            logger.error(f"Error during email verification setup: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email. Please try again later.",
            )

        return {
            "message": "User registered successfully. Please verify your email.",
            "user_id": new_user.id,
        }

    except Exception as e:
        # Log unexpected errors with full details
        logger.exception("Unexpected error during user registration.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )



