# app/services/email_services/gmail_service/pubsub_handler.py
import logging
import json
from fastapi import BackgroundTasks
from app.services.email_services.gmail_service.fetch_email_service import async_check_for_new_emails_task

logger = logging.getLogger(__name__)

def process_notification(notification_data: dict, background_tasks: BackgroundTasks):
    """
    Process a Gmail Pub/Sub notification and schedule email fetching asynchronously.
    """
    try:
        logger.info(f"Received Gmail notification: {json.dumps(notification_data, indent=2)}")
        history_id = notification_data.get("historyId")

        if not history_id:
            logger.error("Notification missing required 'historyId' field.")
            return {"status": "error", "message": "Missing historyId in notification."}
        
        user_id = notification_data.get("user_id")
        email_address = notification_data.get("emailAddress")

        if not user_id and not email_address:
            logger.error("Notification must contain either 'user_id' or 'emailAddress'.")
            return {"status": "error", "message": "Invalid notification format."}
        logger.info(f"Processing notification: user_id={user_id}, email_address={email_address}, history_id={history_id}")

        # Schedule the asynchronous email-fetching task.
        background_tasks.add_task(async_check_for_new_emails_task, user_id=user_id, email_address=email_address, history_id=history_id)
        return {"status": "success", "message": "Notification processing started."}
    
    except Exception as e:
        logger.error(f"Error processing Gmail notification: {e}", exc_info=True)
        return {"status": "error", "message": "Unexpected error during processing."}
