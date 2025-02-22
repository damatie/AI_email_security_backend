# Scan History Endpoint

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models.emails.fetch_email_log import FetchEmailLog
from app.schemas.user_dashboard.scanned_emails.scan_history_schema import ScanHistoryResponseSchema
from app.utils.get_current_user import get_current_user
from app.utils.response_helper import create_response
import logging

get_sacn_history_router = APIRouter()
logger = logging.getLogger(__name__)

@get_sacn_history_router.get(
        "/scan-history",
        response_model=ScanHistoryResponseSchema
        )
async def scan_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Returns the scan history (the latest fetch log) for the current user.
    """
    try:
        fetch_log = db.query(FetchEmailLog).filter(FetchEmailLog.user_id == current_user.id).first()
        if not fetch_log:
            history_data = []
        else:
            history_data = [{
                "timestamp": fetch_log.last_fetched_at.isoformat(),
                "history_id": fetch_log.history_id,
                "initial_scan_completed": fetch_log.initial_scan_completed
            }]
        return create_response(
            status="success",
            msg="Scan history retrieved successfully.",
            data={"scan_history": history_data}
        )
    except Exception as e:
        logger.error(f"Error retrieving scan history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
