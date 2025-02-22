# app/api/v1/routes/email/__init__.py
from app.api.v1.routes.email.email_integration import email_integrations_router
from app.api.v1.routes.email.gmail.gmail_integration import gmail_integrations_router
from app.api.v1.routes.email.email_providers import email_providers_router
from app.api.v1.routes.email.gmail.gmail_notifications import gmail_notifications_router


__all__ = [
  "email_providers_router",
  "email_integrations_router",
  "gmail_integrations_router",
  "gmail_notifications_router"
  ]

