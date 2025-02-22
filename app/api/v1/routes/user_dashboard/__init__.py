# app/api/v1/routes/user_dashboard/__init__.py
from app.api.v1.routes.user_dashboard.dashboard_overview.get_overview import get_overview_router
from app.api.v1.routes.user_dashboard.scanned_emails.get_emails import get_emails_router
from app.api.v1.routes.user_dashboard.scanned_emails.get_email_details import get_email_details_router
from app.api.v1.routes.user_dashboard.scanned_emails.email_reclassification import email_reclassification_router
from app.api.v1.routes.user_dashboard.scanned_emails.get_scan_history import get_sacn_history_router
from app.api.v1.routes.user_dashboard.user_profile.get_user_profile import get_user_profile_router
from app.api.v1.routes.user_dashboard.user_profile.update_user_profile import update_user_profile_router
from app.api.v1.routes.user_dashboard.user_profile.update_user_password import update_user_password_router
from app.api.v1.routes.user_dashboard.user_settings.get_notifications import get_notifications_router
from app.api.v1.routes.user_dashboard.user_settings.mark_notifications_read import update_notifications_router





__all__ = [
  "get_overview_router",
  "get_emails_router",
  "get_email_details_router",
  "email_reclassification_router",
  "get_user_profile_router",
  "update_user_profile_router",
  "update_user_password_router",
  "get_sacn_history_router",
  "get_notifications_router",
  "update_notifications_router"
  ]

