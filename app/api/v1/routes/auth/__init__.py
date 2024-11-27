# app/api/v1/routes/auth/__init__.py
from app.api.v1.routes.auth.individual_user.register import router as register_individual_user_router
from app.api.v1.routes.auth.company_business.register import router as register_company_router
from app.api.v1.routes.auth.verify_email import router as verify_email_router
from app.api.v1.routes.auth.resend_verification import router as resend_verification_router


__all__ = [
  "register_individual_user_router",
  "register_company_router",
  "verify_email_router",
  "resend_verification_router"
  
  ]