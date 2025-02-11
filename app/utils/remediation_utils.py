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