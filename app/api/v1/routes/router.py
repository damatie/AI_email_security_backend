# Main Router - app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.routes.auth import register_individual_user_router,register_company_router,verify_email_router, resend_verification_router,login_router,login_2fa_router,individual_user_onboarding_router
from app.api.v1.routes.email import email_providers_router,email_integrations_router,gmail_integrations_router
router = APIRouter()

# Auth routes


router.include_router(
    login_router,
    prefix="/auth/individual/login",
    tags=["Authentication - Individual User"]
)

router.include_router(
    login_2fa_router,
    prefix="/auth/individual/login-2fa",
    tags=["Authentication - Individual User"]
)

router.include_router(
    register_individual_user_router,
    prefix="/auth/individual/register",
    tags=["Authentication - Individual User"]
)

router.include_router(
    verify_email_router,
    prefix="/auth/email/verify",
    tags=["Authentication - Email Verification"]
)

router.include_router(
    resend_verification_router,
    prefix="/auth/email/resend-verification",
    tags=["Authentication - Email Verification"]
)


# Email Integrations
router.include_router(
    email_integrations_router,
    prefix="/email/integration",
    tags=["Email Integrations"]
)

router.include_router(
    gmail_integrations_router,
    prefix="/email/integration/gmail",
    tags=["Gmail Integration"]
)

# Onboarding (For Individual Users)
router.include_router(
    individual_user_onboarding_router,
    prefix="/individual/onboarding",
    tags=["Onboarding - Individual User"]
)

# Managed by System Super Admin
router.include_router(
    email_providers_router,
    prefix="/system/email/providers",
    tags=["System Management - Email Providers"]
)


router.include_router(
    register_company_router,
    prefix="/auth/register_company",
    tags=["Company/Business - Authentication"]
)