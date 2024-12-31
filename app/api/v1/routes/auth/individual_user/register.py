# app/api/v1/routes/auth/individual_user/register.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.auth.individual_user.register_schema import RegisterNewUserSchema, RegisterNewUserResponseSchema
from app.models import User, Role
from app.core.security import get_password_hash
from app.utils.enums import RoleEnum, UserStatusEnum, UserTypeEnum
from app.services.email_services.email_sending_service import EmailSendingService
from app.core.security import create_verification_token
from app.utils.response_helper import create_response
import logging

register_individual_user_router = APIRouter()


@register_individual_user_router.post("/", response_model=RegisterNewUserResponseSchema, status_code=status.HTTP_201_CREATED)
async def user_register(
    user_data: RegisterNewUserSchema,
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
            logger.warning(f"Registration failed: Email {user_data.email} already exists.")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=create_response(
                    status="error",
                    msg="A user with this email already exists.",
                    data=None,
                ),
            )

        # Assign the INDIVIDUAL_USER role
        role = db.query(Role).filter(Role.name == RoleEnum.INDIVIDUAL_USER).first()
        if not role:
            logger.error("Default role (INDIVIDUAL_USER) not configured in the database.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_response(
                    status="error",
                    msg="Role configuration error. Please contact support.",
                    data=None,
                ),
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
            verification_token=token,
            user_type=UserTypeEnum.INDIVIDUAL,
            role_id=role.id,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Send verification email
        try:
            email_service = EmailSendingService()
            email_service.send_verification_email(new_user.email, token)
            logger.info(f"Verification email sent successfully to {new_user.email}.")
        except Exception as e:
            logger.error(f"Error during email verification setup: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=create_response(
                    status="error",
                    msg="Failed to send verification email. Please try again later.",
                    data=None,
                ),
            )

        return create_response(
            status="success",
            msg="User registered successfully. Please verify your email.",
            data={"user_id": new_user.id},
        )

    except HTTPException:
        # Re-raise known HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors with full details
        logger.exception(f"Unexpected error during user registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_response(
                status="error",
                msg="An unexpected error occurred. Please try again later.",
                data=None,
            ),
        )




