#app/services/email_services/gmail_service/connect_gmail_service.py
import json
import logging
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.models.emails.email_integrations import EmailIntegration
from app.models.emails.fetch_email_log import FetchEmailLog 
from app.core.config import settings
from sqlalchemy.sql import func
from app.utils.enums import EmailProviderEnum

# Define the Gmail scopes
SCOPES = settings.GMAIL_SCOPES

logger = logging.getLogger(__name__)


def generate_gmail_auth_url() -> str:
    """
    Generate Gmail OAuth2 authorization URL.

    Returns:
        str: Authorization URL.
    """
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.GMAIL_CLIENT_SECRET_PATH,
            SCOPES,
            redirect_uri=settings.GMAIL_REDIRECT_URI
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url
    except Exception as e:
        logger.error(f"Failed to generate Gmail auth URL: {e}")
        raise


def fetch_gmail_token(auth_code: str, db: Session, user_id: int = None, company_id: int = None) -> EmailIntegration:
    """
    Fetch Gmail token using authorization code and store it in the database.

    Args:
        auth_code: Authorization code from the user.
        db: Database session.
        user_id: ID of the individual user (if applicable).
        company_id: ID of the company (if applicable).

    Returns:
        EmailIntegration: The created or updated email integration entry.
    """
    try:
        # Initialize OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.GMAIL_CLIENT_SECRET_PATH,
            SCOPES,
            redirect_uri=settings.GMAIL_REDIRECT_URI
        )
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials

        # Prepare token data
        token_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }

        # Store or update integration in the database
        integration = db.query(EmailIntegration).filter(
            EmailIntegration.user_id == user_id if user_id else EmailIntegration.company_id == company_id,
            EmailIntegration.provider_name == EmailProviderEnum.GMAIL
        ).first()

        if integration:
            integration.set_token(json.dumps(token_data))
            integration.is_connected = True
            integration.updated_at = func.now()
        else:
            integration = EmailIntegration(
                user_id=user_id,
                company_id=company_id,
                provider_name=EmailProviderEnum.GMAIL,
                is_connected=True,
            )
            integration.set_token(json.dumps(token_data))
            db.add(integration)

        db.commit()
        db.refresh(integration)

        # Set up Gmail notifications
        setup_gmail_watch(credentials, user_id=user_id, db=db)

        # Save initial historyId
        save_initial_history_id(credentials, user_id=user_id, db=db)

        logger.info(f"Gmail connected successfully for {'user' if user_id else 'company'}.")
        return integration
    except Exception as e:
        logger.error(f"Failed to connect Gmail: {e}")
        raise



def setup_gmail_watch(credentials: Credentials, user_id: int, db: Session):
    """
    Set up Gmail push notifications for a user's account.

    Args:
        credentials: Google OAuth2 credentials.
        user_id: ID of the user.
        db: Database session.
    """
    try:
        service = build('gmail', 'v1', credentials=credentials)
        body = {
            'topicName': settings.GMAIL_PUBSUB_TOPIC,
            'labelIds': ['INBOX'],  # Only watch the INBOX
        }
        watch_response = service.users().watch(userId='me', body=body).execute()
        logger.info(f"Gmail watch setup for user {user_id}: {watch_response}")
    except Exception as e:
        logger.error(f"Error setting up Gmail watch for user {user_id}: {e}")
        raise


def save_initial_history_id(credentials: Credentials, user_id: int, db: Session):
    """
    Save the initial historyId for a user's Gmail account.

    Args:
        credentials: Google OAuth2 credentials.
        user_id: ID of the user.
        db: Database session.
    """
    try:
        service = build('gmail', 'v1', credentials=credentials)
        profile = service.users().getProfile(userId='me').execute()
        history_id = profile.get('historyId')

        if history_id:
            fetch_log = db.query(FetchEmailLog).filter(FetchEmailLog.user_id == user_id).first()
            if fetch_log:
                fetch_log.history_id = history_id
            else:
                fetch_log = FetchEmailLog(user_id=user_id, history_id=history_id)
                db.add(fetch_log)
            db.commit()
            logger.info(f"Initial historyId {history_id} stored for user {user_id}.")
    except Exception as e:
        logger.error(f"Error saving initial historyId for user {user_id}: {e}")
        raise


def refresh_gmail_token(db: Session, user_id: int = None, company_id: int = None) -> str:
    """
    Refresh the Gmail token for the user or company.

    Args:
        db: Database session.
        user_id: ID of the individual user (if applicable).
        company_id: ID of the company (if applicable).

    Returns:
        str: New access token.
    """
    try:
        integration = db.query(EmailIntegration).filter(
            EmailIntegration.user_id == user_id if user_id else EmailIntegration.company_id == company_id
        ).first()

        if not integration:
            raise Exception("Gmail integration not found.")

        token_data = json.loads(integration.get_token())
        credentials = Credentials.from_authorized_user_info(token_data, SCOPES)

        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                token_data["token"] = credentials.token
                integration.set_token(json.dumps(token_data))
                db.commit()
                logger.info("Gmail token refreshed successfully.")
                return credentials.token
            else:
                raise Exception("Refresh token is missing or invalid.")
        return credentials.token
    except Exception as e:
        logger.error(f"Failed to refresh Gmail token: {e}")
        raise


def test_gmail_connection(db: Session, user_id: int = None, company_id: int = None) -> bool:
    """
    Test the Gmail connection to ensure the token is valid.

    Args:
        db: Database session.
        user_id: ID of the individual user (if applicable).
        company_id: ID of the company (if applicable).

    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    try:
        refresh_gmail_token(db=db, user_id=user_id, company_id=company_id)

        integration = db.query(EmailIntegration).filter(
            EmailIntegration.user_id == user_id if user_id else EmailIntegration.company_id == company_id
        ).first()

        token_data = json.loads(integration.get_token())
        credentials = Credentials.from_authorized_user_info(token_data, SCOPES)

        service = build('gmail', 'v1', credentials=credentials)
        profile = service.users().getProfile(userId='me').execute()
        logger.info(f"Connection test successful: {profile}")
        return True
    except HttpError as e:
        logger.error(f"HTTP Error during Gmail connection test: {e}")
        return False
    except Exception as e:
        logger.error(f"Error during Gmail connection test: {e}")
        return False


def get_gmail_credentials(db: Session, user_id: int = None, company_id: int = None) -> Credentials:
    """
    Retrieve Gmail credentials from the database.

    Args:
        db: Database session.
        user_id: ID of the individual user (if applicable).
        company_id: ID of the company (if applicable).

    Returns:
        Credentials: Google OAuth2 credentials.
    """
    try:
        refresh_gmail_token(db=db, user_id=user_id, company_id=company_id)

        integration = db.query(EmailIntegration).filter(
            EmailIntegration.user_id == user_id if user_id else EmailIntegration.company_id == company_id
        ).first()

        if not integration:
            raise Exception("Gmail integration not found.")

        token_data = json.loads(integration.get_token())
        return Credentials.from_authorized_user_info(token_data, SCOPES)
    except Exception as e:
        logger.error(f"Error retrieving Gmail credentials: {e}")
        raise
