# app/routes/emails.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.deps import get_db
from app.utils.get_current_user import get_current_user
from app.utils.response_helper import create_response
from app.models.emails.email import Email
import logging
import math
import email.utils  # For parsing email addresses
from datetime import datetime
from typing import Optional

# Import your enums
from app.utils.enums import ThreatTypeEnum, ThreatSeverityEnum

# Import the ThreatAnalysis model (adjust the path if needed)
from app.models.email_analysis.threat_analysis import ThreatAnalysis

from app.schemas.user_dashboard.scanned_emails.get_emails_schema import (
    EmailListResponseSchema,
    EmailListDataSchema,
    EmailItemSchema
)

get_emails_router = APIRouter()
logger = logging.getLogger(__name__)

@get_emails_router.get(
    "/emails",
    response_model=EmailListResponseSchema,
    summary="Retrieve paginated scanned emails",
    description=(
        "Retrieves a paginated list of scanned emails for the current user with optional filtering. "
        "Supports filtering by threat type (using ThreatTypeEnum), subject keyword, sender email, "
        "and a date range."
    )
)
async def list_emails(
    page: int = Query(1, ge=1, description="Page number (must be >= 1)"),
    limit: int = Query(50, ge=1, le=100, description="Number of emails per page (max 100)"),
    threat_type: Optional[ThreatTypeEnum] = Query(
        None,
        description=(
            "Filter by threat type. Allowed values: PHISHING, SPAM, MALWARE, MALICIOUS, "
            "SUSPICIOUS, SAFE, BEC, IMPERSONATION"
        )
    ),
    subject: Optional[str] = Query(None, description="Filter emails by subject keyword"),
    sender: Optional[str] = Query(None, description="Filter emails by sender email address"),
    start_date: Optional[datetime] = Query(
        None, description="Return emails received after this date (ISO 8601 format)"
    ),
    end_date: Optional[datetime] = Query(
        None, description="Return emails received before this date (ISO 8601 format)"
    ),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        # Build a base query ensuring emails belong to the current user
        query = db.query(Email).filter(Email.user_id == current_user.id)
        
        # Apply threat_type filtering if specified.
        # Use the ThreatAnalysis model to access the column attribute.
        if threat_type:
            query = query.filter(
                Email.threat_analysis.has(ThreatAnalysis.threat_type == threat_type)
            )
        
        # Filter by subject (case-insensitive)
        if subject:
            query = query.filter(Email.subject.ilike(f"%{subject}%"))
        
        # Filter by sender (case-insensitive)
        if sender:
            query = query.filter(Email.sender.ilike(f"%{sender}%"))
        
        # Filter by received_at date range
        if start_date:
            query = query.filter(Email.received_at >= start_date)
        if end_date:
            query = query.filter(Email.received_at <= end_date)
        
        # Retrieve total count for pagination
        total_count = query.with_entities(func.count(Email.id)).scalar()
        offset = (page - 1) * limit
        
        # Fetch the emails for the requested page
        emails = (
            query.order_by(Email.received_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        email_items = []
        for email_obj in emails:
            # Parse the sender field to extract the display name and the email address.
            display_name, email_address = email.utils.parseaddr(email_obj.sender)
            
            # Get threat_type from threat_analysis, defaulting to SAFE if not available.
            t_type = (
                email_obj.threat_analysis.threat_type.value
                if email_obj.threat_analysis and email_obj.threat_analysis.threat_type
                else ThreatTypeEnum.SAFE.value
            )
            # Get threat_severity from threat_analysis, defaulting to NONE if not available.
            t_severity = (
                email_obj.threat_analysis.severity.value
                if email_obj.threat_analysis and hasattr(email_obj.threat_analysis, "severity") and email_obj.threat_analysis.severity
                else ThreatSeverityEnum.NONE.value
            )
            
            email_items.append(
                EmailItemSchema(
                    email_id=email_obj.email_id,
                    subject=email_obj.subject,
                    sender=email_address,  # Only the parsed email address is returned.
                    sender_name=display_name if display_name else None,
                    recipient=email_obj.recipient,
                    received_at=email_obj.received_at,
                    processed_at=email_obj.processed_at,
                    threat_type=t_type,
                    threat_severity=t_severity
                )
            )
        
        total_pages = math.ceil(total_count / limit) if limit else 1
        
        data_payload = EmailListDataSchema(
            emails=email_items,
            total=total_count,
            limit=limit,
            page=page,
            total_pages=total_pages
        )
        
        return create_response(
            status="success",
            msg="Scanned email list retrieved successfully.",
            data=data_payload.dict()
        )
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error("Error retrieving scanned email list: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving emails."
        )