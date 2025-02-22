#Update password
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password
from app.db.deps import get_db
from app.schemas.user_dashboard.user_profile.update_user_password_schema import PasswordUpdateSchema,UpdatePasswordResponseSchema
from app.utils.error_handlers.error_response_schema import ValidationErrorResponseSchema
from app.utils.response_helper import create_response
from app.utils.get_current_user import get_current_user
import logging

update_user_password_router = APIRouter()
logger = logging.getLogger(__name__)

@update_user_password_router.put(
        "/password", 
        response_model=UpdatePasswordResponseSchema,
        responses={
            422: {
                "model": ValidationErrorResponseSchema,
                "description": "Validation error - the input data did not pass the validation checks.",
            }
        }
        )
async def update_password(
    payload: PasswordUpdateSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update the user's password.
    Payload should include the current password and the new password.
    """
    try:
        # Verify current password using your password verification logic.
        if not verify_password(payload.current_password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="Current password is incorrect.")
        
        # Update the password hash with the new password.
        current_user.password_hash = get_password_hash(payload.new_password)
        db.commit()
        return create_response(
            status="success",
            msg="Password updated successfully.",
            data={}
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating password: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Password update failed.")