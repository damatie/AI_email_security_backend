# Email Detail Endpoint
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.v1.routes.user_dashboard.scanned_emails.email_details_schema import EmailDetailResponseSchema
from app.db.deps import get_db
from app.utils.get_current_user import get_current_user
from app.utils.response_helper import create_response
from app.models.emails.email import Email
from app.models.email_analysis.email_analysis_highlights import EmailAnalysisHighlights
from app.models.email_analysis.RemediationLog import RemediationLog
import logging


get_email_details_router = APIRouter()
logger = logging.getLogger(__name__)

@get_email_details_router.get(
        "/email/{email_id}", 
        response_model=EmailDetailResponseSchema,
        description= "Get details and analysis for scanned email" )
async def email_details(
    email_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Returns detailed analysis for a specific email.
    """
    try:
        email = (
            db.query(Email)
              .filter(Email.user_id == current_user.id, Email.email_id == email_id)
              .first()
        )
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Build threat analysis data.
        analysis_data = {}
        if email.threat_analysis:
            analysis_data = {
                "is_threat": email.threat_analysis.is_threat,
                "threat_type": email.threat_analysis.threat_type.value,
                "severity": email.threat_analysis.severity.value if email.threat_analysis.severity else None,
                "confidence_score": email.threat_analysis.confidence_score,
                "remediation_steps": email.threat_analysis.remediation_steps,
                "explanation": email.threat_analysis.explanation,
                "model_version": email.threat_analysis.model_version,
                "analyzed_at": email.threat_analysis.analyzed_at.isoformat()
            }
            # Get risk highlights.
            highlights = (
                db.query(EmailAnalysisHighlights)
                  .filter(EmailAnalysisHighlights.email_id == email.id)
                  .all()
            )
            analysis_data["highlights"] = [{
                "highlight_type": h.highlight_type,
                "content": h.content,
                "severity": h.severity,
                "description": h.description,
                "remediation_suggestion": h.remediation_suggestion,
                "created_at": h.created_at.isoformat()
            } for h in highlights]
        
        # Get remediation logs.
        remediation_logs = (
            db.query(RemediationLog)
              .filter(RemediationLog.email_id == email.id)
              .all()
        )
        remediation_data = [{
            "action_taken": log.action_taken,
            "performed_by": log.performed_by,
            "timestamp": log.timestamp.isoformat()
        } for log in remediation_logs]
        
        detail_data = {
            "email_id": email.email_id,
            "subject": email.subject,
            "sender": email.sender,
            "recipient": email.recipient,
            "received_at": email.received_at.isoformat(),
            "processed_at": email.processed_at.isoformat() if email.processed_at else None,
            "threat_analysis": analysis_data,
            "remediation_logs": remediation_data
        }
        
        return create_response(
            status="success",
            msg="Email detail retrieved successfully.",
            data=detail_data
        )
    except Exception as e:
        logger.error(f"Error retrieving email detail: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
