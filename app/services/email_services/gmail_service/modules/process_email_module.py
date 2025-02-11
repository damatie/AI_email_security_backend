import logging
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.models.emails.email import Email
from app.services.email_services.analysis.analyze_email import analyze_email
from app.utils.enums import ThreatTypeEnum
from app.utils.extract_email_body import extract_email_body
from app.utils.gmail_label_utils import get_or_create_label, add_risk_label

logger = logging.getLogger(__name__)

def process_email(service, message_id: str, user_id: int, db_session: Session):
    """
    Process a single email: fetch content, save metadata, run risk analysis,
    and apply a risk label dynamically based on the analysis.
    
    Args:
        service: The Gmail API service instance.
        message_id (str): The unique Gmail message ID.
        user_id (int): The ID of the user owning the email.
        db_session (Session): The database session.
    
    Returns:
        dict: Status information about the processing.
    """
    try:
        # Fetch email content from Gmail API.
        message = service.users().messages().get(userId='me', id=message_id, format='full').execute()

        # Extract email headers.
        headers = {header['name']: header['value'] for header in message['payload']['headers']}
        subject = headers.get('Subject', 'No Subject')
        sender = headers.get('From', 'Unknown')
        recipient = headers.get('To', 'Unknown')

        # Parse the received_at timestamp.
        # If parsing fails or header is missing, use current UTC time.
        raw_date = headers.get('Date', None)
        if raw_date:
            try:
                received_at = parsedate_to_datetime(raw_date)
            except Exception as e:
                logger.warning(f"Failed to parse date '{raw_date}' for email {message_id}: {e}")
                received_at = datetime.now(timezone.utc)
        else:
            received_at = datetime.now(timezone.utc)

        # Extract the full email body content.
        body_content = extract_email_body(message)

        # Prepare email metadata for database upsert.
        email_data = {
            "user_id": user_id,
            "email_id": message_id,
            "subject": subject,
            "sender": sender,
            "recipient": recipient,
            "received_at": received_at
        }
        stmt = insert(Email).values(**email_data)
        stmt = stmt.on_conflict_do_nothing(index_elements=['email_id'])
        result = db_session.execute(stmt)
        db_session.commit()

        if result.rowcount == 0:
            logger.info(f"Email {message_id} already exists (upsert), skipping processing.")
            return {"status": "skipped", "message": "Email already processed"}

        logger.info(f"Saved email {message_id} metadata to the database using upsert.")
        email = db_session.query(Email).filter(Email.email_id == message_id, Email.user_id == user_id).first()

        # Run phishing analysis and capture the result.
        model_start_time = time.time()
        analysis_result = analyze_email(email, body_content, db_session)
        model_end_time = time.time()
        logger.info(f"Model analysis for email {message_id} took {model_end_time - model_start_time:.2f} seconds")

        # Map the analysis result to industry-standard labels.
        # Convert enum classification to a string label.
        classification = analysis_result.get("classification", ThreatTypeEnum.SAFE)
        if classification == ThreatTypeEnum.PHISHING:
            risk_level = "Phishing"
        elif classification == ThreatTypeEnum.SUSPICIOUS:
            risk_level = "Suspicious"
        else:
            risk_level = "Safe"

        logger.info(f"Determined risk level: {risk_level}")

        # Dynamically get or create the corresponding Gmail label.
        risk_label_id = get_or_create_label(service, risk_level)
        if risk_label_id:
            add_risk_label(service, message_id, risk_label_id)
        else:
            logger.error(f"Could not retrieve or create label for risk level: {risk_level}")

        logger.info(f"Email {message_id} processed successfully.")
        return {"status": "success", "message": f"Email {message_id} processed successfully."}

    except Exception as e:
        db_session.rollback()
        logger.error(f"Error processing email {message_id}: {e}", exc_info=True)
        raise
