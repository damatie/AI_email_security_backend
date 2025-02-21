from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.utils.get_current_user import get_current_user
from app.utils.response_helper import create_response
from app.models.emails.email import Email
from app.models.email_analysis.threat_analysis import ThreatAnalysis
from app.models.email_analysis.RemediationLog import RemediationLog
from app.schemas.user_dashboard.scanned_emails.reclassification_schema import ReclassificationRequestSchema, ReclassificationResponseSchema
from app.utils.enums import ThreatTypeEnum, ThreatSeverityEnum
import logging
from datetime import datetime, timezone

email_reclassification_router = APIRouter()
logger = logging.getLogger(__name__)

@email_reclassification_router.put("/email/{email_id}/reclassify", response_model=ReclassificationResponseSchema)
async def reclassify_email(
    email_id: str,
    payload: ReclassificationRequestSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Allows the user to reclassify an email that was originally marked as Safe (or another classification)
    into a different category (e.g., Phishing or Suspicious). This endpoint updates the threat analysis
    record and logs the action.
    """
    try:
        # Fetch the email ensuring it belongs to the current user.
        email = db.query(Email).filter(
            Email.user_id == current_user.id, 
            Email.email_id == email_id
        ).first()
        if not email:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")

        # Determine the new threat type and severity based on the requested classification.
        new_classification = payload.new_classification.lower()
        if new_classification == ThreatTypeEnum.PHISHING.lower():
            threat_type = ThreatTypeEnum.PHISHING
            severity = ThreatSeverityEnum.HIGH
        elif new_classification == ThreatTypeEnum.SUSPICIOUS.lower():
            threat_type = ThreatTypeEnum.SUSPICIOUS
            severity = ThreatSeverityEnum.MEDIUM
        elif new_classification == ThreatTypeEnum.SAFE.lower():
            threat_type = ThreatTypeEnum.SAFE
            severity = ThreatSeverityEnum.LOW
        else:
            raise HTTPException(status_code=400, detail="Invalid classification value")

        # Get the associated ThreatAnalysis record; if not present, create a new one.
        threat_analysis = db.query(ThreatAnalysis).filter(ThreatAnalysis.email_id == email.id).first()
        confidence_score = 1.0
        if threat_analysis:
            # Update the existing record.
            threat_analysis.threat_type = threat_type
            threat_analysis.is_threat = (threat_type != ThreatTypeEnum.SAFE)
            threat_analysis.severity = severity
            threat_analysis.confidence_score = confidence_score  # Assuming full confidence after user feedback.
            threat_analysis.explanation = {"updated_by_user": payload.reason}
            threat_analysis.analyzed_at = datetime.now(timezone.utc)
        else:
            # Create a new ThreatAnalysis record if one does not exist.
            threat_analysis = ThreatAnalysis(
                email_id=email.id,
                is_threat=(threat_type != ThreatTypeEnum.SAFE),
                threat_type=threat_type,
                severity=severity,
                confidence_score=confidence_score,
                remediation_steps=[payload.reason or "Reclassified by user"],
                analyzed_at=datetime.now(timezone.utc),
                explanation={"updated_by_user": payload.reason},
                model_version="manual"
            )
            db.add(threat_analysis)

        # Optionally, add a remediation log entry indicating the reclassification.
        remediation_log = RemediationLog(
            email_id=email.id,
            action_taken=f"Reclassified as {new_classification.capitalize()}",
            performed_by=f"User {current_user.id}",
        )
        db.add(remediation_log)

        db.commit()
        logger.info(f"Email {email_id} reclassified to {new_classification} by user {current_user.id}")

        # Build a response that reflects the updated threat analysis.
        updated_data = {
            "email_id": email.email_id,
            "new_classification": threat_analysis.threat_type.value,
            "severity": threat_analysis.severity.value if threat_analysis.severity else None,
            "updated_at": threat_analysis.analyzed_at.isoformat(),
            "reason": payload.reason
        }
        return create_response(
            status="success",
            msg="Email reclassified successfully.",
            data=updated_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reclassifying email {email_id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
