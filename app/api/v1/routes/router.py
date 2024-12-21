# Main Router - app/api/v1/router.py
from fastapi import APIRouter, Depends
from app.api.v1.routes.auth import register_individual_user_router,register_company_router,verify_email_router, resend_verification_router,login_router,login_2fa_router,individual_user_onboarding_router

router = APIRouter()

# Auth routes
router.include_router(
    register_individual_user_router,
    prefix="/auth/individual/register",
    tags=["Individual User - Authentication"]
)

router.include_router(
    register_company_router,
    prefix="/auth/register_company",
    tags=["Company/Business - Authentication"]
)

router.include_router(
    verify_email_router,
    prefix="/auth",
    tags=["Email Verification - Authentication"]
)

router.include_router(
    resend_verification_router,
    prefix="/auth",
    tags=["Resend Email Verification - Authentication"]
)

router.include_router(
    login_router,
    prefix="/auth/login",
    tags=["Login - Authentication"]
)

router.include_router(
    login_2fa_router,
    prefix="/auth/login-2fa",
    tags=["Login - Authentication"]
)

router.include_router(
    individual_user_onboarding_router,
    prefix="/individual_user",
    tags=["Individual User - Onboarding"]
)