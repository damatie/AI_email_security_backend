import logging
import json
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.email_services.analysis.phishing_detection.phishing_detector import detect_phishing
from app.models.email_analysis.threat_analysis import ThreatAnalysis
from app.models.email_analysis.email_analysis_highlights import EmailAnalysisHighlights
from app.models.email_analysis.RemediationLog import RemediationLog
from app.utils.enums import RiskLevelEnum, ThreatTypeEnum, ThreatSeverityEnum

logger = logging.getLogger(__name__)

def save_analysis_results(email, phishing_result, db_session: Session):
    """
    Save the overall phishing analysis results to the database using a normalized design.
    Detailed risk indicators are stored in a separate EmailAnalysisHighlights record.
    """
    try:
        # Determine threat type and severity based on the classification.
        if phishing_result.get('classification') == ThreatTypeEnum.PHISHING:
            threat_type = ThreatTypeEnum.PHISHING
            severity = ThreatSeverityEnum.HIGH
        elif phishing_result.get('classification') == ThreatTypeEnum.SUSPICIOUS:
            threat_type = ThreatTypeEnum.SUSPICIOUS
            severity = ThreatSeverityEnum.MEDIUM
        else:
            threat_type = ThreatTypeEnum.SAFE
            severity = ThreatSeverityEnum.LOW

        # Create the ThreatAnalysis record.
        threat_analysis = ThreatAnalysis(
            email_id=email.id,
            is_threat=(threat_type != ThreatTypeEnum.SAFE),
            threat_type=threat_type,
            severity=severity,
            confidence_score=phishing_result.get('technical_details', {}).get('model_score', 0),
            remediation_steps=[phishing_result.get('recommendation')],
            analyzed_at=datetime.now(),
            explanation=phishing_result.get('summary'),
            model_version="1.0"
        )
        db_session.add(threat_analysis)
        db_session.flush()  # Flush so that threat_analysis.id is available.

        # Save each individual risk factor as a separate highlight.
        # Assume phishing_result['risk_factors'] is a list of strings.
        if phishing_result.get('risk_factors'):
            for factor in phishing_result['risk_factors']:
                # Customize the mapping for each risk factor if desired.
                highlight_type = "Phishing Indicator"  # Standard type for all factors
                content = factor
                # For demonstration, we assign "Medium" severity to each; you may add custom logic.
                factor_severity = "Medium"
                description = f"Indicator detected: {factor}"
                remediation_suggestion = "Review the email carefully and verify the sender before interacting."
                
                highlight = EmailAnalysisHighlights(
                    email_id=email.id,
                    threat_analysis_id=threat_analysis.id,
                    highlight_type=highlight_type,
                    content=content,
                    severity=factor_severity,
                    description=description,
                    remediation_suggestion=remediation_suggestion
                )
                db_session.add(highlight)

        # Save a remediation log entry.
        remediation_log = RemediationLog(
            email_id=email.id,
            action_taken=phishing_result.get('recommendation', 'No action specified'),
            performed_by="System"
        )
        db_session.add(remediation_log)

        # Update the email's processed timestamp.
        email.processed_at = datetime.now()

        # Commit all changes.
        db_session.commit()
        logger.info(f"Analysis results saved for email {email.id}")
        return threat_analysis

    except Exception as e:
        db_session.rollback()
        logger.error(f"Error saving analysis results: {e}", exc_info=True)
        raise

def analyze_email(email, body_content: str, db_session: Session):
    """
    Analyze an email for phishing threats and store the analysis results in the database.
    
    Args:
        email (Email): The email metadata record.
        body_content (str): The full email content extracted from the email.
        db_session (Session): The database session for storing analysis results.
    
    Returns:
        dict: The phishing detection results, including analysis time and risk level.
    """
    try:
        start_time = time.time()
        
        # Prepare the data for analysis.
        email_dict = {
            "subject": str(email.subject) if email.subject else "",
            "body": str(body_content) if body_content else "",
            "sender": str(email.sender) if email.sender else "",
            "recipient": str(email.recipient) if email.recipient else "",
            "received_at": email.received_at.strftime("%a, %d %b %Y %H:%M:%S GMT") if email.received_at else "Unknown"
        }
        
        # Run the phishing detection model.
        phishing_result = detect_phishing(email_dict)
        
        analysis_time = time.time() - start_time
        phishing_result["analysis_time"] = analysis_time
        logger.info(f"Phishing detection for email {email.id} took {analysis_time:.2f} seconds")
        
        # If the model returned an error, log and return the error.
        if "error" in phishing_result:
            logger.error(f"Phishing detection error: {phishing_result['error']}")
            return phishing_result
        
        # Map the classification to a risk level using your RiskLevelEnum.
        # For example, if the classification is PHISHING, then the risk level is HIGH_RISK.
        if phishing_result.get('classification') == ThreatTypeEnum.PHISHING:
            phishing_result["risk_level"] = RiskLevelEnum.HIGH_RISK
        elif phishing_result.get('classification') == ThreatTypeEnum.SUSPICIOUS:
            phishing_result["risk_level"] = RiskLevelEnum.MEDIUM_RISK
        else:
            phishing_result["risk_level"] = RiskLevelEnum.LOW_RISK
        
        # Save the analysis results to the database (normalized approach).
        save_analysis_results(email, phishing_result, db_session)
        
        logger.info(f"Email analysis completed for email_id: {email.id}")
        print(json.dumps(phishing_result, indent=2))
        return phishing_result

    except AttributeError as ae:
        logger.error(f"Email object attribute error: {ae}")
        return {"error": f"Email object attribute error: {str(ae)}"}
    except Exception as e:
        logger.error(f"Error analyzing email: {e}")
        return {"error": f"Analysis failed: {str(e)}"}
