# User Profile Endpoints
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.user_dashboard.user_profile.get_user_profile import UserProfileResponseSchema
from app.utils.response_helper import create_response
from app.utils.get_current_user import get_current_user
import logging

get_user_profile_router = APIRouter()
logger = logging.getLogger(__name__)


@get_user_profile_router.get(
        "/profile", 
        response_model=UserProfileResponseSchema,
        description="Get user profile details")

async def get_user_profile(
    _: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """
    Retrieve the current user's profile.
    """
    try:
        user_data = {
            "id": current_user.id,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "status": current_user.status.value if current_user.status else None,
            "is_active": current_user.is_active,
            "is_admin": current_user.is_admin,
            "user_type": current_user.user_type.value if current_user.user_type else None,
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
        }
        return create_response(
            status="success",
            msg="User profile retrieved successfully.",
            data=user_data
        )
    except Exception as e:
        logger.error(f"Error retrieving user profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))