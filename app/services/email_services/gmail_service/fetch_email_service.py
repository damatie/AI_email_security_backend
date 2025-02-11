import logging
import json
import time
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import asyncio

from app.models.emails.fetch_email_log import FetchEmailLog
from app.models.emails.email_integrations import EmailIntegration
from app.models.users.user import User
from app.utils.enums import EmailProviderEnum
from app.core.config import settings
from app.services.email_services.gmail_service.connect_gmail_service import refresh_gmail_token
from app.services.email_services.gmail_service.modules.handle_token_module import check_token_status, handle_token_error
from app.services.email_services.gmail_service.modules.process_email_module import process_email
from app.db.session import SessionLocal  # Our session factory

logger = logging.getLogger(__name__)
SCOPES = settings.GMAIL_SCOPES

def get_latest_history_id(service):
    """Get the latest history ID from Gmail for new messages."""
    try:
        results = service.users().messages().list(userId='me', maxResults=1).execute()
        if results.get('messages'):
            message = service.users().messages().get(
                userId='me',
                id=results['messages'][0]['id'],
                format='minimal'
            ).execute()
            return message.get('historyId')
    except Exception as e:
        logger.error(f"Error getting latest history ID: {e}")
    return None

def initialize_gmail_service(db: Session, integration: EmailIntegration) -> tuple:
    """Initialize Gmail service with proper credentials."""
    try:
        refresh_gmail_token(db, user_id=integration.user_id)
        token_info = json.loads(integration.get_token())
        credentials = Credentials.from_authorized_user_info(token_info, SCOPES)
        service = build(settings.GMAIL_HOST, settings.GMAIL_V, credentials=credentials)
        return service, True
    except Exception as e:
        logger.error(f"Error initializing Gmail service: {e}")
        handle_token_error(db, integration, e)
        return None, False

def check_for_new_emails(db: Session, user_id: int = None, email_address: str = None, history_id: str = None):
    """
    Check for new emails using the Gmail API and process them.
    
    For an MVP targeting individual users, this function will:
      - Perform an initial scan of the most recent 50 emails if no fetch log exists or if the initial scan has not been completed.
      - Otherwise, perform incremental scanning using Gmail’s history API.
    
    This function uses its own DB session (passed in as `db`) and logs the total processing time.
    """
    start_time = time.time()
    logger.info(f"Email processing started for user_id={user_id} at {start_time}")
    
    try:
        # Resolve user_id if only the email address is provided.
        if email_address and not user_id:
            user = db.query(User).filter(User.email == email_address).first()
            if not user:
                logger.error(f"No user found with email: {email_address}")
                return
            user_id = user.id

        # Retrieve the Gmail integration details for the user.
        integration = db.query(EmailIntegration).filter(
            EmailIntegration.user_id == user_id,
            EmailIntegration.provider_name == EmailProviderEnum.GMAIL
        ).first()

        if not integration:
            logger.error(f"No Gmail integration found for user {user_id}")
            return

        # Validate token and initialize the Gmail service.
        if not check_token_status(db, integration):
            logger.warning(f"Token issues detected for user {user_id}")
            return

        service, success = initialize_gmail_service(db, integration)
        if not success:
            return

        # Retrieve the fetch log for this user.
        fetch_log = db.query(FetchEmailLog).filter(FetchEmailLog.user_id == user_id).first()
        
        # If no fetch log exists, or the initial scan has not been completed, perform the initial scan.
        if not fetch_log or (fetch_log and not fetch_log.initial_scan_completed):
            logger.info(f"No fetch log or initial scan incomplete for user {user_id}. Performing initial scan of recent 50 emails.")
            messages_results = service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                maxResults=50  # Scan the most recent 50 emails
            ).execute()
            messages_to_process = {msg['id'] for msg in messages_results.get('messages', [])}
            new_history_id = get_latest_history_id(service)
            
            # Process each message in the initial batch.
            for message_id in messages_to_process:
                process_email(service, message_id, user_id, db)
            
            # Update (or create) the fetch log with the new history ID and mark the initial scan as completed.
            current_time = datetime.now(timezone.utc)
            if fetch_log:
                fetch_log.history_id = new_history_id
                fetch_log.last_fetched_at = current_time
                fetch_log.initial_scan_completed = True
            else:
                fetch_log = FetchEmailLog(
                    user_id=user_id,
                    history_id=new_history_id,
                    last_fetched_at=current_time,
                    initial_scan_completed=True
                )
                db.add(fetch_log)
            db.commit()
        else:
            # Incremental scanning branch: process only new messages.
            logger.info(f"Fetch log exists and initial scan completed for user {user_id}. Performing incremental scan.")
            start_history_id = fetch_log.history_id  # Use the history ID from the fetch log.
            latest_new_message_history_id = start_history_id
            messages_to_process = set()
            page_token = None

            while True:
                history_results = service.users().history().list(
                    userId='me',
                    startHistoryId=start_history_id,
                    historyTypes=['messageAdded'],
                    pageToken=page_token
                ).execute()
                for record in history_results.get('history', []):
                    for message in record.get('messages', []):
                        message_id = message['id']
                        msg_details = service.users().messages().get(
                            userId='me',
                            id=message_id,
                            format='minimal'
                        ).execute()
                        if 'INBOX' in msg_details.get('labelIds', []):
                            messages_to_process.add(message_id)
                            msg_history_id = msg_details.get('historyId')
                            if msg_history_id and int(msg_history_id) > int(latest_new_message_history_id):
                                latest_new_message_history_id = msg_history_id
                page_token = history_results.get('nextPageToken')
                if not page_token:
                    break

            for message_id in messages_to_process:
                process_email(service, message_id, user_id, db)

            # Update the fetch log with the latest history ID if new messages were processed.
            current_time = datetime.now(timezone.utc)
            if latest_new_message_history_id != start_history_id:
                fetch_log.history_id = latest_new_message_history_id
                fetch_log.last_fetched_at = current_time
                db.commit()

    except Exception as e:
        logger.error(f"Error in check_for_new_emails: {e}", exc_info=True)
        db.rollback()
        raise

    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Total processing time for user {user_id} is {elapsed_time:.2f} seconds")

def check_for_new_emails_task(user_id: int = None, email_address: str = None, history_id: str = None):
    """
    Wrapper for check_for_new_emails that creates its own DB session.
    This function is scheduled as a background task.
    """
    db = SessionLocal()
    try:
        check_for_new_emails(db, user_id=user_id, email_address=email_address, history_id=history_id)
    except Exception as e:
        logger.error(f"Exception in check_for_new_emails_task: {e}", exc_info=True)
    finally:
        db.close()

async def async_check_for_new_emails_task(user_id: int = None, email_address: str = None, history_id: str = None):
    """
    Asynchronous wrapper for offloading the synchronous email check to a thread.
    This wrapper handles task cancellation gracefully.
    """
    try:
        await asyncio.to_thread(check_for_new_emails_task, user_id, email_address, history_id)
    except asyncio.CancelledError:
        logger.info("async_check_for_new_emails_task was cancelled (likely due to shutdown).")
        raise
