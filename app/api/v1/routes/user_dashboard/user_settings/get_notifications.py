from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models.users.user_notification import UserNotification
from app.schemas.user_dashboard.user_settings.get_notifications_schema import NotificationResponseSchema
from app.utils.response_helper import create_response
from app.utils.get_current_user import get_current_user
import logging

get_notifications_router = APIRouter()
logger = logging.getLogger(__name__)

@get_notifications_router.get("/notifications", response_model=NotificationResponseSchema)
async def get_user_notifications(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retrieve notifications for the current user.
    """
    try:
      # test_notif = UserNotification(
      #     user_id=current_user.id,
      #     title="Test Notification",
      #     message="This is a test notification inserted for testing.",
      #     data={"sample_key": "sample_value"},
      #     is_read=False,
      #     created_at=datetime.now(timezone.utc),
      #     read_at=None
      # )
      # db.add(test_notif)
      # db.commit()
      # db.refresh(test_notif)
       
      notifications = db.query(UserNotification).filter(UserNotification.user_id == current_user.id).all()
      notif_list = [{
          "id": n.id,
          "title": n.title,
          "message": n.message,
          "data": n.data,
          "is_read": n.is_read,
          "created_at": n.created_at.isoformat(),
          "read_at": n.read_at.isoformat() if n.read_at else None
      } for n in notifications]
      return create_response(
          status="success",
          msg="User notifications retrieved successfully.",
          data={"notifications": notif_list}
      )
    except Exception as e:
        logger.error(f"Error retrieving user notifications: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
