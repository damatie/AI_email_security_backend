from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models.users.user_notification import UserNotification
from app.schemas.user_dashboard.user_settings.mark_notifications_schema import UserNotificationMarkReadResponseSchema
from app.utils.response_helper import create_response
from app.utils.get_current_user import get_current_user
import logging

update_notifications_router = APIRouter()
logger = logging.getLogger(__name__)

@update_notifications_router.put(
    "/notifications/{notification_id}/read",
    response_model=UserNotificationMarkReadResponseSchema,
)
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mark a notification as read.
    """
    try:
        notif = db.query(UserNotification).filter(
            UserNotification.user_id == current_user.id,
            UserNotification.id == notification_id
        ).first()
        if not notif:
            # If notification doesn't exist, raise a 404.
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notif.is_read = True
        notif.read_at = datetime.now(timezone.utc)
        db.commit()
        return create_response(
            status="success",
            msg="Notification marked as read.",
            data={"notification_id": notification_id}
        )
    except HTTPException as he:
        # Re-raise HTTP exceptions (like the 404 above) without modification.
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error marking notification as read: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to mark notification as read.")
