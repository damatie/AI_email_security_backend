import logging

from app.utils.enums import ThreatTypeEnum

logger = logging.getLogger(__name__)

def list_labels(service):
    try:
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        logger.info("Existing labels:")
        for label in labels:
            logger.info(f"Label Name: {label['name']}, Label ID: {label['id']}")
        return labels
    except Exception as e:
        logger.error(f"Error listing labels: {e}")
        return []

def create_label(service, label_name, color=None):
    try:
        label_body = {
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show"
        }
        if color:
            label_body["color"] = color
        label = service.users().labels().create(userId='me', body=label_body).execute()
        logger.info(f"Created label: {label}")
        return label['id']
    except Exception as e:
        logger.error(f"Error creating label '{label_name}': {e}")
        return None

def get_or_create_label(service, label_name):
    """
    Get a label by name; if it doesn't exist, create it with a color based on industry standards.
    """
    labels = list_labels(service)
    for label in labels:
        if label['name'].lower() == label_name.lower():
            logger.info(f"Found existing label '{label_name}' with ID: {label['id']}")
            return label['id']
    # Define color mapping using allowed Gmail colors.
    risk_colors = {
         "Phishing": {"backgroundColor": "#fb4c2f", "textColor": "#ffffff"},   # Red-ish
         "Suspicious": {"backgroundColor": "#ffad47", "textColor": "#ffffff"}, # Orange-ish
         "Safe": {"backgroundColor": "#16a765", "textColor": "#ffffff"}        # Green-ish
         # Optionally, you could add a "Malicious" label if needed.
    }
    color = risk_colors.get(label_name, None)
    logger.info(f"Label '{label_name}' not found. Creating it with color: {color}.")
    return create_label(service, label_name, color)

def add_risk_label(service, message_id: str, risk_label_id: str):
    try:
        msg_labels = {
            "addLabelIds": [risk_label_id],
            "removeLabelIds": []
        }
        service.users().messages().modify(userId='me', id=message_id, body=msg_labels).execute()
        logger.info(f"Added label {risk_label_id} to message {message_id}")
    except Exception as e:
        logger.error(f"Failed to add risk label for message {message_id}: {e}")
