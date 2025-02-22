# User Profile Endpoints
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.user_dashboard.user_profile.update_user_profile_schema import UpdateUserProfileResponseSchema, UpdateUserProfileSchema
from app.utils.error_handlers.error_response_schema import ValidationErrorResponseSchema
from app.utils.response_helper import create_response
from app.utils.get_current_user import get_current_user
import logging

update_user_profile_router = APIRouter()
logger = logging.getLogger(__name__)

@update_user_profile_router.put(
        "/profile",
        response_model=UpdateUserProfileResponseSchema,
        responses={
            422: {
                "model": ValidationErrorResponseSchema,
                "description": "Validation error - the input data did not pass the validation checks.",
            }
        }
        )
async def update_user_profile(
    payload: UpdateUserProfileSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update current user's profile details (e.g., first_name, last_name).
    """
    try:
        # Update fields (e.g., first_name, last_name)
        current_user.first_name = payload.first_name or current_user.first_name
        current_user.last_name = payload.last_name or current_user.last_name
        # Additional fields can be updated similarly.
        db.commit()
        db.refresh(current_user)
        return create_response(
            status="success",
            msg="User profile updated successfully.",
            data=current_user
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Profile update failed.")
