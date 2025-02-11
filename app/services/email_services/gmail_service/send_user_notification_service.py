from typing import Optional
from app.core.config import settings
from app.services.email_services.send_email_notifications.email_sending_service import EmailSendingService
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.email_service = EmailSendingService()
        
    def _get_notification_template(self, notification_type: str, title: str, message: str) -> tuple[str, str]:
        """
        Returns the HTML and plain text templates for different notification types
        """
        html_template = f"""
        <html>
        <body>
            <h2>{title}</h2>
            <p>{message}</p>
            <p>Regards,<br>Your App Team</p>
        </body>
        </html>
        """
        
        plain_template = f"""
        {title}
        
        {message}
        
        Regards,
        Your App Team
        """
        
        # Customize templates based on notification type
        if notification_type == "token_expiring":
            html_template = f"""
            <html>
            <body>
                <h2>{title}</h2>
                <p>{message}</p>
                <p>To maintain uninterrupted service, please click below to re-authenticate:</p>
                <a href="settings.APP_URL/settings/email">Re-authenticate Gmail</a>
                <p>Regards,<br>Your App Team</p>
            </body>
            </html>
            """
        elif notification_type == "token_expired" or notification_type == "token_revoked":
            html_template = f"""
            <html>
            <body>
                <h2>{title}</h2>
                <p>{message}</p>
                <p>To restore your email sync, please re-authenticate your account:</p>
                <a href="settings.APP_URL/settings/email">Re-authenticate Gmail</a>
                <p>Regards,<br>Your App Team</p>
            </body>
            </html>
            """
            
        return html_template, plain_template

    def send_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        email: Optional[str] = None,
        notification_type: Optional[str] = "general"
    ) -> None:
        """
        Sends a notification to the user through available channels (email, etc.)
        
        Args:
            user_id: The ID of the user to notify
            title: The notification title
            message: The notification message
            email: Optional email address to send to
            notification_type: Type of notification for template selection
        """
        try:
            # Log the notification
            logger.info(f"Sending {notification_type} notification to user {user_id}: {title}")
            
            # Send email if address is provided
            if email:
                html_template, plain_template = self._get_notification_template(
                    notification_type,
                    title,
                    message
                )
                
                self.email_service.send_email(
                    to_email=email,
                    subject=title,
                    body=plain_template,
                    html_body=html_template
                )
                
            # Here you could add other notification channels like:
            # - Push notifications
            # - In-app notifications
            # - SMS
            # - Webhook calls
            
            logger.info(f"Successfully sent {notification_type} notification to user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send notification to user {user_id}: {str(e)}")
            raise

# Create a singleton instance
_notification_service = NotificationService()

def send_notification(
    user_id: int,
    title: str,
    message: str,
    email: Optional[str] = None,
    notification_type: Optional[str] = "general"
) -> None:
    """
    Helper function to send notifications using the singleton NotificationService instance
    """
    return _notification_service.send_notification(
        user_id=user_id,
        title=title,
        message=message,
        email=email,
        notification_type=notification_type
    )