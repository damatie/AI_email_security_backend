import base64
import logging

logger = logging.getLogger(__name__)

def extract_email_body(message):
    """
    Extract the body content from the Gmail API message.

    Args:
        message (dict): The email message object from the Gmail API.

    Returns:
        str: The extracted email body content.
    """
    try:
        parts = message.get('payload', {}).get('parts', [])
        body_content = ""

        for part in parts:
            if part.get('mimeType') == 'text/plain':  # Handle plain text
                body_content += part['body'].get('data', '')
            elif part.get('mimeType') == 'text/html':  # Handle HTML
                body_content += part['body'].get('data', '')

        # Decode Base64 content
        decoded_body = base64.urlsafe_b64decode(body_content).decode('utf-8', errors='ignore')
        return decoded_body

    except Exception as e:
        logger.error(f"Error extracting email body: {e}")
        return ""
