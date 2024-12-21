# app/api/v1/routes/auth/__init__.py
from app.api.v1.routes.auth.individual_user.register import register_individual_user_router
from app.api.v1.routes.auth.company_business.register import register_company_router
from app.api.v1.routes.auth.verify_email import verify_email_router
from app.api.v1.routes.auth.resend_verification import resend_verification_router
from app.api.v1.routes.auth.login import login_router
from app.api.v1.routes.auth.login_2fa import login_2fa_router
from app.api.v1.routes.auth.individual_user.onboarding import onboarding_router as individual_user_onboarding_router

__all__ = [
  "register_individual_user_router",
  "register_company_router",
  "verify_email_router",
  "resend_verification_router",
  "login_router",
  "login_2fa_router",
  "individual_user_onboarding_router"
  ]