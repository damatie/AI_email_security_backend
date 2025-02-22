from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.deps import get_db
from app.schemas.user_dashboard.dashboard_overview.overview_schema import DashboardOverviewResponseSchema
from app.utils.get_current_user import get_current_user
from app.utils.response_helper import create_response
from app.models.emails.email import Email
from app.models.email_analysis.threat_analysis import ThreatAnalysis
from app.models.emails.fetch_email_log import FetchEmailLog
import logging

get_overview_router = APIRouter()
logger = logging.getLogger(__name__)

@get_overview_router.get("/", response_model=DashboardOverviewResponseSchema)
async def dashboard_overview(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Returns a high-level overview of the user's email security status.
    """
    try:
        # Total emails scanned
        total_emails = (
            db.query(func.count(func.distinct(Email.id)))
            .join(ThreatAnalysis, ThreatAnalysis.email_id == Email.id)
            .filter(Email.user_id == current_user.id)
            .scalar()
        )
        
        # Threat summary: Count threat analysis grouped by threat type
        threat_summary_query = (
            db.query(ThreatAnalysis.threat_type, func.count(ThreatAnalysis.id))
              .join(Email, ThreatAnalysis.email_id == Email.id)
              .filter(Email.user_id == current_user.id)
              .group_by(ThreatAnalysis.threat_type)
        )
        threat_summary = {}
        for threat_type, count in threat_summary_query.all():
            # Assume threat_type is an Enum and use its .value for clarity.
            threat_summary[threat_type.value] = count

        # Get the last scan timestamp from the FetchEmailLog.
        fetch_log = db.query(FetchEmailLog).filter(FetchEmailLog.user_id == current_user.id).first()
        last_scan_at = fetch_log.last_fetched_at.isoformat() if fetch_log else None

        overview_data = {
            "total_emails_scanned": total_emails,
            "threat_summary": threat_summary,
            "last_scan_at": last_scan_at,
            "next_scheduled_scan": None      # Omit if the system is fully event-driven.
        }
        return create_response(
            status="success",
            msg="Dashboard overview retrieved successfully.",
            data=overview_data
        )
    except Exception as e:
        logger.error(f"Error in dashboard overview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))