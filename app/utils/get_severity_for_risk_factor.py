# Helper function to determine severity based on risk factor text.
def get_severity_for_risk_factor(factor: str) -> str:
    """
    Determines the severity for a given risk factor based on keywords.
    Returns one of: "High", "Medium", or "Low".
    """
    factor_lower = factor.lower()
    if "malicious url" in factor_lower:
        return "High"
    elif "suspicious url" in factor_lower:
        return "Medium"
    elif "requests sensitive information" in factor_lower:
        return "High"
    elif "sender's domain was registered" in factor_lower:
        return "High"
    elif "contains threat language" in factor_lower:
        return "High"
    elif "uses urgency language" in factor_lower:
        return "Medium"
    elif "grammar and spelling issues" in factor_lower:
        return "Low"
    elif "suspicious sender domain" in factor_lower:
        return "High"
    # Fallback severity if no keywords match.
    return "Medium"