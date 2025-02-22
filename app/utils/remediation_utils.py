# app/utils/remediation_utils.py
def generate_remediation_steps(threat_type):
    """Generate remediation steps for a given threat type."""
    steps = {
        "PHISHING": ["Move email to quarantine", "Notify the user"],
        "MALWARE": ["Block the sender", "Remove attachment"],
        "SPAM": ["Mark as spam", "Add sender to spam list"],
        "BEC": ["Verify sender identity", "Report to admin"],
        "IMPERSONATION": ["Warn the user", "Investigate the sender"]
    }
    return steps.get(threat_type, ["No specific action required"])



# Helper function to generate a remediation suggestion based on severity.
def get_remediation_suggestion_for_severity(severity: str) -> str:
    """
    Returns a remediation suggestion string based on the given severity.
    """
    if severity == "High":
        return "Do not interact with this email. Report it as phishing and delete it immediately."
    elif severity == "Medium":
        return "Review the email carefully and verify the sender's identity before proceeding."
    elif severity == "Low":
        return "This email appears mostly legitimate, but exercise caution."
    return "Exercise caution."