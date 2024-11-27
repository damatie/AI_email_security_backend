# Main Router - app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.routes.auth import register_individual_user_router,register_company_router,verify_email_router, resend_verification_router

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