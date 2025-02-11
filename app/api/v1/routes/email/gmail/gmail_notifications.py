# app/api/gmail_notification.py
import base64
import json
import logging
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from starlette.requests import ClientDisconnect
from app.services.email_services.gmail_service.pubsub_handler import process_notification

logger = logging.getLogger(__name__)
gmail_notifications_router = APIRouter()

@gmail_notifications_router.post("/notifications")
async def gmail_notifications(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Handle Gmail Pub/Sub push notifications.
    """
    try:
        raw_body = await request.body()

        if not raw_body:
            logger.warning("Received empty request body from Gmail Pub/Sub.")
            return {"status": "error", "message": "Empty request body"}
        try:
            body = json.loads(raw_body.decode("utf-8"))

        except json.JSONDecodeError:
            logger.error("Invalid JSON format in request body.")
            raise HTTPException(status_code=400, detail="Invalid JSON format.")
        logger.info(f"Received Gmail notification: {json.dumps(body, indent=2)}")

        if "message" not in body:
            logger.error("Invalid Pub/Sub notification: Missing 'message' field.")
            raise HTTPException(status_code=400, detail="Invalid Pub/Sub notification: Missing 'message' field.")
        encoded_message = body["message"].get("data")

        if not encoded_message:
            logger.error("Invalid Pub/Sub notification: Missing 'data' field.")
            raise HTTPException(status_code=400, detail="Invalid Pub/Sub notification: Missing 'data' field.")
        try:
            decoded_message = base64.urlsafe_b64decode(encoded_message).decode("utf-8")
            notification_data = json.loads(decoded_message)

        except (base64.binascii.Error, json.JSONDecodeError) as decode_error:
            logger.error(f"Error decoding Pub/Sub message: {decode_error}")
            raise HTTPException(status_code=400, detail="Error decoding Pub/Sub message.")
        
        # Schedule the notification processing task.
        background_tasks.add_task(process_notification, notification_data, background_tasks)
        return {"status": "success", "message": "Notification received. Processing in background."}
    except ClientDisconnect:
        logger.warning("Client disconnected before request could be completed.")
        return {"status": "error", "message": "Client disconnected before request completion."}
    
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        logger.error(f"Unexpected error handling Gmail notification: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected error handling Gmail notification.")
