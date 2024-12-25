# Main Router - app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.routes.auth import register_individual_user_router,register_company_router,verify_email_router, resend_verification_router,login_router,login_2fa_router,individual_user_onboarding_router;
from app.api.v1.routes.email.email_providers import email_providers_router

router = APIRouter()

# Auth routes
router.include_router(
    register_individual_user_router,
    prefix="/auth/individual/register",
    tags=["Individual User - Authentication"]
)



router.include_router(
    verify_email_router,
    prefix="/auth",
    tags=["Email Verification - Authentication"]
)

router.include_router(
    resend_verification_router,
    prefix="/auth",
    tags=["Email Verification - Authentication"]
)

router.include_router(
    login_router,
    prefix="/auth/login",
    tags=["Individual User - Authentication"]
)

router.include_router(
    login_2fa_router,
    prefix="/auth/login-2fa",
     tags=["Individual User - Authentication"]
)

router.include_router(
    individual_user_onboarding_router,
    prefix="/individual_user",
    tags=["Individual User - Onboarding (To be reviewed)"]
)

router.include_router(
    email_providers_router,
    prefix="/email/providers",
    tags=["Email Providers"]
)

router.include_router(
    register_company_router,
    prefix="/auth/register_company",
    tags=["Company/Business - Authentication"]
)