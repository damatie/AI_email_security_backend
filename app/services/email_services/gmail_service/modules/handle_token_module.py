import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from googleapiclient.errors import HttpError
from app.models.emails.email_integrations import EmailIntegration
from app.models.users.user import User
from app.core.config import settings
from app.services.email_services.gmail_service.send_user_notification_service import send_notification

logger = logging.getLogger(__name__)
SCOPES = settings.GMAIL_SCOPES

# Check token status
def check_token_status(db: Session, integration: EmailIntegration) -> bool:
    """
    Check token status and send notifications if needed.
    Returns True if token is valid, False otherwise.
    Only sends notification once when approaching expiration.
    """
    try:
        token_created_at = integration.updated_at or integration.created_at
        days_since_refresh = (datetime.now(timezone.utc) - token_created_at).days
        
        # Check if token is approaching expiration (150 days = 5 months)
        if days_since_refresh > 150:
            # Only send notification if we haven't sent one in the last week
            last_notification_sent = getattr(integration, 'last_notification_sent', None)
            should_notify = (
                last_notification_sent is None or 
                (datetime.now(timezone.utc) - last_notification_sent).days >= 7
            )
            
            if should_notify:
                user = db.query(User).filter(User.id == integration.user_id).first()
                send_notification(
                    user_id=integration.user_id,
                    title="Gmail Authentication Expiring Soon",
                    message=f"Your Gmail integration will expire soon. Please re-authenticate to maintain email sync.",
                    email=user.email,
                    notification_type="token_expiring"
                )
                
                # Update last notification timestamp
                integration.last_notification_sent = datetime.now(timezone.utc)
                db.commit()
            
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error checking token status: {e}")
        return False
    
# Handle token-related errors
def handle_token_error(db: Session, integration: EmailIntegration, error: Exception):
    """Handle token-related errors and send appropriate notifications"""
    user = db.query(User).filter(User.id == integration.user_id).first()
    
    if isinstance(error, HttpError):
        if error.resp.status == 401:
            send_notification(
                user_id=integration.user_id,
                title="Gmail Authentication Required",
                message="Your Gmail access has expired. Please re-authenticate to continue syncing emails.",
                email=user.email,
                notification_type="token_expired"
            )
        elif error.resp.status == 403:
            send_notification(
                user_id=integration.user_id,
                title="Gmail Access Revoked",
                message="Your Gmail access has been revoked. Please re-authenticate to continue syncing emails.",
                email=user.email,
                notification_type="token_revoked"
            )
    
    integration.is_active = False
    integration.last_error = str(error)
    integration.last_error_at = datetime.now(timezone.utc)
    db.commit()